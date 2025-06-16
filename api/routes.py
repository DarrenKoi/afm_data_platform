from flask import Blueprint, jsonify, request
from .data_service import get_dummy_afm_data, get_trend_data, get_analysis_results, get_profile_data, get_summary_data
from .measurement_data_service import afm_data_service

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'API is healthy', 'service': 'AFM Data Platform API'})

@api_bp.route('/afm-data', methods=['GET'])
def get_afm_data():
    """Get dummy AFM measurement data"""
    try:
        data = get_dummy_afm_data()
        return jsonify({
            'success': True,
            'data': data,
            'message': 'AFM data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve AFM data'
        }), 500

@api_bp.route('/trend-data', methods=['GET'])
def get_trend_data_endpoint():
    """Get trend analysis data"""
    try:
        data = get_trend_data()
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Trend data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve trend data'
        }), 500

@api_bp.route('/analysis-results', methods=['GET'])
def get_analysis_results_endpoint():
    """Get analysis results data"""
    try:
        data = get_analysis_results()
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Analysis results retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve analysis results'
        }), 500

@api_bp.route('/profile-data/<group_key>/<int:point>', methods=['GET'])
def get_profile_data_endpoint(group_key, point):
    """Get profile data for specific group and point"""
    try:
        data = get_profile_data(group_key, point)
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Profile data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve profile data'
        }), 500

@api_bp.route('/summary-data/<group_key>', methods=['GET'])
def get_summary_data_endpoint(group_key):
    """Get summary data for specific group"""
    try:
        data = get_summary_data(group_key)
        return jsonify({
            'success': True,
            'data': data,
            'message': 'Summary data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve summary data'
        }), 500

@api_bp.route('/measurements/search', methods=['GET'])
def search_measurements():
    """Search AFM measurements with real-time filtering"""
    try:
        # Get query parameters
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = max(int(request.args.get('offset', 0)), 0)
        
        # Search measurements
        result = afm_data_service.search_measurements(query=query, limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'total': result['total'],
            'limit': result['limit'],
            'offset': result['offset'],
            'query': result['query'],
            'has_more': result['has_more'],
            'message': f'Found {result["total"]} measurements'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to search measurements'
        }), 500

@api_bp.route('/measurements/suggestions', methods=['GET'])
def get_search_suggestions():
    """Get search suggestions for autocomplete"""
    try:
        query = request.args.get('q', '').strip()
        limit = min(int(request.args.get('limit', 10)), 20)  # Max 20 suggestions
        
        if len(query) < 2:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Query too short for suggestions'
            })
        
        suggestions = afm_data_service.get_quick_search_suggestions(query, limit)
        
        return jsonify({
            'success': True,
            'data': suggestions,
            'query': query,
            'message': f'Found {len(suggestions)} suggestions'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to get suggestions'
        }), 500

@api_bp.route('/measurements/<measurement_id>', methods=['GET'])
def get_measurement_details(measurement_id):
    """Get detailed information for a specific measurement"""
    try:
        measurement = afm_data_service.get_measurement_by_id(measurement_id)
        
        if measurement is None:
            return jsonify({
                'success': False,
                'error': 'Measurement not found',
                'message': f'No measurement found with ID: {measurement_id}'
            }), 404
        
        return jsonify({
            'success': True,
            'data': measurement,
            'message': 'Measurement details retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve measurement details'
        }), 500

@api_bp.route('/measurements/stats', methods=['GET'])
def get_measurement_statistics():
    """Get summary statistics for all measurements"""
    try:
        stats = afm_data_service.get_summary_stats()
        
        return jsonify({
            'success': True,
            'data': stats,
            'message': 'Statistics retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve statistics'
        }), 500

@api_bp.route('/measurements', methods=['GET'])
def get_all_measurements():
    """Get all measurements (with pagination)"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 results
        offset = max(int(request.args.get('offset', 0)), 0)
        
        # Get measurements
        result = afm_data_service.search_measurements(query="", limit=limit, offset=offset)
        
        return jsonify({
            'success': True,
            'data': result['data'],
            'total': result['total'],
            'limit': result['limit'],
            'offset': result['offset'],
            'has_more': result['has_more'],
            'message': 'Measurements retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve measurements'
        }), 500

@api_bp.route('/wafer-data/<group_key>', methods=['GET'])
def get_wafer_data_endpoint(group_key):
    """Get wafer heat map data for specific group"""
    try:
        # Generate dummy wafer data (this would normally come from database)
        import math
        import random
        
        wafer_data = []
        die_size = 10  # 10x10 mm die
        wafer_radius = 150  # 300mm wafer
        
        # Generate die positions in a circular wafer pattern
        for x in range(-wafer_radius, wafer_radius + 1, die_size):
            for y in range(-wafer_radius, wafer_radius + 1, die_size):
                distance = math.sqrt(x * x + y * y)
                
                # Only include die within the wafer radius
                if distance <= wafer_radius:
                    # Generate realistic AFM measurement values with some spatial correlation
                    base_value = 0.5 + 0.3 * math.sin(x / 30) * math.cos(y / 30)
                    noise = (random.random() - 0.5) * 0.2
                    edge_effect = max(0, (wafer_radius - distance) / wafer_radius) * 0.1
                    
                    z_value = base_value + noise + edge_effect
                    
                    wafer_data.append({
                        'x': round(x / die_size),  # Die coordinate
                        'y': round(y / die_size),  # Die coordinate
                        'z': z_value,
                        'realX': x,  # Real position in mm
                        'realY': y   # Real position in mm
                    })
        
        return jsonify({
            'success': True,
            'data': wafer_data,
            'group_key': group_key,
            'message': 'Wafer data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve wafer data'
        }), 500

@api_bp.route('/enhanced-profile-data/<group_key>/<int:die_x>/<int:die_y>', methods=['GET'])
def get_enhanced_profile_data_endpoint(group_key, die_x, die_y):
    """Get detailed profile data for specific die position"""
    try:
        import math
        import random
        
        profile_data = []
        points_per_axis = 50  # 50x50 measurement points per die
        die_size = 10000  # 10mm in microns
        step_size = die_size / points_per_axis
        
        # Base AFM profile with some surface roughness
        base_z = 0.5 + random.random() * 0.3
        
        for i in range(points_per_axis):
            for j in range(points_per_axis):
                x = i * step_size
                y = j * step_size
                
                # Generate realistic AFM surface profile
                surface_pattern = 0.1 * math.sin(x / 1000) * math.cos(y / 1000)
                roughness = (random.random() - 0.5) * 0.05
                gradient = (x + y) / die_size * 0.02
                
                z = base_z + surface_pattern + roughness + gradient
                
                profile_data.append({'x': x, 'y': y, 'z': z})
        
        return jsonify({
            'success': True,
            'data': profile_data,
            'group_key': group_key,
            'die_x': die_x,
            'die_y': die_y,
            'message': 'Enhanced profile data retrieved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve enhanced profile data'
        }), 500