import hashlib
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

import feedparser
import httpx
import yaml
from dateutil import parser as date_parser
from redis import Redis
from rq import Queue

from app.config import get_settings
from app.database import get_db_context
from app.models import Source, SourceType, Item, ItemType, FundingDetails, CompanyDetails, IngestRun, IngestStatus

logger = logging.getLogger(__name__)
settings = get_settings()


def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url)


def get_queue() -> Queue:
    return Queue(connection=get_redis())


def create_item_hash(url: str, title: str, published_at: Optional[datetime]) -> str:
    """Create a stable hash for deduplication."""
    # Normalize URL
    parsed = urlparse(url)
    normalized_url = f"{parsed.netloc}{parsed.path}".lower().strip("/")
    
    # Normalize title
    normalized_title = title.lower().strip()
    
    # Include date if available
    date_str = published_at.isoformat() if published_at else ""
    
    content = f"{normalized_url}|{normalized_title}|{date_str}"
    return hashlib.sha256(content.encode()).hexdigest()


def parse_rss_feed(url: str) -> List[Dict[str, Any]]:
    """Parse an RSS feed and return items."""
    try:
        feed = feedparser.parse(url)
        items = []
        
        for entry in feed.entries:
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except:
                    pass
            elif hasattr(entry, 'published'):
                try:
                    published_at = date_parser.parse(entry.published)
                except:
                    pass
            
            # Get summary
            summary = ""
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            
            # Clean HTML from summary (basic)
            import re
            summary = re.sub(r'<[^>]+>', '', summary)[:500]
            
            items.append({
                'title': entry.get('title', 'Untitled'),
                'url': entry.get('link', ''),
                'published_at': published_at,
                'summary': summary,
                'raw': dict(entry),
            })
        
        return items
    except Exception as e:
        logger.error(f"Error parsing RSS feed {url}: {e}")
        return []


def determine_item_type(title: str, summary: str, category: Optional[str]) -> ItemType:
    """Determine if an item is about funding or a company."""
    title_lower = title.lower()
    summary_lower = summary.lower()
    
    funding_keywords = [
        'raise', 'raised', 'funding', 'series', 'seed', 'investment',
        'million', 'billion', '$', 'valuation', 'round', 'venture',
        'backed', 'investor', 'capital', 'led by'
    ]
    
    for keyword in funding_keywords:
        if keyword in title_lower or keyword in summary_lower:
            return ItemType.FUNDING
    
    if category and 'funding' in category.lower():
        return ItemType.FUNDING
    
    return ItemType.COMPANY


def extract_company_name(title: str) -> Optional[str]:
    """Extract company name from title (heuristic)."""
    # Common patterns: "Company raises $X", "Company announces", etc.
    import re
    
    # Try to find company name before common verbs
    patterns = [
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:\s+raises?\s)',
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:\s+announces?\s)',
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:\s+secures?\s)',
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:\s+closes?\s)',
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:\s+gets?\s)',
        r'^([A-Z][A-Za-z0-9\s\.]+?)(?:,\s)',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, title)
        if match:
            return match.group(1).strip()
    
    # Fallback: first few words
    words = title.split()
    if len(words) >= 2:
        # Take words until we hit a common verb or punctuation
        company_words = []
        for word in words[:5]:
            if word.lower() in ['raises', 'announces', 'secures', 'closes', 'gets', 'lands', '-', '–', '|']:
                break
            company_words.append(word)
        if company_words:
            return ' '.join(company_words)
    
    return None


def extract_funding_details(title: str, summary: str) -> Dict[str, Any]:
    """Extract funding details from title and summary."""
    import re
    
    details = {
        'round_type': None,
        'amount_usd': None,
        'investors': [],
    }
    
    text = f"{title} {summary}".lower()
    
    # Extract round type
    round_patterns = [
        (r'series\s+([a-z])', lambda m: f"series_{m.group(1)}"),
        (r'seed\s+round', lambda m: 'seed'),
        (r'pre-seed', lambda m: 'pre_seed'),
        (r'seed', lambda m: 'seed'),
        (r'series\s+([a-z])\d?', lambda m: f"series_{m.group(1)}"),
        (r'growth\s+round', lambda m: 'growth'),
        (r'bridge\s+round', lambda m: 'bridge'),
    ]
    
    for pattern, extractor in round_patterns:
        match = re.search(pattern, text)
        if match:
            details['round_type'] = extractor(match)
            break
    
    # Extract amount
    amount_patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(?:million|m\b)',
        r'\$(\d+(?:\.\d+)?)\s*(?:billion|b\b)',
        r'(\d+(?:\.\d+)?)\s*(?:million|m)\s*(?:dollars|\$)',
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            amount = float(match.group(1))
            if 'billion' in text[match.start():match.end()+10].lower() or 'b' in text[match.start():match.end()+3].lower():
                amount *= 1000
            details['amount_usd'] = amount * 1_000_000
            break
    
    return details


