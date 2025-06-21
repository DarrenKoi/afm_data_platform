"""
AFM Data Platform API Routes
Consolidated routes for health, AFM files, and profile data
"""
import pickle
import re
from flask import Blueprint, jsonify, request, send_file
from pathlib import Path
from urllib.parse import unquote
from .utils.file_parser import (
    load_afm_file_list, 
    get_pickle_file_path_by_filename,
    get_profile_file_path_by_filename,
    get_image_file_path_by_filename,
)

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Health Check Routes
@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return jsonify({'status': 'API is healthy', 'service': 'AFM Data Platform API'})


# AFM Files Routes
@api_bp.route('/afm-files', methods=['GET'])
def get_afm_files():
    """Get parsed AFM file data for a specific tool"""
    try:
        # Get tool parameter from query string, default to MAP608
        tool_name = request.args.get('tool', 'MAP608')
        print(f"=== AFM Files API Called for tool: {tool_name} ===")
        
        # Load and parse the file list for the specified tool
        parsed_data = load_afm_file_list(tool_name)
        
        print(f"Returning {len(parsed_data)} measurements to frontend")
        
        # Print sample data for debugging
        if parsed_data:
            print("Sample measurement data:")
            print(f"  First item: {parsed_data[0]}")
            if len(parsed_data) > 1:
                print(f"  Last item: {parsed_data[-1]}")
        
        return jsonify({
            'success': True,
            'data': parsed_data,
            'total': len(parsed_data),
            'tool': tool_name,
            'message': f'Successfully loaded {len(parsed_data)} AFM measurements for {tool_name}'
        })
        
    except Exception as e:
        print(f"Error in get_afm_files: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to load AFM file data'
        }), 500


@api_bp.route('/afm-files/detail/<path:filename>', methods=['GET'])
def get_afm_file_detail(filename):
    """Get detailed AFM measurement data from pickle file for a specific tool"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename
        decoded_filename = unquote(filename)
        print(f"=== AFM Detail API Called for tool: {tool_name}, filename: '{decoded_filename}' ===")
        
        # Find matching pickle file using the utility function
        pickle_path = get_pickle_file_path_by_filename(decoded_filename, tool_name)
        
        if not pickle_path:
            return jsonify({
                'success': False,
                'error': 'Measurement file not found',
                'message': f'No pickle file found for filename: {decoded_filename} in tool {tool_name}',
                'tool': tool_name
            }), 404
        
        # Load pickle file
        print(f"Loading pickle file: {pickle_path}")
        
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
        
        # Extract measurement information from 'info' key (dict)
        data_info = data.get('info', {})
        
        # Extract summary data and convert to records using pandas if available
        data_summary = data.get('summary', {})
        if hasattr(data_summary, 'to_dict'):
            # It's a DataFrame
            summary_records = data_summary.to_dict('records')
        elif isinstance(data_summary, dict) and 'Site' in data_summary and 'ITEM' in data_summary:
            # Dict with columnar data - convert to records
            summary_records = []
            num_rows = len(data_summary.get('Site', []))
            for i in range(num_rows):
                record = {}
                for key, values in data_summary.items():
                    if isinstance(values, list) and i < len(values):
                        record[key] = values[i]
                if record:
                    summary_records.append(record)
        elif isinstance(data_summary, list):
            # Already in records format
            summary_records = data_summary
        else:
            summary_records = []
        
        # Extract detailed data and convert to records
        data_detail = data.get('data', {})
        if hasattr(data_detail, 'to_dict'):
            # It's a DataFrame
            detail_records = data_detail.to_dict('records')
        elif isinstance(data_detail, dict):
            # Dict with measurement points as keys
            detail_records = []
            for point_key, point_data in data_detail.items():
                if isinstance(point_data, dict) and any(isinstance(v, list) for v in point_data.values()):
                    # Convert columnar data to records
                    num_rows = max(len(v) for v in point_data.values() if isinstance(v, list))
                    for i in range(num_rows):
                        record = {'measurement_point': point_key}
                        for key, values in point_data.items():
                            if isinstance(values, list) and i < len(values):
                                record[key] = values[i]
                        detail_records.append(record)
        elif isinstance(data_detail, list):
            # Already in records format
            detail_records = data_detail
        else:
            detail_records = []
        
        # Extract available measurement points
        available_points = []
        if isinstance(data_detail, dict):
            # Get measurement points directly from data keys
            available_points = sorted(list(data_detail.keys()))
        elif summary_records:
            # Extract unique sites from summary records
            sites = {record.get('Site') for record in summary_records if 'Site' in record}
            available_points = sorted(list(sites))

        response_data = {
            'success': True,
            'data': {
                'filename': decoded_filename,
                'tool': tool_name,
                'pickle_filename': pickle_path.name,
                'information': data_info,
                'summary': summary_records,
                'data': detail_records,
                'available_points': available_points,
            },
            'message': f'Successfully loaded measurement data for {decoded_filename} from {tool_name}'
        }
        
        # Print sample data for debugging
        print(f"Successfully loaded pickle data:")
        print(f"  - Summary records: {len(summary_records)} items")
        if summary_records:
            print(f"  - Sample summary: {summary_records[0]}")
        print(f"  - Detail records: {len(detail_records)} items") 
        if detail_records:
            print(f"  - Sample detail: {detail_records[0]}")
        print(f"  - Available points: {available_points}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_afm_file_detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to load measurement detail for {decoded_filename}'
        }), 500


@api_bp.route('/afm-files/profile/<path:filename>/<path:decoded_point_number>', methods=['GET'])
def get_profile_data(filename, decoded_point_number):
    """Get profile data (x,y,z) from profile_dir for a specific measurement point"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename and point number
        decoded_filename = unquote(filename)
        decoded_point_number = unquote(decoded_point_number)
        print(f"=== Profile Data API Called for tool: {tool_name}, filename: '{decoded_filename}', point: '{decoded_point_number}' ===")
        
        # Find matching profile file using the utility function
        profile_path = get_profile_file_path_by_filename(decoded_filename, decoded_point_number, tool_name)
        
        if not profile_path:
            return jsonify({
                'success': False,
                'error': 'Profile file not found',
                'message': f'No profile file found for filename: {decoded_filename}, point: {decoded_point_number} in tool {tool_name}',
                'tool': tool_name
            }), 404
        
        # Check if file exists
        if not profile_path.exists():
            return jsonify({
                'success': False,
                'error': 'Profile file not accessible',
                'message': f'Profile file {profile_path.name} exists in listing but not accessible',
                'tool': tool_name
            }), 404
        
        # Load profile data from pickle file
        try:
            with open(profile_path, 'rb') as f:
                profile_data = pickle.load(f)
            
            # Profile data should be a list of dictionaries with x, y, z coordinates
            if not isinstance(profile_data, list):
                return jsonify({
                    'success': False,
                    'error': 'Invalid profile data format',
                    'message': f'Profile data should be a list, got {type(profile_data)}',
                    'tool': tool_name
                }), 400
            
            print(f"Successfully loaded {len(profile_data)} profile data points")
            
            return jsonify({
                'success': True,
                'data': profile_data,
                'count': len(profile_data),
                'tool': tool_name,
                'message': f'Successfully loaded profile data for {decoded_filename}, point {decoded_point_number} from {tool_name}'
            })
            
        except Exception as e:
            print(f"Error loading profile pickle file: {e}")
            return jsonify({
                'success': False,
                'error': 'Failed to load profile data',
                'message': f'Error reading profile file: {str(e)}',
                'tool': tool_name
            }), 500
        
    except Exception as e:
        print(f"Error in get_profile_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to get profile data for {decoded_filename}, point {decoded_point_number}'
        }), 500


