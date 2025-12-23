import json
import logging
from typing import Optional, Dict, Any

from openai import OpenAI

from app.config import get_settings
from app.database import get_db_context
from app.models import Item, MenaAnalysis, ItemType
from app.services.ingestion import get_queue

logger = logging.getLogger(__name__)
settings = get_settings()


MENA_ANALYSIS_PROMPT = """You are an AI analyst specializing in MENA (Middle East & North Africa) market opportunity assessment.

Analyze the following AI company/funding news and determine its applicability for the MENA market.

Title: {title}
Company: {company_name}
Type: {item_type}
Summary: {summary}
{additional_context}

Score each dimension from 0-20 based on:

1. **budget_buyer_exists** (0-20): Does MENA have buyers with budget for this? Consider:
   - Government/sovereign wealth fund relevance
   - Enterprise adoption potential in GCC
   - SMB market fit

2. **localization_arabic_bilingual** (0-20): How easy is localization?
   - Software-only (high score) vs hardware-dependent (low)
   - Arabic language requirements
   - Cultural adaptation needs

3. **regulatory_friction** (0-20): Higher score = easier regulatory path
   - Data sovereignty concerns
   - Industry-specific regulations
   - Government approval requirements

4. **distribution_path** (0-20): Clear path to market?
   - Existing channel partners
   - Local competition landscape
   - Go-to-market complexity

5. **time_to_revenue** (0-20): How quickly can this generate MENA revenue?
   - Sales cycle length
   - Implementation complexity
   - Customer education needs

Respond ONLY with valid JSON:
{{
  "fit_score": <sum of all dimensions, 0-100>,
  "mena_summary": "<2-3 sentences on MENA applicability>",
  "rubric": {{
    "budget_buyer_exists": <0-20>,
    "localization_arabic_bilingual": <0-20>,
    "regulatory_friction": <0-20>,
    "distribution_path": <0-20>,
    "time_to_revenue": <0-20>
  }}
}}
"""


def get_stub_analysis() -> Dict[str, Any]:
    """Return stub analysis when LLM is not available."""
    return {
        "fit_score": 50,
        "mena_summary": "This opportunity requires further analysis to assess MENA applicability. Key factors to evaluate include regional buyer appetite, localization requirements, and regulatory considerations.",
        "rubric": {
            "budget_buyer_exists": 10,
            "localization_arabic_bilingual": 10,
            "regulatory_friction": 10,
            "distribution_path": 10,
            "time_to_revenue": 10,
        }
    }


def run_llm_analysis(item: Item) -> Dict[str, Any]:
    """Run LLM-based MENA analysis."""
    if not settings.openai_api_key:
        logger.info("No OpenAI API key configured, using stub analysis")
        return get_stub_analysis()
    
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        
        # Build additional context
        additional_context = ""
        if item.funding_details:
            fd = item.funding_details
            if fd.round_type:
                additional_context += f"Round Type: {fd.round_type}\n"
            if fd.amount_usd:
                additional_context += f"Amount: ${fd.amount_usd:,.0f}\n"
            if fd.investors:
                additional_context += f"Investors: {', '.join(fd.investors) if isinstance(fd.investors, list) else fd.investors}\n"
        
        if item.company_details:
            cd = item.company_details
            if cd.category:
                additional_context += f"Category: {cd.category}\n"
            if cd.stage_hint:
                additional_context += f"Stage: {cd.stage_hint}\n"
        
        prompt = MENA_ANALYSIS_PROMPT.format(
            title=item.title,
            company_name=item.company_name or "Unknown",
            item_type=item.type.value,
            summary=item.summary or "No summary available",
            additional_context=additional_context,
        )
        
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": "You are a MENA market analyst. Respond only with valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        if content.startswith("```"):
            # Remove markdown code blocks
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        result = json.loads(content)
        
        # Validate and sanitize
        fit_score = min(100, max(0, int(result.get("fit_score", 50))))
        mena_summary = result.get("mena_summary", "Analysis completed.")[:1000]
        rubric = result.get("rubric", {})
        
        # Ensure rubric values are valid
        for key in ["budget_buyer_exists", "localization_arabic_bilingual", "regulatory_friction", "distribution_path", "time_to_revenue"]:
            if key in rubric:
                rubric[key] = min(20, max(0, int(rubric[key])))
            else:
                rubric[key] = 10
        
        return {
            "fit_score": fit_score,
            "mena_summary": mena_summary,
            "rubric": rubric,
        }
        
    except Exception as e:
        logger.exception(f"Error running LLM analysis: {e}")
        return get_stub_analysis()


def analyze_item(item_id: int) -> Dict[str, Any]:
    """Analyze a single item for MENA applicability."""
    with get_db_context() as db:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return {"status": "error", "message": "Item not found"}
        
        # Check if analysis already exists
        existing = db.query(MenaAnalysis).filter(MenaAnalysis.item_id == item_id).first()
        if existing:
            return {"status": "skipped", "message": "Analysis already exists"}
        
        # Run analysis
        result = run_llm_analysis(item)
        
        # Save analysis
        analysis = MenaAnalysis(
            item_id=item_id,
            fit_score=result["fit_score"],
            mena_summary=result["mena_summary"],
            rubric_json=result.get("rubric"),
            model_name=settings.openai_model if settings.openai_api_key else "stub",
        )
        db.add(analysis)
        db.commit()
        
        return {"status": "success", "fit_score": result["fit_score"]}


def enqueue_analysis(item_id: int) -> Optional[str]:
    """Enqueue an analysis job."""
    try:
        queue = get_queue()
        job = queue.enqueue(analyze_item, item_id, job_timeout=60)
        return job.id
    except Exception as e:
        logger.error(f"Error enqueueing analysis job: {e}")
        # Run synchronously as fallback
        analyze_item(item_id)
        return None


def reanalyze_all_items() -> Dict[str, int]:
    """Re-analyze all items that don't have analysis."""
    with get_db_context() as db:
        items_without_analysis = db.query(Item).filter(
            ~Item.id.in_(
                db.query(MenaAnalysis.item_id)
            )
        ).all()
        
        count = 0
        for item in items_without_analysis:
            enqueue_analysis(item.id)
            count += 1
        
        return {"queued": count}

