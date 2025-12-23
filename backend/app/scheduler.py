"""
Background scheduler for periodic ingestion.
Run with: python -m app.scheduler
"""
import logging
import time
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.services.ingestion import ingest_all_sources, load_sources_from_yaml

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


def run_ingestion():
    """Run the ingestion job."""
    logger.info(f"Starting scheduled ingestion at {datetime.utcnow()}")
    try:
        results = ingest_all_sources()
        total_items = sum(r.get('items_added', 0) for r in results.values() if isinstance(r, dict))
        logger.info(f"Ingestion completed. Total items added: {total_items}")
    except Exception as e:
        logger.exception(f"Error during scheduled ingestion: {e}")


def main():
    """Main scheduler entry point."""
    logger.info("Starting MENA Signal Scheduler")
    
    # Load sources from YAML on startup
    logger.info("Loading sources from YAML configuration")
    try:
        load_sources_from_yaml()
    except Exception as e:
        logger.error(f"Error loading sources: {e}")
    
    # Run initial ingestion
    logger.info("Running initial ingestion")
    run_ingestion()
    
    # Set up scheduler
    scheduler = BlockingScheduler()
    
    # Schedule ingestion every N minutes
    scheduler.add_job(
        run_ingestion,
        trigger=IntervalTrigger(minutes=settings.ingestion_interval_minutes),
        id='ingest_all_sources',
        name='Ingest all enabled sources',
        replace_existing=True,
    )
    
    logger.info(f"Scheduler configured to run every {settings.ingestion_interval_minutes} minutes")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down")


if __name__ == "__main__":
    main()

