#!/usr/bin/env python3
"""
Fetch yesterday's AI startup funding news from RSS feeds.
Uses LLM-based classification to accurately detect fundraising events.
Optionally runs MENA market analysis on each article.
"""

import feedparser
from datetime import datetime, timedelta
from dateutil import parser as date_parser
import re
import os
import json
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any

# Load .env file if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on environment variables

# Try to import OpenAI - optional dependency
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Note: OpenAI not installed. Using keyword-based detection.")
    print("Install with: pip install openai\n")

# Try to import requests and BeautifulSoup for web scraping
try:
    import requests
    from bs4 import BeautifulSoup
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False


# RSS feeds focused on AI/startup funding
FEEDS = [
    # Major Tech News
    ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
    ("TechCrunch Startups", "https://techcrunch.com/category/startups/feed/"),
    ("TechCrunch Venture", "https://techcrunch.com/category/venture/feed/"),
    ("VentureBeat AI", "https://venturebeat.com/category/ai/feed/"),
    ("VentureBeat Business", "https://venturebeat.com/category/business/feed/"),
    ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
    ("Ars Technica AI", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
    ("Wired Business", "https://www.wired.com/feed/category/business/latest/rss"),
    
    # Startup & VC Focused
    ("Crunchbase News", "https://news.crunchbase.com/feed/"),
    ("SiliconANGLE", "https://siliconangle.com/feed/"),
    ("PitchBook News", "https://pitchbook.com/news/rss"),
    ("Fortune Venture", "https://fortune.com/feed/fortune-feeds/?id=3230629"),
    
    # AI Specific
    ("AI News", "https://www.artificialintelligence-news.com/feed/"),
    ("MIT Tech Review AI", "https://www.technologyreview.com/topic/artificial-intelligence/feed"),
    ("The AI Beat", "https://venturebeat.com/category/ai/feed/"),
    
    # MENA Region
    ("Wamda", "https://www.wamda.com/feed"),
    ("Magnitt", "https://magnitt.com/feed"),
    ("Arabian Business", "https://www.arabianbusiness.com/rss"),
    
    # General Business/Finance
    ("Reuters Tech", "https://www.reutersagency.com/feed/?best-topics=tech"),
    ("Bloomberg Tech", "https://feeds.bloomberg.com/technology/news.rss"),
]

# Keywords that indicate funding news (fallback when LLM not available)
FUNDING_KEYWORDS = [
    "raises", "raised", "funding", "series a", "series b", "series c", "series d",
    "seed", "investment", "million", "billion", "valuation", "venture", "backed",
    "investor", "capital", "round", "financing", "secures", "closes"
]

# Keywords that indicate NOT a fundraising event (for filtering)
NEGATIVE_KEYWORDS = [
    "opinion", "editorial", "how to", "guide", "tutorial", "review", 
    "what is", "explainer", "analysis:", "podcast", "interview"
]


@dataclass
class FundingClassification:
    """Result of LLM-based funding classification."""
    is_fundraising: bool
    confidence: float  # 0.0 to 1.0
    company_name: Optional[str] = None
    amount: Optional[str] = None
    round_type: Optional[str] = None
    reasoning: Optional[str] = None


@dataclass
class MENAAnalysis:
    """Result of MENA market analysis."""
    # 1. Summary
    innovation_summary: str
    innovation_type: str  # LLM, CV, SaaS, infrastructure, etc.
    
    # 2. Problem-Solution Fit
    problem_solution_fit: str
    target_sectors: List[str]
    vision_2030_alignment: str
    
    # 3. Localizability Scorecard
    arabic_complexity: str  # Low/Medium/High
    arabic_complexity_notes: str
    regulatory_fit: str  # Low/Medium/High
    regulatory_fit_notes: str
    market_readiness: str  # Low/Medium/High
    market_readiness_notes: str
    infrastructure_fit: str  # Low/Medium/High
    infrastructure_fit_notes: str
    
    # 4. Commercial Buyer Map
    potential_buyers: List[str]
    sales_motion: str
    
    # 5. Opportunity Rating
    commercialization_potential: str  # High/Medium/Low
    localization_requirement: str  # Minor/Moderate/Major
    priority: str  # Worth prototyping / Keep tracking / Ignore
    
    # 6. Justification
    justification: str


# MENA Analysis Prompt
MENA_ANALYSIS_PROMPT = """You are a venture analyst assessing the commercial potential of global AI developments in the MENA region — with a focus on UAE and Saudi Arabia. Your goal is to identify which AI innovations from today's news are viable for localization and commercialization, especially for B2B enterprise or government markets.

Analyze this article through the lens of UAE/Saudi-specific economic, regulatory, and cultural contexts. Prioritize actionable insights to help two Dubai-based co-founders with $5M+ and deep AI expertise (LLMs, CV) decide what to pursue or adapt.

ARTICLE TITLE: {title}

ARTICLE CONTENT:
{content}

Provide your analysis as a JSON object with the following structure:
{{
    "innovation_summary": "What is the AI product or breakthrough? 2-3 sentences.",
    "innovation_type": "LLM/CV/SaaS/Infrastructure/Enterprise/Other",
    "problem_solution_fit": "How well does this solve a known pain in MENA? 2-3 sentences focusing on UAE/KSA sectors.",
    "target_sectors": ["list", "of", "relevant", "sectors"],
    "vision_2030_alignment": "How does this tie to Vision 2030 goals or digital transformation? 1-2 sentences.",
    "arabic_complexity": "Low/Medium/High",
    "arabic_complexity_notes": "Brief explanation of Arabic/multilingual adaptation needs",
    "regulatory_fit": "Low/Medium/High",
    "regulatory_fit_notes": "Will data sovereignty, government oversight help or hinder?",
    "market_readiness": "Low/Medium/High", 
    "market_readiness_notes": "Are UAE/KSA enterprises mature enough to adopt this?",
    "infrastructure_fit": "Low/Medium/High",
    "infrastructure_fit_notes": "Compatibility with local cloud, APIs, secure networks",
    "potential_buyers": ["Government ministry", "SOE like Aramco/DEWA", "Bank", "Telco", "etc"],
    "sales_motion": "Direct B2G / Channel partner / POC-first / etc",
    "commercialization_potential": "High/Medium/Low",
    "localization_requirement": "Minor/Moderate/Major",
    "priority": "Worth prototyping/Keep tracking/Ignore for now",
    "justification": "2-4 sentences: Why is this interesting or not? What makes it viable or risky in UAE/KSA? Could it be basis for pilot, verticalized SaaS, or infra/API?"
}}

Respond with ONLY the JSON object, no other text."""


# LLM Classification prompt - using double braces to escape JSON example
CLASSIFICATION_PROMPT = """You are a financial news classifier. Analyze the following news headline and summary to determine if it's about a STARTUP FUNDRAISING EVENT.

A fundraising event includes:
- Seed rounds, Series A/B/C/D rounds
- Venture capital investments
- Private equity investments in startups
- Growth funding rounds

NOT a fundraising event:
- General company news or product launches
- Acquisitions or mergers (unless it mentions fundraising too)
- IPOs (these are exits, not fundraises)
- Government grants or subsidies
- Layoffs or company shutdowns
- Opinion pieces or analysis articles
- How-to guides or tutorials

Respond with a JSON object:
{{
    "is_fundraising": true/false,
    "confidence": 0.0-1.0,
    "company_name": "extracted company name or null",
    "amount": "funding amount like '$50M' or null",
    "round_type": "Seed/Series A/Series B/etc or null",
    "reasoning": "brief 1-sentence explanation"
}}

NEWS HEADLINE: {title}

NEWS SUMMARY: {summary}

JSON Response:"""


def classify_with_llm(title: str, summary: str, client: "OpenAI", verbose: bool = False, debug: bool = False) -> FundingClassification:
    """Use LLM to classify if news is about a fundraising event."""
    content = ""  # Initialize for error handling
    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        if debug:
            print(f"\n      DEBUG: Calling API for '{title[:40]}...'")
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise financial news classifier. Respond ONLY with a compact JSON object on a single line, no other text."
                },
                {
                    "role": "user", 
                    "content": CLASSIFICATION_PROMPT.format(title=title, summary=summary[:500])
                }
            ],
            temperature=0.0,
            max_tokens=300
        )
        
        if debug:
            print(f"      DEBUG: Got API response")
        
        content = response.choices[0].message.content
        if content:
            content = content.strip()
        else:
            content = "{}"
        
        if debug:
            print(f"      DEBUG raw response: {repr(content[:200])}")
        
        # Clean up the response - remove markdown code blocks
        if "```" in content:
            parts = content.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    content = part
                    break
        
        # Find the JSON object in the response
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        if start_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx]
        
        if debug:
            print(f"      DEBUG cleaned JSON: {repr(content[:200])}")
        
        data = json.loads(content)
        
        if debug:
            print(f"      DEBUG parsed data keys: {list(data.keys())}")
        
        # Handle both snake_case and possible variations
        is_fund = data.get("is_fundraising", data.get("is_fundraising_event", data.get("fundraising", False)))
        conf = data.get("confidence", 0.5)
        
        result = FundingClassification(
            is_fundraising=bool(is_fund),
            confidence=float(conf) if conf else 0.5,
            company_name=data.get("company_name"),
            amount=data.get("amount"),
            round_type=data.get("round_type"),
            reasoning=data.get("reasoning")
        )
        
        if verbose:
            status = "✓" if result.is_fundraising else "✗"
            print(f"      {status} [{result.confidence:.0%}] {title[:50]}...")
        
        return result
        
    except json.JSONDecodeError as e:
        if verbose or debug:
            print(f"      ⚠ JSON parse error for '{title[:30]}...': {e}")
            print(f"         Content: {repr(content[:100] if content else 'empty')}")
        return classify_with_keywords(title, summary)
    except Exception as e:
        if verbose or debug:
            print(f"      ⚠ LLM error for '{title[:30]}...': {type(e).__name__}: {e}")
            import traceback
            if debug:
                traceback.print_exc()
        return classify_with_keywords(title, summary)