def ingest_source(source_id: int) -> Dict[str, Any]:
    """Ingest items from a single source."""
    with get_db_context() as db:
        source = db.query(Source).filter(Source.id == source_id).first()
        if not source or not source.enabled:
            return {'status': 'skipped', 'reason': 'Source not found or disabled'}
        
        # Create ingest run
        run = IngestRun(source_id=source_id)
        db.add(run)
        db.commit()
        
        try:
            items_added = 0
            
            if source.type.value == 'rss':
                parsed_items = parse_rss_feed(source.url)
                
                for item_data in parsed_items:
                    if not item_data.get('url'):
                        continue
                    
                    # Create hash for dedup
                    hash_value = create_item_hash(
                        url=item_data['url'],
                        title=item_data['title'],
                        published_at=item_data['published_at'],
                    )
                    
                    # Check if already exists
                    existing = db.query(Item).filter(Item.hash == hash_value).first()
                    if existing:
                        continue
                    
                    # Determine type
                    item_type = determine_item_type(
                        item_data['title'],
                        item_data.get('summary', ''),
                        source.category,
                    )
                    
                    # Extract company name
                    company_name = extract_company_name(item_data['title'])
                    
                    # Create item
                    item = Item(
                        type=item_type,
                        title=item_data['title'],
                        company_name=company_name,
                        url=item_data['url'],
                        source_id=source.id,
                        published_at=item_data['published_at'],
                        summary=item_data.get('summary'),
                        raw_json=item_data.get('raw'),
                        hash=hash_value,
                    )
                    db.add(item)
                    db.flush()
                    
                    # Add details based on type
                    if item_type == ItemType.FUNDING:
                        funding = extract_funding_details(item_data['title'], item_data.get('summary', ''))
                        funding_details = FundingDetails(
                            item_id=item.id,
                            round_type=funding.get('round_type'),
                            amount_usd=funding.get('amount_usd'),
                            investors=funding.get('investors'),
                        )
                        db.add(funding_details)
                    else:
                        company_details = CompanyDetails(
                            item_id=item.id,
                            one_liner=item_data.get('summary', '')[:200] if item_data.get('summary') else None,
                        )
                        db.add(company_details)
                    
                    items_added += 1
                    
                    # Enqueue analysis job
                    from app.services.analysis import enqueue_analysis
                    enqueue_analysis(item.id)
            
            db.commit()
            
            # Update run status
            run.finished_at = datetime.utcnow()
            run.status = IngestStatus.SUCCESS
            run.items_added = items_added
            db.commit()
            
            return {'status': 'success', 'items_added': items_added}
            
        except Exception as e:
            logger.exception(f"Error ingesting source {source_id}")
            run.finished_at = datetime.utcnow()
            run.status = IngestStatus.FAILED
            run.error = str(e)
            db.commit()
            return {'status': 'failed', 'error': str(e)}


def ingest_all_sources() -> Dict[str, Any]:
    """Ingest items from all enabled sources."""
    with get_db_context() as db:
        sources = db.query(Source).filter(Source.enabled == True).all()
        source_ids = [s.id for s in sources]
    
    results = {}
    for source_id in source_ids:
        results[source_id] = ingest_source(source_id)
    
    return results


def trigger_ingestion(source_id: Optional[int] = None) -> str:
    """Trigger ingestion job."""
    queue = get_queue()
    
    if source_id:
        job = queue.enqueue(ingest_source, source_id)
    else:
        job = queue.enqueue(ingest_all_sources)
    
    return job.id


def load_sources_from_yaml() -> None:
    """Load sources from YAML configuration file."""
    import os
    yaml_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sources.yaml')
    
    if not os.path.exists(yaml_path):
        logger.warning(f"Sources YAML not found at {yaml_path}")
        return
    
    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if not config or 'sources' not in config:
        return
    
    with get_db_context() as db:
        for source_data in config['sources']:
            # Check if source exists
            existing = db.query(Source).filter(Source.url == source_data['url']).first()
            if existing:
                continue
            
            # Convert string to SourceType enum
            type_str = source_data.get('type', 'rss').lower()
            source_type = SourceType(type_str)
            
            source = Source(
                name=source_data['name'],
                type=source_type,
                url=source_data['url'],
                category=source_data.get('category'),
                enabled=source_data.get('enabled', True),
            )
            db.add(source)
        
        db.commit()