@api_bp.route('/afm-files/image/<path:filename>/<path:decoded_point_number>', methods=['GET'])
def get_profile_image(filename, decoded_point_number):
    """Get profile image from tiff_dir for a specific measurement point"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename and point number
        decoded_filename = unquote(filename)
        decoded_point_number = unquote(decoded_point_number)
        print(f"=== Profile Image API Called for tool: {tool_name}, filename: '{decoded_filename}', point: '{decoded_point_number}' ===")
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, decoded_point_number, tool_name)
        
        if not image_path:
            return jsonify({
                'success': False,
                'error': 'Image file not found',
                'message': f'No image file found for filename: {decoded_filename}, point: {decoded_point_number} in tool {tool_name}',
                'tool': tool_name
            }), 404
        
        # Check if file exists
        if not image_path.exists():
            return jsonify({
                'success': False,
                'error': 'Image file not accessible',
                'message': f'Image file {image_path.name} exists in listing but not accessible',
                'tool': tool_name
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'filename': image_path.name,
                'path': str(image_path),
                'relative_path': f'tiff_dir/{image_path.name}',
                'url': f'/api/afm-files/image-file/{decoded_filename}/{decoded_point_number}?tool={tool_name}'
            },
            'tool': tool_name,
            'message': f'Successfully found image for {decoded_filename}, point {decoded_point_number} from {tool_name}'
        })
        
    except Exception as e:
        print(f"Error in get_profile_image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to find image for {decoded_filename}, point {decoded_point_number}'
        }), 500

@api_bp.route('/afm-files/image-file/<path:filename>/<path:point_number>', methods=['GET'])
def serve_profile_image(filename, point_number):
    """Serve the actual image file"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename and point number
        decoded_filename = unquote(filename)
        decoded_point_number = unquote(point_number)
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, decoded_point_number, tool_name)
        
        if not image_path or not image_path.exists():
            return "Image file not found", 404
        
        return send_file(image_path, mimetype='image/webp')
        
    except Exception as e:
        print(f"Error serving image: {e}")
        return f"Error serving image: {str(e)}", 500