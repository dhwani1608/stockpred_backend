"""Background tasks and scheduled jobs."""

from apscheduler.schedulers.background import BackgroundScheduler
from app.services.market_data import market_data_service
import logging

logger = logging.getLogger(__name__)


def daily_update_job():
    """Job that runs daily to update market data and make predictions."""
    logger.info("Running daily update job...")
    # TODO: Implement daily batch predictions
    pass


def init_scheduler():
    """Initialize APScheduler."""
    scheduler = BackgroundScheduler()
    # Schedule daily job at 9:30 AM
    scheduler.add_job(daily_update_job, "cron", hour=9, minute=30)
    scheduler.start()
    return scheduler
