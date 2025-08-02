"""
User Activity API Routes
Handles user activity tracking and retrieval
"""
from flask import Blueprint, jsonify, request
from .user_activity import get_user_activities, get_current_user

# Create activity blueprint
activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/user-activities', methods=['GET'])
def get_activities():
    """Get user activities log"""
    try:
        # Get optional user filter from query params
        user_id = request.args.get('user')
        limit = int(request.args.get('limit', 100))
        
        activities = get_user_activities(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': activities,
            'count': len(activities),
            'message': f'Retrieved {len(activities)} activities'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve activities'
        }), 500


@activity_bp.route('/my-activities', methods=['GET'])
def get_my_activities():
    """Get current user's activities"""
    try:
        # Get current user from cookie
        current_user = request.cookies.get('LAST_USER')
        if not current_user:
            return jsonify({
                'success': False,
                'error': 'No user identified',
                'message': 'LAST_USER cookie not found'
            }), 400
        
        activities = get_user_activities(current_user, 50)
        
        return jsonify({
            'success': True,
            'user': current_user,
            'data': activities,
            'count': len(activities),
            'message': f'Retrieved {len(activities)} activities for {current_user}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve user activities'
        }), 500


@activity_bp.route('/current-user', methods=['GET'])
def get_current_user_endpoint():
    """Get current user from cookie"""
    try:
        current_user = request.cookies.get('LAST_USER')
        
        if not current_user:
            return jsonify({
                'success': False,
                'error': 'No user identified',
                'message': 'LAST_USER cookie not found'
            }), 400
        
        return jsonify({
            'success': True,
            'user': current_user,
            'message': f'Current user: {current_user}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get current user'
        }), 500


@activity_bp.route('/debug/cookies', methods=['GET'])
def debug_cookies():
    """Debug endpoint to see all cookies"""
    cookies = {}
    for cookie_name, cookie_value in request.cookies.items():
        cookies[cookie_name] = cookie_value
    
    return jsonify({
        'success': True,
        'cookies': cookies,
        'count': len(cookies),
        'message': 'All cookies received by server'
    })