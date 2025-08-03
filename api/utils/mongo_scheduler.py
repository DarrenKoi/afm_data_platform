"""
MongoDB cleanup scheduler for AFM data platform
Runs periodic cleanup of old measurements
"""
import os
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .mongo_client import get_mongo_client

logger = logging.getLogger(__name__)


class MongoCleanupScheduler:
    """Scheduler for MongoDB cleanup tasks"""
    
    def __init__(self, days_to_keep=300):
        """
        Initialize scheduler
        
        Args:
            days_to_keep: Number of days to keep measurements (default 300)
        """
        self.scheduler = BackgroundScheduler()
        self.days_to_keep = days_to_keep
        self.mongo_client = None
        
    def cleanup_job(self):
        """Job function for cleaning up old measurements"""
        try:
            logger.info(f"Starting scheduled cleanup job at {datetime.utcnow()}")
            
            # Get MongoDB client
            self.mongo_client = get_mongo_client()
            
            if not self.mongo_client.db:
                logger.error("MongoDB not connected, skipping cleanup")
                return
            
            # First, get statistics before cleanup
            logger.info("Getting date statistics before cleanup...")
            for tool in ['MAP608', 'MAPC01', '5EAP1501']:
                stats = self.mongo_client.get_date_statistics(tool)
                if stats:
                    logger.info(f"{tool} - Measurements over 300 days: {stats['age_buckets']['over_300_days']}")
            
            # Run cleanup for all tools
            result = self.mongo_client.cleanup_all_tools(
                days_to_keep=self.days_to_keep,
                dry_run=False  # Set to True for testing
            )
            
            logger.info(f"Cleanup completed: {result['total_deleted']} documents deleted")
            logger.info(f"Cleanup details: {result}")
            
            # Send notification if needed (email, Slack, etc.)
            if result['total_deleted'] > 0:
                self._send_cleanup_notification(result)
                
        except Exception as e:
            logger.error(f"Error in cleanup job: {e}")
            # Send error notification
            self._send_error_notification(str(e))
    
    def _send_cleanup_notification(self, result):
        """Send notification about cleanup results"""
        # Implement notification logic (email, Slack, etc.)
        # For now, just log
        logger.info(f"NOTIFICATION: Cleanup completed - {result['total_deleted']} measurements deleted")
    
    def _send_error_notification(self, error_msg):
        """Send notification about cleanup errors"""
        # Implement error notification logic
        logger.error(f"NOTIFICATION: Cleanup failed - {error_msg}")
    
    def start(self):
        """Start the scheduler"""
        # Schedule cleanup job
        # Run daily at 2 AM
        self.scheduler.add_job(
            self.cleanup_job,
            CronTrigger(hour=2, minute=0),
            id='mongodb_cleanup',
            name='MongoDB Old Data Cleanup',
            replace_existing=True
        )
        
        # Add a job to check statistics weekly
        self.scheduler.add_job(
            self.check_statistics,
            CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='mongodb_stats',
            name='MongoDB Statistics Check',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info("MongoDB cleanup scheduler started")
    
    def check_statistics(self):
        """Check and log MongoDB statistics"""
        try:
            logger.info("Running weekly statistics check...")
            
            self.mongo_client = get_mongo_client()
            
            total_stats = {
                'total_measurements': 0,
                'measurements_by_age': {
                    '0-30_days': 0,
                    '31-90_days': 0,
                    '91-180_days': 0,
                    '181-300_days': 0,
                    'over_300_days': 0
                }
            }
            
            for tool in ['MAP608', 'MAPC01', '5EAP1501']:
                stats = self.mongo_client.get_date_statistics(tool)
                if stats:
                    total_stats['total_measurements'] += stats['total_measurements']
                    for age_key, count in stats['age_buckets'].items():
                        total_stats['measurements_by_age'][age_key] += count
            
            logger.info(f"Weekly Statistics Report: {total_stats}")
            
            # Alert if too many old measurements
            if total_stats['measurements_by_age']['over_300_days'] > 10000:
                logger.warning(f"WARNING: {total_stats['measurements_by_age']['over_300_days']} "
                             f"measurements are over 300 days old")
                
        except Exception as e:
            logger.error(f"Error in statistics check: {e}")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("MongoDB cleanup scheduler stopped")
    
    def run_cleanup_now(self, dry_run=True):
        """Run cleanup immediately (for testing)"""
        logger.info(f"Running manual cleanup (dry_run={dry_run})...")
        
        self.mongo_client = get_mongo_client()
        result = self.mongo_client.cleanup_all_tools(
            days_to_keep=self.days_to_keep,
            dry_run=dry_run
        )
        
        return result


# Example usage in Flask app
def init_mongodb_scheduler(app=None):
    """
    Initialize MongoDB cleanup scheduler
    
    Args:
        app: Flask app instance (optional)
    
    Returns:
        MongoCleanupScheduler instance
    """
    # Check if cleanup is enabled
    if os.getenv('ENABLE_MONGODB_CLEANUP', 'false').lower() != 'true':
        logger.info("MongoDB cleanup scheduler is disabled")
        return None
    
    # Get configuration
    days_to_keep = int(os.getenv('MONGODB_CLEANUP_DAYS', '300'))
    
    # Create and start scheduler
    scheduler = MongoCleanupScheduler(days_to_keep=days_to_keep)
    scheduler.start()
    
    # Register shutdown handler if Flask app provided
    if app:
        import atexit
        atexit.register(lambda: scheduler.stop())
    
    return scheduler


if __name__ == "__main__":
    # Test the scheduler
    logging.basicConfig(level=logging.INFO)
    
    # Create scheduler
    scheduler = MongoCleanupScheduler(days_to_keep=300)
    
    # Run cleanup in dry-run mode
    print("Running cleanup in dry-run mode...")
    result = scheduler.run_cleanup_now(dry_run=True)
    print(f"Dry run result: {result}")
    
    # Start scheduler (for production)
    # scheduler.start()
    # 
    # try:
    #     # Keep the main thread alive
    #     while True:
    #         time.sleep(60)
    # except (KeyboardInterrupt, SystemExit):
    #     scheduler.stop()