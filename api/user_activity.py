"""
User Activity Logging Module
Tracks user activities based on LAST_USER cookie
"""

from flask import request
from datetime import datetime
import os
import json

# Activity log file path
ACTIVITY_LOG_FILE = 'user_activities.txt'

def log_user_activity():
    """Log user activity to a text file"""
    try:
        # Get the LAST_USER cookie
        user_id = request.cookies.get('LAST_USER', 'anonymous')
        
        # Create activity record
        activity = {
            'timestamp': datetime.now().isoformat(),
            'user': user_id,
            'method': request.method,
            'path': request.path,
            'endpoint': request.endpoint,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        }
        
        # Write to log file
        with open(ACTIVITY_LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(activity) + '\n')
            
    except Exception as e:
        # Don't let logging errors break the application
        print(f"Error logging activity: {e}")

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
        print(f"Error reading activities: {e}")
    
    return activities