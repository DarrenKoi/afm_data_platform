"""
Centralized logger configuration for the entire application.
This ensures all parts of the app (Flask, scheduler, background tasks) use the same logger.
"""
import os
from .logger_manager import LoggerManager

# Singleton instances for different logger purposes
_system_log_manager = None
_system_logger = None
_activity_log_manager = None
_activity_logger = None
_error_log_manager = None
_error_logger = None

def get_system_logger():
    """
    Get the system logger for application lifecycle events (startup, shutdown, configuration).
    """
    global _system_log_manager, _system_logger
    
    if _system_logger is None:
        _system_log_manager = LoggerManager(
            log_name="afm_system",
            log_file_path="logs/system/afm_system.log",
            level=os.getenv('LOG_LEVEL', 'INFO'),
            mode="prod" if os.getenv('FLASK_ENV') == 'production' else "dev",
            console_level="INFO",
            retention="60 days",
            rotation="50 MB",
            json_format=os.getenv('FLASK_ENV') == 'production',
            enable_exception_logging=False,
            backtrace=False,
            diagnose=False
        )
        _system_logger = _system_log_manager.get_logger()
        
        # Add application startup log
        _system_logger.info("System logger initialized", 
                          pid=os.getpid(),
                          log_file=_system_log_manager.log_file_path.absolute())
    
    return _system_logger

def get_activity_logger():
    """
    Get the activity logger for user activities and API requests.
    """
    global _activity_log_manager, _activity_logger
    
    if _activity_logger is None:
        _activity_log_manager = LoggerManager(
            log_name="afm_activity",
            log_file_path="logs/activity/afm_activity.log",
            level=os.getenv('LOG_LEVEL', 'INFO'),
            mode="prod" if os.getenv('FLASK_ENV') == 'production' else "dev",
            console_level="WARNING",  # Less verbose for activity logs
            retention="90 days",  # Keep activity logs longer
            rotation="200 MB",
            json_format=True,  # Always use JSON for activity logs (easier to parse)
            enable_exception_logging=False,
            backtrace=False,
            diagnose=False
        )
        _activity_logger = _activity_log_manager.get_logger()
        
        _activity_logger.info("Activity logger initialized", 
                            pid=os.getpid(),
                            log_file=_activity_log_manager.log_file_path.absolute())
    
    return _activity_logger

def get_error_logger():
    """
    Get the error logger for exceptions and error handling.
    """
    global _error_log_manager, _error_logger
    
    if _error_logger is None:
        _error_log_manager = LoggerManager(
            log_name="afm_error",
            log_file_path="logs/error/afm_error.log",
            level="WARNING",  # Only log warnings and errors
            mode="prod" if os.getenv('FLASK_ENV') == 'production' else "dev",
            console_level="ERROR",
            retention="180 days",  # Keep error logs even longer
            rotation="100 MB",
            json_format=os.getenv('FLASK_ENV') == 'production',
            enable_exception_logging=True,
            backtrace=True,
            diagnose=os.getenv('FLASK_ENV') != 'production'
        )
        _error_logger = _error_log_manager.get_logger()
        
        _error_logger.info("Error logger initialized", 
                         pid=os.getpid(),
                         log_file=_error_log_manager.log_file_path.absolute())
    
    return _error_logger

# Backward compatibility - get_app_logger returns system logger
def get_app_logger():
    """
    Get the centralized application logger instance.
    This ensures all parts of the application use the same logger configuration.
    (Deprecated: Use get_system_logger, get_activity_logger, or get_error_logger instead)
    """
    return get_system_logger()

def get_task_logger(task_name: str):
    """
    Get a logger instance for a specific background task.
    This adds task context to all log messages.
    
    Args:
        task_name: Name of the background task
        
    Returns:
        Logger instance with task context
    """
    base_logger = get_app_logger()
    return base_logger.bind(task=task_name, task_type="scheduled")

def cleanup_logger():
    """
    Clean up all logger instances.
    Should be called when the application shuts down.
    """
    global _system_log_manager, _system_logger
    global _activity_log_manager, _activity_logger
    global _error_log_manager, _error_logger
    
    # Cleanup system logger
    if _system_log_manager:
        _system_logger.info("Shutting down system logger")
        _system_log_manager.cleanup()
        _system_log_manager = None
        _system_logger = None
    
    # Cleanup activity logger
    if _activity_log_manager:
        _activity_logger.info("Shutting down activity logger")
        _activity_log_manager.cleanup()
        _activity_log_manager = None
        _activity_logger = None
    
    # Cleanup error logger
    if _error_log_manager:
        _error_logger.info("Shutting down error logger")
        _error_log_manager.cleanup()
        _error_log_manager = None
        _error_logger = None

# Create convenience aliases for backward compatibility
logger = get_system_logger()
system_logger = get_system_logger()
activity_logger = get_activity_logger()
error_logger = get_error_logger()