def classify_with_keywords(title: str, summary: str) -> FundingClassification:
    """Fallback keyword-based classification."""
    text = f"{title} {summary}".lower()
    
    # Check for negative keywords first
    if any(neg in text for neg in NEGATIVE_KEYWORDS):
        return FundingClassification(
            is_fundraising=False,
            confidence=0.6,
            reasoning="Contains editorial/opinion indicators"
        )
    
    # Check for funding keywords
    funding_matches = sum(1 for kw in FUNDING_KEYWORDS if kw in text)
    
    if funding_matches >= 2:
        # Extract amount if present
        amount = extract_amount(text)
        return FundingClassification(
            is_fundraising=True,
            confidence=min(0.5 + (funding_matches * 0.1), 0.9),
            amount=amount,
            reasoning=f"Matched {funding_matches} funding keywords"
        )
    elif funding_matches == 1:
        return FundingClassification(
            is_fundraising=True,
            confidence=0.4,
            reasoning="Matched 1 funding keyword - low confidence"
        )
    
    return FundingClassification(
        is_fundraising=False,
        confidence=0.7,
        reasoning="No funding keywords found"
    )


def is_funding_related(title: str, summary: str) -> bool:
    """Check if article is about funding (keyword-based fallback)."""
    text = f"{title} {summary}".lower()
    return any(keyword in text for keyword in FUNDING_KEYWORDS)


