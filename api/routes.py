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
        
        # Validate data structure - expect 'information', 'summary', 'data' keys
        if not isinstance(data, dict):
            return jsonify({
                'success': False,
                'error': 'Invalid pickle file format',
                'message': 'Pickle file does not contain dictionary structure',
                'tool': tool_name
            }), 400
        
        print(f"Pickle data keys: {list(data.keys())}")
        
        # Extract measurement information from 'info' key (dict)
        data_info = data.get('info', {})
        print(f"Measurement info keys: {list(data_info.keys()) if data_info else []}")
        
        # Extract data_summary from 'summary' key - already in the right format
        data_summary = data.get('summary', {})
        print(f"🔍 Raw data_summary type: {type(data_summary)}")
        print(f"🔍 Raw data_summary keys: {list(data_summary.keys()) if isinstance(data_summary, dict) else 'Not a dict'}")
        
        # Check if data_summary is already in records format (list of dicts)
        if isinstance(data_summary, list):
            summary_records = data_summary
            print(f"🔍 Summary already in records format: {len(summary_records)} records")
        elif isinstance(data_summary, dict):
            # If it's a dict, try to convert to records
            summary_records = []
            if 'Site' in data_summary and 'ITEM' in data_summary:
                # New format with columnar data
                num_rows = len(data_summary.get('Site', []))
                for i in range(num_rows):
                    record = {}
                    for key, values in data_summary.items():
                        if isinstance(values, list) and i < len(values):
                            record[key] = values[i]
                    if record:
                        summary_records.append(record)
            else:
                # Legacy format - convert each site's data
                for site, site_data in data_summary.items():
                    if isinstance(site_data, dict) and 'ITEM' in site_data:
                        items = site_data['ITEM']
                        for i, item in enumerate(items):
                            record = {'Site': site, 'ITEM': item}
                            for key, values in site_data.items():
                                if key != 'ITEM' and isinstance(values, list) and i < len(values):
                                    record[key] = values[i]
                            summary_records.append(record)
            print(f"🔍 Converted summary to {len(summary_records)} records")
        else:
            summary_records = []
            print(f"🔍 Summary data not in expected format")

        # Extract detailed data from 'data' key
        data_detail = data.get('data', {})
        
        # Check if data_detail is already in records format
        if isinstance(data_detail, list):
            detail_records = data_detail
            print(f"🔍 Detail already in records format: {len(detail_records)} records")
        elif isinstance(data_detail, dict):
            # Convert dict format to records
            detail_records = []
            for point_key, point_data in data_detail.items():
                if isinstance(point_data, dict) and 'Point No' in point_data:
                    point_numbers = point_data.get('Point No', [])
                    for i in range(len(point_numbers)):
                        record = {'measurement_point': point_key, 'index': i}
                        for key, values in point_data.items():
                            if isinstance(values, list) and i < len(values):
                                record[key] = values[i]
                        detail_records.append(record)
            print(f"🔍 Converted detail to {len(detail_records)} records")
        else:
            detail_records = []
            print(f"🔍 Detail data not in expected format")

        # Extract available measurement points
        available_points = []
        if summary_records and len(summary_records) > 0:
            # Get unique sites from records
            sites = set()
            for record in summary_records:
                if 'Site' in record:
                    sites.add(record['Site'])
            available_points = sorted(list(sites))
        elif isinstance(data_summary, dict):
            available_points = list(data_summary.keys())

        response_data = {
            'success': True,
            'data': {
                'filename': decoded_filename,
                'tool': tool_name,
                'pickle_filename': pickle_path.name,
                'information': data_info,      # Dict with measurement metadata
                'summary': summary_records,    # Summary data in records format
                'data': detail_records,        # Detail data in records format
                'available_points': available_points,  # List of measurement points
            },
            'message': f'Successfully loaded measurement data for {decoded_filename} from {tool_name}'
        }
        print(f"Successfully loaded pickle data with:")
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


@api_bp.route('/afm-files/profile/<path:filename>/<point_number>', methods=['GET'])
def get_profile_data(filename, point_number):
    """Get profile data (x,y,z) from profile_dir for a specific measurement point"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename
        decoded_filename = unquote(filename)
        print(f"=== Profile Data API Called for tool: {tool_name}, filename: '{decoded_filename}', point: '{point_number}' ===")
        
        # Find matching profile file using the utility function
        profile_path = get_profile_file_path_by_filename(decoded_filename, point_number, tool_name)
        
        if not profile_path:
            return jsonify({
                'success': False,
                'error': 'Profile file not found',
                'message': f'No profile file found for filename: {decoded_filename}, point: {point_number} in tool {tool_name}',
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
                'message': f'Successfully loaded profile data for {decoded_filename}, point {point_number} from {tool_name}'
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
            'message': f'Failed to get profile data for {decoded_filename}, point {point_number}'
        }), 500


@api_bp.route('/afm-files/image/<path:filename>/<point_number>', methods=['GET'])
def get_profile_image(filename, point_number):
    """Get profile image from tiff_dir for a specific measurement point"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename
        decoded_filename = unquote(filename)
        print(f"=== Profile Image API Called for tool: {tool_name}, filename: '{decoded_filename}', point: '{point_number}' ===")
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, point_number, tool_name)
        
        if not image_path:
            return jsonify({
                'success': False,
                'error': 'Image file not found',
                'message': f'No image file found for filename: {decoded_filename}, point: {point_number} in tool {tool_name}',
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
                'url': f'/api/afm-files/image-file/{decoded_filename}/{point_number}?tool={tool_name}'
            },
            'tool': tool_name,
            'message': f'Successfully found image for {decoded_filename}, point {point_number} from {tool_name}'
        })
        
    except Exception as e:
        print(f"Error in get_profile_image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to find image for {decoded_filename}, point {point_number}'
        }), 500

@api_bp.route('/afm-files/image-file/<path:filename>/<point_number>', methods=['GET'])
def serve_profile_image(filename, point_number):
    """Serve the actual image file"""
    try:
        tool_name = request.args.get('tool', 'MAP608')
        # URL decode the filename
        decoded_filename = unquote(filename)
        
        # Find matching image file using the utility function
        image_path = get_image_file_path_by_filename(decoded_filename, point_number, tool_name)
        
        if not image_path or not image_path.exists():
            return "Image file not found", 404
        
        return send_file(image_path, mimetype='image/webp')
        
    except Exception as e:
        print(f"Error serving image: {e}")
        return f"Error serving image: {str(e)}", 500