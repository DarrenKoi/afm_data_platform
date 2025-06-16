import os
import re
import pickle
from flask import Blueprint, jsonify, request

api_bp = Blueprint('api', __name__)

def parse_filename(filename):
    """
    Parse AFM filename into structured data
    Pattern: #date#recipe_name#lot_id_time#slot_measured_info#.extension
    """
    try:
        print(f"Parsing filename: {filename}")
        
        # Remove extension
        filename_no_ext = filename.replace('.csv', '').replace('.pkl', '')
        
        # Split by # and remove empty parts
        parts = [part for part in filename_no_ext.split('#') if part]
        
        if len(parts) < 4:
            print(f"  -> Not enough parts: {parts}")
            return None
        
        # Extract components
        date = parts[0]  # e.g., "250609"
        recipe_name = parts[1]  # e.g., "FSOXCMP_DISHING_9PT"
        lot_time_part = parts[2]  # e.g., "T7HQR42TA_250709" or "T3HQR47TF[250814]"
        slot_info = parts[3]  # e.g., "21_1" or "07_repeat2"
        
        # Extract lot_id (remove time info)
        if '[' in lot_time_part:
            # Format: T3HQR47TF[250814]
            lot_id = lot_time_part.split('[')[0]
        elif '_' in lot_time_part:
            # Format: T7HQR42TA_250709
            lot_id = lot_time_part.split('_')[0]
        else:
            lot_id = lot_time_part
        
        # Parse slot and measured info
        slot_parts = slot_info.split('_')
        slot_number = slot_parts[0]
        measured_info = '_'.join(slot_parts[1:]) if len(slot_parts) > 1 else "standard"
        
        # Format date to readable format
        try:
            year = "20" + date[:2]
            month = date[2:4]
            day = date[4:6]
            formatted_date = f"{year}-{month}-{day}"
        except:
            formatted_date = date
        
        parsed_data = {
            'filename': filename,
            'date': date,
            'formatted_date': formatted_date,
            'recipe_name': recipe_name,
            'lot_id': lot_id,
            'slot_number': slot_number,
            'measured_info': measured_info
        }
        
        print(f"  -> Parsed: {parsed_data}")
        return parsed_data
        
    except Exception as e:
        print(f"  -> Error parsing {filename}: {e}")
        return None

def load_afm_file_list():
    """Load and parse all files from data_dir_list.txt"""
    try:
        data_list_path = os.path.join(
            'itc-afm-data-platform-pjt-shared', 
            'AFM_DB', 
            'MAP608', 
            'data_dir_list.txt'
        )
        
        print(f"Loading file list from: {data_list_path}")
        
        if not os.path.exists(data_list_path):
            print(f"File not found: {data_list_path}")
            return []
        
        parsed_data = []
        
        with open(data_list_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                
                # Remove line numbers if present (e.g., "   123→")
                if '→' in line:
                    filename = line.split('→')[1].strip()
                else:
                    filename = line
                
                parsed_file = parse_filename(filename)
                if parsed_file:
                    parsed_file['id'] = line_num
                    parsed_data.append(parsed_file)
        
        print(f"Successfully loaded {len(parsed_data)} measurements")
        return parsed_data
        
    except Exception as e:
        print(f"Error loading file list: {e}")
        return []

@api_bp.route('/health', methods=['GET'])
def health():
    """API health check"""
    return jsonify({'status': 'API is healthy', 'service': 'AFM Data Platform API'})

@api_bp.route('/afm-files', methods=['GET'])
def get_afm_files():
    """Get parsed AFM file data"""
    try:
        print("=== AFM Files API Called ===")
        
        # Load and parse the file list
        parsed_data = load_afm_file_list()
        
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
            'message': f'Successfully loaded {len(parsed_data)} AFM measurements'
        })
        
    except Exception as e:
        print(f"Error in get_afm_files: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to load AFM file data'
        }), 500

@api_bp.route('/afm-files/search', methods=['GET'])
def search_afm_files():
    """Search AFM files"""
    try:
        query = request.args.get('q', '').strip().lower()
        print(f"=== AFM Files Search API Called with query: '{query}' ===")
        
        # Load and parse the file list
        parsed_data = load_afm_file_list()
        
        # Filter data if query provided
        if query:
            filtered_data = []
            for item in parsed_data:
                # Search only in date, recipe name, and lot id
                searchable_text = ' '.join([
                    item.get('lot_id', ''),
                    item.get('recipe_name', ''),
                    item.get('date', ''),
                    item.get('formatted_date', '')
                ]).lower()
                
                if query in searchable_text:
                    filtered_data.append(item)
                    
            print(f"Search '{query}' found {len(filtered_data)} results")
        else:
            filtered_data = parsed_data
            print(f"No query provided, returning all {len(filtered_data)} results")
        
        return jsonify({
            'success': True,
            'data': filtered_data,
            'total': len(filtered_data),
            'query': query,
            'message': f'Found {len(filtered_data)} measurements'
        })
        
    except Exception as e:
        print(f"Error in search_afm_files: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to search AFM files'
        }), 500