def extract_amount(text: str) -> str | None:
    """Extract funding amount from text."""
    patterns = [
        r'\$(\d+(?:\.\d+)?)\s*(?:million|m\b)',
        r'\$(\d+(?:\.\d+)?)\s*(?:billion|b\b)',
        r'(\d+(?:\.\d+)?)\s*million',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            amount = match.group(1)
            if 'billion' in text.lower():
                return f"${amount}B"
            return f"${amount}M"
    return None


def clean_html(text: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r'<[^>]+>', '', text).strip()


def fetch_article_content(url: str, timeout: int = 10) -> Optional[str]:
    """Fetch and extract main content from an article URL."""
    if not SCRAPING_AVAILABLE:
        return None
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
            element.decompose()
        
        # Try to find article content using common selectors
        content = None
        selectors = [
            'article',
            '[role="main"]',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.story-body',
            '.article-body',
            'main',
            '.content'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                content = element.get_text(separator='\n', strip=True)
                break
        
        # Fallback to body if no article container found
        if not content:
            body = soup.find('body')
            if body:
                content = body.get_text(separator='\n', strip=True)
        
        if content:
            # Clean up whitespace
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            content = '\n'.join(lines)
            # Truncate to reasonable length for LLM
            return content[:8000]
        
        return None
        
    except Exception as e:
        return None


def run_mena_analysis(title: str, content: str, client: "OpenAI", verbose: bool = True) -> Optional[MENAAnalysis]:
    """Run MENA market analysis on an article using LLM."""
    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        # Use summary if content is too short
        if not content or len(content) < 100:
            return None
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a venture analyst specializing in MENA markets. Respond only with valid JSON."
                },
                {
                    "role": "user",
                    "content": MENA_ANALYSIS_PROMPT.format(title=title, content=content[:6000])
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        response_content = response.choices[0].message.content.strip()
        
        # Clean up JSON
        if "```" in response_content:
            parts = response_content.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{"):
                    response_content = part
                    break
        
        start_idx = response_content.find("{")
        end_idx = response_content.rfind("}") + 1
        if start_idx != -1 and end_idx > start_idx:
            response_content = response_content[start_idx:end_idx]
        
        data = json.loads(response_content)
        
        return MENAAnalysis(
            innovation_summary=data.get("innovation_summary", ""),
            innovation_type=data.get("innovation_type", "Unknown"),
            problem_solution_fit=data.get("problem_solution_fit", ""),
            target_sectors=data.get("target_sectors", []),
            vision_2030_alignment=data.get("vision_2030_alignment", ""),
            arabic_complexity=data.get("arabic_complexity", "Unknown"),
            arabic_complexity_notes=data.get("arabic_complexity_notes", ""),
            regulatory_fit=data.get("regulatory_fit", "Unknown"),
            regulatory_fit_notes=data.get("regulatory_fit_notes", ""),
            market_readiness=data.get("market_readiness", "Unknown"),
            market_readiness_notes=data.get("market_readiness_notes", ""),
            infrastructure_fit=data.get("infrastructure_fit", "Unknown"),
            infrastructure_fit_notes=data.get("infrastructure_fit_notes", ""),
            potential_buyers=data.get("potential_buyers", []),
            sales_motion=data.get("sales_motion", ""),
            commercialization_potential=data.get("commercialization_potential", "Unknown"),
            localization_requirement=data.get("localization_requirement", "Unknown"),
            priority=data.get("priority", "Unknown"),
            justification=data.get("justification", "")
        )
        
    except Exception as e:
        if verbose:
            print(f"      ⚠ MENA analysis error: {e}")
        return None


def print_mena_analysis(item: Dict[str, Any], analysis: MENAAnalysis, index: int):
    """Pretty print the MENA analysis for an article."""
    print(f"\n{'='*80}")
    print(f"📊 MENA ANALYSIS #{index}: {item['title'][:60]}...")
    print(f"{'='*80}")
    
    # Company & Funding Info
    print(f"\n🏢 Company: {item.get('company', 'Unknown')}")
    print(f"💰 Funding: {item.get('amount', 'Unknown')} ({item.get('round_type', 'Unknown')})")
    print(f"🔗 {item['link']}")
    
    # 1. Innovation Summary
    print(f"\n📌 INNOVATION SUMMARY")
    print(f"   Type: {analysis.innovation_type}")
    print(f"   {analysis.innovation_summary}")
    
    # 2. Problem-Solution Fit
    print(f"\n🎯 PROBLEM-SOLUTION FIT IN MENA")
    print(f"   {analysis.problem_solution_fit}")
    print(f"   Target Sectors: {', '.join(analysis.target_sectors)}")
    print(f"   Vision 2030: {analysis.vision_2030_alignment}")
    
    # 3. Localizability Scorecard
    print(f"\n📋 LOCALIZABILITY SCORECARD")
    print(f"   ┌─────────────────────┬────────┬─────────────────────────────────────┐")
    print(f"   │ Factor              │ Rating │ Notes                               │")
    print(f"   ├─────────────────────┼────────┼─────────────────────────────────────┤")
    print(f"   │ Arabic Complexity   │ {analysis.arabic_complexity:6} │ {analysis.arabic_complexity_notes[:35]:35} │")
    print(f"   │ Regulatory Fit      │ {analysis.regulatory_fit:6} │ {analysis.regulatory_fit_notes[:35]:35} │")
    print(f"   │ Market Readiness    │ {analysis.market_readiness:6} │ {analysis.market_readiness_notes[:35]:35} │")
    print(f"   │ Infrastructure Fit  │ {analysis.infrastructure_fit:6} │ {analysis.infrastructure_fit_notes[:35]:35} │")
    print(f"   └─────────────────────┴────────┴─────────────────────────────────────┘")
    
    # 4. Commercial Buyer Map
    print(f"\n🛒 COMMERCIAL BUYER MAP")
    print(f"   Potential Buyers: {', '.join(analysis.potential_buyers)}")
    print(f"   Sales Motion: {analysis.sales_motion}")
    
    # 5. Opportunity Rating
    print(f"\n⭐ OPPORTUNITY RATING")
    comm_emoji = "🟢" if analysis.commercialization_potential == "High" else "🟡" if analysis.commercialization_potential == "Medium" else "🔴"
    loc_emoji = "🟢" if analysis.localization_requirement == "Minor" else "🟡" if analysis.localization_requirement == "Moderate" else "🔴"
    pri_emoji = "🚀" if "prototyping" in analysis.priority.lower() else "👀" if "tracking" in analysis.priority.lower() else "⏸️"
    
    print(f"   {comm_emoji} Commercialization Potential: {analysis.commercialization_potential}")
    print(f"   {loc_emoji} Localization Requirement: {analysis.localization_requirement}")
    print(f"   {pri_emoji} Priority: {analysis.priority}")
    
    # 6. Justification
    print(f"\n💡 JUSTIFICATION")
    print(f"   {analysis.justification}")


def fetch_yesterdays_funding_news(use_llm: bool = True, run_mena: bool = False):
    """Fetch funding news from yesterday with optional LLM classification."""
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Initialize OpenAI client if available
    openai_client = None
    if use_llm and OPENAI_AVAILABLE:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and not api_key.startswith("sk-your"):
            openai_client = OpenAI(api_key=api_key)
            print("🤖 Using LLM-based classification for accurate detection\n")
        else:
            print("⚠️  No OPENAI_API_KEY set. Using keyword-based detection.")
            print("   Set OPENAI_API_KEY environment variable for better accuracy.\n")
    elif use_llm and not OPENAI_AVAILABLE:
        print("⚠️  OpenAI package not installed. Using keyword-based detection.\n")
    
    print(f"{'=' * 60}")
    print(f"AI STARTUP FUNDING NEWS")
    print(f"Date: {yesterday.strftime('%B %d, %Y')}")
    print(f"{'=' * 60}")
    print()
    
    # First pass: collect all potential candidates
    candidates = []
    
    print("📡 Fetching from RSS feeds...")
    for feed_name, feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Parse published date
                published_at = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_at = datetime(*entry.published_parsed[:6])
                elif hasattr(entry, 'published'):
                    try:
                        published_at = date_parser.parse(entry.published)
                    except:
                        continue
                
                if not published_at:
                    continue
                
                # Check if from yesterday
                if not (yesterday_start <= published_at < today_start):
                    continue
                
                title = entry.get('title', 'Untitled')
                link = entry.get('link', '')
                summary = clean_html(entry.get('summary', entry.get('description', '')))[:500]
                
                # Pre-filter: quick keyword check to reduce LLM calls
                if not is_funding_related(title, summary):
                    continue
                
                candidates.append({
                    'source': feed_name,
                    'title': title,
                    'link': link,
                    'summary': summary,
                    'published': published_at,
                })
                
        except Exception as e:
            print(f"   Error fetching {feed_name}: {e}")
    
    print(f"   Found {len(candidates)} potential articles\n")
    
    # Remove duplicates by title similarity
    seen_titles = set()
    unique_candidates = []
    for item in candidates:
        title_key = item['title'].lower()[:50]
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            unique_candidates.append(item)
    
    print(f"   {len(unique_candidates)} unique articles after deduplication\n")
    
    # Second pass: classify with LLM or keywords
    confirmed_news = []
    rejected_count = 0
    
    # Check for debug mode (set in main block)
    debug_mode = globals().get('DEBUG_MODE', False)
    
    if openai_client:
        print("🔍 Classifying articles with LLM...\n")
        for i, item in enumerate(unique_candidates):
            classification = classify_with_llm(item['title'], item['summary'], openai_client, verbose=True, debug=debug_mode)
            
            if classification.is_fundraising and classification.confidence >= 0.6:
                item['classification'] = classification
                item['amount'] = classification.amount or extract_amount(f"{item['title']} {item['summary']}")
                item['company'] = classification.company_name
                item['round_type'] = classification.round_type
                item['confidence'] = classification.confidence
                confirmed_news.append(item)
            else:
                rejected_count += 1
        
        print(f"\n   ✅ Accepted: {len(confirmed_news)} | ❌ Rejected: {rejected_count}\n")
    else:
        # Keyword-based fallback
        print("🔍 Classifying articles with keywords...")
        for item in unique_candidates:
            classification = classify_with_keywords(item['title'], item['summary'])
            
            if classification.is_fundraising and classification.confidence >= 0.5:
                item['classification'] = classification
                item['amount'] = classification.amount or extract_amount(f"{item['title']} {item['summary']}")
                item['company'] = classification.company_name
                item['round_type'] = classification.round_type
                item['confidence'] = classification.confidence
                confirmed_news.append(item)
        
        print(f"   Classification complete!\n")
    
    # Sort by confidence, then published time
    confirmed_news.sort(key=lambda x: (-x.get('confidence', 0), x['published']), reverse=False)
    confirmed_news.sort(key=lambda x: x['published'], reverse=True)
    
    if not confirmed_news:
        print("❌ No AI startup funding news found from yesterday.")
        print("\n💡 Tips:")
        print("   - Try running this script on a weekday for more results")
        print("   - Set OPENAI_API_KEY for better classification accuracy")
        return []
    
    print(f"✅ Found {len(confirmed_news)} confirmed funding news items:\n")
    print("-" * 60)
    
    for i, item in enumerate(confirmed_news, 1):
        # Build info string
        info_parts = []
        if item.get('amount'):
            info_parts.append(item['amount'])
        if item.get('round_type'):
            info_parts.append(item['round_type'])
        if item.get('confidence'):
            info_parts.append(f"{int(item['confidence'] * 100)}% conf")
        
        info_str = f" [{', '.join(info_parts)}]" if info_parts else ""
        
        print(f"{i}. {item['title']}{info_str}")
        if item.get('company'):
            print(f"   🏢 Company: {item['company']}")
        print(f"   📰 Source: {item['source']}")
        print(f"   🔗 {item['link']}")
        if item['summary']:
            print(f"   📝 {item['summary'][:150]}...")
        print()
    
    # Run MENA analysis if requested
    if run_mena and confirmed_news and openai_client:
        print("\n" + "=" * 60)
        print("🌍 RUNNING MENA MARKET ANALYSIS")
        print("=" * 60)
        
        if not SCRAPING_AVAILABLE:
            print("\n⚠️  Web scraping not available. Install with: pip install requests beautifulsoup4")
            print("   Using RSS summaries instead of full article content.\n")
        
        for i, item in enumerate(confirmed_news, 1):
            print(f"\n📄 Fetching article {i}/{len(confirmed_news)}: {item['title'][:50]}...")
            
            # Try to fetch full article content
            full_content = None
            if SCRAPING_AVAILABLE:
                full_content = fetch_article_content(item['link'])
            
            # Use RSS summary as fallback
            content = full_content if full_content else item['summary']
            content_source = "full article" if full_content else "RSS summary"
            print(f"   Using {content_source} ({len(content)} chars)")
            
            # Run MENA analysis
            print(f"   🔍 Analyzing MENA potential...")
            analysis = run_mena_analysis(item['title'], content, openai_client)
            
            if analysis:
                item['mena_analysis'] = analysis
                print_mena_analysis(item, analysis, i)
            else:
                print(f"   ⚠️  Could not generate MENA analysis")
    
    return confirmed_news


def export_to_txt(results: List[Dict[str, Any]], filename: str):
    """Export results to a formatted text file."""
    lines = []
    
    # Header
    yesterday = datetime.now() - timedelta(days=1)
    lines.append("=" * 80)
    lines.append("MENA SIGNAL - AI STARTUP FUNDING REPORT")
    lines.append(f"Date: {yesterday.strftime('%B %d, %Y')}")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Summary
    lines.append(f"EXECUTIVE SUMMARY")
    lines.append("-" * 40)
    lines.append(f"Total Funding News Found: {len(results)}")
    
    if any('mena_analysis' in item for item in results):
        high_priority = sum(1 for item in results if 'mena_analysis' in item and 'prototyping' in item['mena_analysis'].priority.lower())
        lines.append(f"High Priority (Worth Prototyping): {high_priority}")
    lines.append("")
    
    # Each article
    for i, item in enumerate(results, 1):
        lines.append("")
        lines.append("=" * 80)
        lines.append(f"#{i} {item['title']}")
        lines.append("=" * 80)
        lines.append("")
        
        # Basic info
        lines.append("FUNDING DETAILS")
        lines.append("-" * 40)
        lines.append(f"Company: {item.get('company', 'Unknown')}")
        lines.append(f"Amount: {item.get('amount', 'Undisclosed')}")
        lines.append(f"Round: {item.get('round_type', 'Unknown')}")
        lines.append(f"Source: {item['source']}")
        lines.append(f"Link: {item['link']}")
        lines.append(f"Published: {item['published'].strftime('%Y-%m-%d')}")
        lines.append("")
        lines.append("Summary:")
        lines.append(item['summary'])
        lines.append("")
        
        # MENA Analysis if present
        if 'mena_analysis' in item:
            analysis = item['mena_analysis']
            
            lines.append("MENA MARKET ANALYSIS")
            lines.append("-" * 40)
            lines.append("")
            
            lines.append("1. INNOVATION SUMMARY")
            lines.append(f"   Type: {analysis.innovation_type}")
            lines.append(f"   {analysis.innovation_summary}")
            lines.append("")
            
            lines.append("2. PROBLEM-SOLUTION FIT IN MENA")
            lines.append(f"   {analysis.problem_solution_fit}")
            lines.append(f"   Target Sectors: {', '.join(analysis.target_sectors)}")
            lines.append(f"   Vision 2030 Alignment: {analysis.vision_2030_alignment}")
            lines.append("")
            
            lines.append("3. LOCALIZABILITY SCORECARD")
            lines.append(f"   Arabic Complexity: {analysis.arabic_complexity}")
            lines.append(f"     - {analysis.arabic_complexity_notes}")
            lines.append(f"   Regulatory Fit: {analysis.regulatory_fit}")
            lines.append(f"     - {analysis.regulatory_fit_notes}")
            lines.append(f"   Market Readiness: {analysis.market_readiness}")
            lines.append(f"     - {analysis.market_readiness_notes}")
            lines.append(f"   Infrastructure Fit: {analysis.infrastructure_fit}")
            lines.append(f"     - {analysis.infrastructure_fit_notes}")
            lines.append("")
            
            lines.append("4. COMMERCIAL BUYER MAP")
            lines.append(f"   Potential Buyers: {', '.join(analysis.potential_buyers)}")
            lines.append(f"   Sales Motion: {analysis.sales_motion}")
            lines.append("")
            
            lines.append("5. OPPORTUNITY RATING")
            lines.append(f"   Commercialization Potential: {analysis.commercialization_potential}")
            lines.append(f"   Localization Requirement: {analysis.localization_requirement}")
            lines.append(f"   Priority: {analysis.priority}")
            lines.append("")
            
            lines.append("6. JUSTIFICATION")
            lines.append(f"   {analysis.justification}")
            lines.append("")
    
    # Footer
    lines.append("")
    lines.append("=" * 80)
    lines.append("END OF REPORT")
    lines.append("=" * 80)
    
    with open(filename, 'w') as f:
        f.write('\n'.join(lines))


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch yesterday's AI startup funding news")
    parser.add_argument("--no-llm", action="store_true", help="Disable LLM classification (use keywords only)")
    parser.add_argument("--mena", action="store_true", help="Run MENA market analysis on filtered articles")
    parser.add_argument("--export", type=str, help="Export results to file (.txt or .json based on extension)")
    parser.add_argument("--debug", action="store_true", help="Enable debug output for LLM responses")
    args = parser.parse_args()
    
    # Store debug flag globally for use in classification
    DEBUG_MODE = args.debug
    
    results = fetch_yesterdays_funding_news(use_llm=not args.no_llm, run_mena=args.mena)
    
    if args.export and results:
        # Determine export format by file extension
        if args.export.endswith('.txt'):
            export_to_txt(results, args.export)
            print(f"\n📁 Report exported to {args.export}")
        else:
            # Export to JSON (default)
            export_data = []
            for item in results:
                item_data = {
                    'title': item['title'],
                    'company': item.get('company'),
                    'amount': item.get('amount'),
                    'round_type': item.get('round_type'),
                    'source': item['source'],
                    'link': item['link'],
                    'summary': item['summary'],
                    'published': item['published'].isoformat(),
                    'confidence': item.get('confidence', 0)
                }
                
                # Include MENA analysis if present
                if 'mena_analysis' in item:
                    analysis = item['mena_analysis']
                    item_data['mena_analysis'] = {
                        'innovation_summary': analysis.innovation_summary,
                        'innovation_type': analysis.innovation_type,
                        'problem_solution_fit': analysis.problem_solution_fit,
                        'target_sectors': analysis.target_sectors,
                        'vision_2030_alignment': analysis.vision_2030_alignment,
                        'localizability': {
                            'arabic_complexity': analysis.arabic_complexity,
                            'arabic_notes': analysis.arabic_complexity_notes,
                            'regulatory_fit': analysis.regulatory_fit,
                            'regulatory_notes': analysis.regulatory_fit_notes,
                            'market_readiness': analysis.market_readiness,
                            'market_notes': analysis.market_readiness_notes,
                            'infrastructure_fit': analysis.infrastructure_fit,
                            'infrastructure_notes': analysis.infrastructure_fit_notes
                        },
                        'commercial': {
                            'potential_buyers': analysis.potential_buyers,
                            'sales_motion': analysis.sales_motion
                        },
                        'opportunity': {
                            'commercialization_potential': analysis.commercialization_potential,
                            'localization_requirement': analysis.localization_requirement,
                            'priority': analysis.priority
                        },
                        'justification': analysis.justification
                    }
                
                export_data.append(item_data)
            
            with open(args.export, 'w') as f:
                json.dump(export_data, f, indent=2)
            print(f"\n📁 Results exported to {args.export}")

