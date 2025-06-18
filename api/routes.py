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
    parse_filename
)
from .utils.data_converter import (
    convert_data_status_to_records,
    convert_data_detail_to_records
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
        information = data.get('info', {})
        print(f"Measurement info keys: {list(information.keys()) if information else []}")
        
        # Extract data_status from 'data_status' key and convert to DataFrame records format
        data_status = data.get('data_status', {})
        print(f"🔍 Raw data_status type: {type(data_status)}")
        print(f"🔍 Raw data_status keys: {list(data_status.keys()) if data_status else 'No data_status'}")
        if data_status:
            print(f"🔍 First data_status entry: {list(data_status.items())[0] if data_status else 'No entries'}")
        
        summary_dict = []
        if data_status:
            try:
                # Convert data_status structure to DataFrame records format
                # data_status format: {'1_UL': {'ITEM': [...], 'Left_H (nm)': [...], ...}}
                print(f"🔄 Converting data_status to records...")
                summary_dict = convert_data_status_to_records(data_status)
                print(f"✅ Converted data_status to {len(summary_dict)} summary records")
                print(f"📊 Sample summary record: {summary_dict[0] if summary_dict else 'No records'}")
            except Exception as e:
                print(f"❌ Error converting data_status: {e}")
                import traceback
                traceback.print_exc()
                summary_dict = []
        
        # Extract detailed data from 'data_detail' key and convert to records format
        data_detail = data.get('data_detail', {})
        data_dict = []
        if data_detail:
            try:
                # Convert data_detail structure to records format
                # data_detail format: {'1_UL': {'Point No': [...], 'X (um)': [...], ...}}
                data_dict = convert_data_detail_to_records(data_detail)
                print(f"Converted data_detail to {len(data_dict)} data records")
            except Exception as e:
                print(f"Error converting data_detail: {e}")
                data_dict = []
        
        # Extract available measurement points from data_status
        available_points = list(data_status.keys()) if data_status else []
        
        # Add profile data extraction from data_detail
        profile_data = []
        if data_detail:
            # Get first measurement point for profile visualization
            first_point_key = list(data_detail.keys())[0]
            first_point_data = data_detail[first_point_key]
            
            if 'Point No' in first_point_data and 'Left_H (nm)' in first_point_data:
                point_nos = first_point_data['Point No']
                height_values = first_point_data['Left_H (nm)']
                
                for i, (point_no, height) in enumerate(zip(point_nos, height_values)):
                    if i < 1000:  # Limit for performance
                        profile_data.append({
                            'x': i % 50,  # Create grid layout
                            'y': i // 50,
                            'z': float(height)
                        })
        
        response_data = {
            'success': True,
            'data': {
                'filename': decoded_filename,
                'tool': tool_name,
                'pickle_filename': pickle_path.name,
                'information': information,      # Dict with measurement metadata
                'summary': summary_dict,        # Converted from data_status to records format
                'data': data_dict,             # Converted from data_detail to records format
                'available_points': available_points,  # List of measurement points
                'profile_data': profile_data,   # Profile data for visualization
                'raw_data_status': data_status, # Original data_status structure for debugging
                'raw_data_detail': data_detail  # Original data_detail structure for debugging
            },
            'message': f'Successfully loaded measurement data for {decoded_filename} from {tool_name}'
        }
        
        print(f"Successfully loaded pickle data with:")
        print(f"  - Information fields: {list(information.keys()) if information else []}")
        print(f"  - Summary records: {len(summary_dict) if isinstance(summary_dict, list) else 'N/A'}")
        print(f"  - Data records: {len(data_dict) if isinstance(data_dict, list) else 'N/A'}")
        print(f"  - Profile points: {len(profile_data)}")
        
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

# Profile Data Routes
@api_bp.route('/afm-files/profile/<path:filename>/<point_number>', methods=['GET'])
def get_profile_data(filename, point_number):
    """Get profile data (x, y, z) from profile_dir for a specific measurement point"""
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
        
        # Load the profile file
        print(f"Loading profile file: {profile_path}")
        
        with open(profile_path, 'rb') as f:
            profile_data = pickle.load(f)
        
        print(f"Profile data type: {type(profile_data)}")
        print(f"Profile data keys: {list(profile_data.keys()) if isinstance(profile_data, dict) else 'Not a dict'}")
        
        # Process profile data to extract x, y, z coordinates
        processed_data = []
        
        if isinstance(profile_data, dict):
            # Look for common coordinate keys
            x_key = None
            y_key = None
            z_key = None
            
            # Find coordinate keys (case insensitive)
            for key in profile_data.keys():
                key_lower = key.lower()
                if 'x' in key_lower and not x_key:
                    x_key = key
                elif 'y' in key_lower and not y_key:
                    y_key = key
                elif any(z_name in key_lower for z_name in ['z', 'height', 'h']):
                    z_key = key
            
            print(f"Found coordinate keys: x={x_key}, y={y_key}, z={z_key}")
            
            if x_key and y_key:
                x_data = profile_data.get(x_key, [])
                y_data = profile_data.get(y_key, [])
                z_data = profile_data.get(z_key, []) if z_key else []
                
                # Ensure all arrays are the same length
                min_length = min(len(x_data), len(y_data))
                if z_data:
                    min_length = min(min_length, len(z_data))
                
                print(f"Data lengths: x={len(x_data)}, y={len(y_data)}, z={len(z_data) if z_data else 0}")
                print(f"Using min_length: {min_length}")
                
                for i in range(min_length):
                    point = {
                        'x': float(x_data[i]) if x_data[i] is not None else 0,
                        'y': float(y_data[i]) if y_data[i] is not None else 0
                    }
                    if z_data and i < len(z_data):
                        point['z'] = float(z_data[i]) if z_data[i] is not None else 0
                    
                    processed_data.append(point)
                
                print(f"✅ Processed {len(processed_data)} profile points")
                if processed_data:
                    print(f"Sample point: {processed_data[0]}")
            else:
                print(f"❌ Could not find x,y coordinate keys in profile data")
        
        return jsonify({
            'success': True,
            'data': processed_data,
            'total_points': len(processed_data),
            'tool': tool_name,
            'filename': profile_path.name,
            'message': f'Successfully loaded profile data for {decoded_filename}, point {point_number} from {tool_name}'
        })
        
    except Exception as e:
        print(f"Error in get_profile_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to load profile data for {decoded_filename}, point {point_number}'
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