@api_bp.route('/afm-files/detail/<group_key>', methods=['GET'])
def get_afm_file_detail(group_key):
    """Get detailed AFM measurement data from pickle file"""
    try:
        print(f"=== AFM Detail API Called for group_key: '{group_key}' ===")
        
        # Parse group_key to find the corresponding pickle file
        # group_key format: lot_id_slot_measured_info (e.g., T7HQR42TA_21_1)
        parts = group_key.split('_')
        if len(parts) < 3:
            return jsonify({
                'success': False,
                'error': 'Invalid group_key format',
                'message': 'group_key should be in format: lot_id_slot_measured_info'
            }), 400
        
        lot_id = parts[0]
        slot_number = parts[1]
        measured_info = '_'.join(parts[2:])
        
        print(f"Parsed: lot_id={lot_id}, slot={slot_number}, measured_info={measured_info}")
        
        # Find matching pickle file
        data_dir = os.path.join(
            'itc-afm-data-platform-pjt-shared',
            'AFM_DB',
            'MAP608',
            'data_dir'
        )
        
        if not os.path.exists(data_dir):
            return jsonify({
                'success': False,
                'error': 'Data directory not found',
                'message': f'Data directory {data_dir} does not exist'
            }), 404
        
        # Find matching pickle file
        matching_file = None
        for filename in os.listdir(data_dir):
            if filename.endswith('.pkl'):
                parsed = parse_filename(filename)
                if (parsed and 
                    parsed['lot_id'] == lot_id and 
                    parsed['slot_number'] == slot_number and 
                    parsed['measured_info'] == measured_info):
                    matching_file = filename
                    break
        
        if not matching_file:
            return jsonify({
                'success': False,
                'error': 'Measurement file not found',
                'message': f'No pickle file found for group_key: {group_key}'
            }), 404
        
        # Load pickle file
        pickle_path = os.path.join(data_dir, matching_file)
        print(f"Loading pickle file: {pickle_path}")
        
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
        
        # Validate data structure
        if not isinstance(data, dict) or 'info' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid pickle file format',
                'message': 'Pickle file does not contain expected data structure'
            }), 400
        
        # Extract measurement info
        measurement_info = data.get('info', {})
        
        # Extract statistical data (data_status)
        data_status = data.get('data_status', {})
        
        # Process data_status into table format for frontend
        statistics_table = []
        if data_status:
            # Get all unique measurement points (keys like '1_UL', '2_UL', etc.)
            measurement_points = list(data_status.keys())
            
            # Get all statistical items from the first point to determine structure
            if measurement_points:
                first_point_data = data_status[measurement_points[0]]
                if 'ITEM' in first_point_data:
                    stat_items = first_point_data['ITEM']
                    
                    # Get all measurement parameters (excluding 'ITEM')
                    parameters = [key for key in first_point_data.keys() if key != 'ITEM']
                    
                    # Create table rows for each statistic
                    for i, stat_name in enumerate(stat_items):
                        row = {'statistic': stat_name}
                        
                        # Add values for each parameter
                        for param in parameters:
                            # Initialize parameter columns if not exists
                            if param not in row:
                                row[param] = {}
                            
                            # Add values for each measurement point
                            for point in measurement_points:
                                if param in data_status[point] and len(data_status[point][param]) > i:
                                    row[param][point] = data_status[point][param][i]
                        
                        statistics_table.append(row)
        
        # Extract detailed measurement data
        data_detail = data.get('data_detail', {})
        
        # Process first measurement point for profile data
        profile_data = []
        if data_detail:
            first_point = list(data_detail.keys())[0]
            point_data = data_detail[first_point]
            
            # Convert to profile format expected by frontend
            if 'Point No' in point_data:
                point_numbers = point_data['Point No']
                
                # Get the first measurement parameter (excluding Point No)
                measurement_params = [key for key in point_data.keys() if key != 'Point No']
                if measurement_params:
                    first_param = measurement_params[0]
                    values = point_data[first_param]
                    
                    for i, point_no in enumerate(point_numbers):
                        if i < len(values):
                            profile_data.append({
                                'x': i,  # index
                                'y': point_no,  # point number
                                'z': float(values[i])  # measurement value
                            })
        
        response_data = {
            'success': True,
            'data': {
                'group_key': group_key,
                'filename': matching_file,
                'measurement_info': measurement_info,
                'statistics_table': statistics_table,
                'profile_data': profile_data,
                'available_points': list(data_detail.keys()) if data_detail else [],
                'data_status': data_status,  # Raw data for backwards compatibility
                'data_detail': data_detail   # Raw data for backwards compatibility
            },
            'message': f'Successfully loaded measurement data for {group_key}'
        }
        
        print(f"Successfully loaded pickle data: {len(profile_data)} profile points")
        print(f"Available measurement points: {list(data_detail.keys()) if data_detail else []}")
        print(f"Statistics table rows: {len(statistics_table)}")
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error in get_afm_file_detail: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f'Failed to load measurement detail for {group_key}'
        }), 500