from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from pathlib import Path
from .utils.file_parser import parse_and_cache_afm_data

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


def scheduled_afm_data_parsing():
    """Scheduled job to parse and cache AFM data from data_dir_list.txt"""
    logger.info(f"🔄 Starting scheduled AFM data parsing at {datetime.now()}")
    
    # List of tools to process (can be extended to support multiple tools)
    tools = ['MAP608']
    
    for tool_name in tools:
        try:
            logger.info(f"📊 Processing tool: {tool_name}")
            success = parse_and_cache_afm_data(tool_name)
            
            if success:
                logger.info(f"✅ Successfully cached data for {tool_name}")
            else:
                logger.error(f"❌ Failed to cache data for {tool_name}")
                
        except Exception as e:
            logger.error(f"❌ Error processing {tool_name}: {e}")
    
    logger.info(f"🏁 Completed scheduled AFM data parsing at {datetime.now()}")


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
    
    # Add AFM data parsing job - runs every hour to keep data up to date
    scheduler.add_job(
        func=scheduled_afm_data_parsing,
        trigger="interval",
        hours=1,  # Run every hour
        id='afm_data_parsing_job',
        name='AFM data parsing and caching',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("🚀 Scheduler initialized and started")

    return scheduler