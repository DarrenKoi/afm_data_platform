from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging

# Configure logging for scheduler
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scheduled_data_cleanup():
    """Example scheduled job for data cleanup"""
    logger.info(f"Running scheduled data cleanup at {datetime.now()}")
    # Add your scheduled tasks here
    # For example: clean old files, update cached data, etc.

def scheduled_health_check():
    """Example scheduled job for system health check"""
    logger.info(f"Running system health check at {datetime.now()}")
    # Add health check logic here

def init_scheduler(app):
    """Initialize and configure the scheduler"""
    scheduler = BackgroundScheduler()
    
    # Add scheduled jobs
    scheduler.add_job(
        func=scheduled_data_cleanup,
        trigger="interval",
        hours=24,  # Run daily
        id='data_cleanup_job',
        name='Daily data cleanup',
        replace_existing=True
    )
    
    scheduler.add_job(
        func=scheduled_health_check,
        trigger="interval",
        minutes=30,  # Run every 30 minutes
        id='health_check_job',
        name='System health check',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler initialized and started")
    
    return scheduler