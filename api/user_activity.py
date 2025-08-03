"""
User Activity Logging Module
Tracks user activities based on LAST_USER cookie
"""

from flask import request
from datetime import datetime
import os
import json
from api.utils.app_logger import get_activity_logger, get_error_logger

# Activity log file path (kept for backward compatibility)
ACTIVITY_LOG_FILE = 'user_activities.txt'

# Get logger instances
activity_logger = get_activity_logger()
error_logger = get_error_logger()

def log_user_activity():
    """Log user activity using the activity logger"""
    try:
        # Get the LAST_USER cookie
        user_id = request.cookies.get('LAST_USER', 'anonymous')
        
        # Log activity with structured data
        activity_logger.info("User activity",
                           user=user_id,
                           method=request.method,
                           path=request.path,
                           endpoint=request.endpoint,
                           ip_address=request.remote_addr,
                           user_agent=request.headers.get('User-Agent', ''),
                           query_params=dict(request.args) if request.args else None,
                           referrer=request.referrer)
        
        # Also write to legacy file for backward compatibility
        activity = {
            'timestamp': datetime.now().isoformat(),
            'user': user_id,
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        with open(ACTIVITY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(activity) + '\n')
            
    except Exception as e:
        # Don't let logging errors break the application
        error_logger.error("Failed to log user activity",
                         error=str(e),
                         error_type=type(e).__name__,
                         path=request.path if request else None)

def get_current_user():
    """Get the current user from cookie"""
    return request.cookies.get('LAST_USER', None)

def get_user_activities(user_id=None, limit=100):
    """Read user activities from log file"""
    activities = []
    
    if not os.path.exists(ACTIVITY_LOG_FILE):
        return activities
    
    try:
        with open(ACTIVITY_LOG_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Parse each line
        for line in reversed(lines[-limit:]):
            try:
                activity = json.loads(line.strip())
                if user_id is None or activity.get('user') == user_id:
                    activities.append(activity)
            except json.JSONDecodeError:
                continue
                
    except Exception as e:
        error_logger.error("Failed to read user activities",
                         error=str(e),
                         error_type=type(e).__name__,
                         user_id=user_id,
                         limit=limit)
    
    return activities