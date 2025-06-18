"""
File parsing utilities using pathlib for cross-platform compatibility
"""
import re
from pathlib import Path


def parse_filename(filename):
    """
    Parse AFM filename into structured data
    Pattern: #date#recipe_name#lot_id_time#slot_measured_info#.extension
    """
    try:
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


def check_pickle_file_exists(parsed_file, tool_name='MAP608'):
    """Check if a pickle file exists for the given parsed file data"""
    try:
        # Define the pickle directory path using pathlib
        pickle_dir = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_pickle'
        
        if not pickle_dir.exists():
            return False
        
        # Get all pickle files in the directory
        pickle_files = [f.name for f in pickle_dir.glob('*.pkl')]
        
        # Check if any pickle file matches this parsed file
        target_lot_id = parsed_file['lot_id']
        target_slot = parsed_file['slot_number']
        target_measured_info = parsed_file['measured_info']
        target_recipe = parsed_file['recipe_name']
        
        for pickle_file in pickle_files:
            # Parse the pickle filename to check if it matches
            pickle_parsed = parse_filename(pickle_file)
            if (pickle_parsed and 
                pickle_parsed['lot_id'] == target_lot_id and
                pickle_parsed['slot_number'] == target_slot and
                pickle_parsed['measured_info'] == target_measured_info and
                pickle_parsed['recipe_name'] == target_recipe):
                
                return True
        
        return False
        
    except Exception as e:
        print(f"Error checking pickle file existence: {e}")
        return False


def load_afm_file_list(tool_name='MAP608'):
    """Load AFM file list from pre-parsed pickle file"""
    try:
        print(f"🔍 Loading AFM file list for tool: {tool_name}")
        
        # Use pathlib for cross-platform file paths
        parsed_pickle_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_list_parsed.pkl'
        
        print(f"📂 Loading parsed file list from: {parsed_pickle_path}")
        
        if not parsed_pickle_path.exists():
            print(f"❌ Parsed pickle file not found: {parsed_pickle_path}")
            print("📝 Falling back to live parsing...")
            return load_afm_file_list_live(tool_name)
        
        # Load the pre-parsed data from pickle file
        import pickle
        with open(parsed_pickle_path, 'rb') as f:
            data = pickle.load(f)
        
        measurements = data.get('measurements', [])
        metadata = data.get('metadata', {})
        
        print(f"✅ Successfully loaded {len(measurements)} measurements from cache")
        print(f"📊 Cache generated at: {metadata.get('generated_at', 'Unknown')}")
        print(f"🔧 Total processed: {metadata.get('total_files_processed', 'Unknown')}")
        
        return measurements
        
    except Exception as e:
        print(f"❌ Error loading cached file list: {e}")
        print("📝 Falling back to live parsing...")
        import traceback
        traceback.print_exc()
        return load_afm_file_list_live(tool_name)


def load_afm_file_list_live(tool_name='MAP608'):
    """Load AFM file list by parsing data_dir_list.txt (fallback method)"""
    try:
        print(f"🔍 Live parsing AFM file list for tool: {tool_name}")
        
        # Use pathlib for cross-platform file paths
        data_list_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_list.txt'
        pickle_dir = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_pickle'
        
        print(f"📂 Loading file list from: {data_list_path}")
        print(f"🗂️ Checking pickle files in: {pickle_dir}")
        
        if not data_list_path.exists():
            print(f"❌ File not found: {data_list_path}")
            return []
            
        if not pickle_dir.exists():
            print(f"❌ Pickle directory not found: {pickle_dir}")
            return []
        
        parsed_data = []
        skipped_files = []
        
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
                    # Only include files that have corresponding pickle files
                    if check_pickle_file_exists(parsed_file, tool_name):
                        parsed_file['id'] = line_num
                        parsed_file['tool_name'] = tool_name
                        parsed_data.append(parsed_file)
                    else:
                        skipped_files.append(filename)
        
        print(f"✅ Successfully loaded {len(parsed_data)} measurements (with pickle files)")
        print(f"📊 Skipped {len(skipped_files)} measurements (no pickle files)")
        if skipped_files:
            print(f"📄 Sample skipped files: {skipped_files[:5]}")
        
        return parsed_data
        
    except Exception as e:
        print(f"❌ Error loading file list: {e}")
        import traceback
        traceback.print_exc()
        return []


def parse_and_cache_afm_data(tool_name='MAP608'):
    """Parse AFM data from data_dir_list.txt and save to persistent cache file"""
    try:
        from datetime import datetime
        import pickle

        print(f"🔄 Starting scheduled parsing and caching for tool: {tool_name}")

        # Parse the data using the live parsing function
        measurements = load_afm_file_list_live(tool_name)

        if not measurements:
            print(f"❌ No measurements found for {tool_name}")
            return False

        # Prepare cache data structure
        cache_data = {
            'measurements': measurements,
            'metadata': {
                'tool_name': tool_name,
                'total_files_processed': len(measurements),
                'generated_at': datetime.now().isoformat(),
                'cache_version': '1.0'
            }
        }

        # Save to cache file
        cache_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_list_parsed.pkl'

        # Ensure directory exists
        cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(cache_path, 'wb') as f:
            pickle.dump(cache_data, f)

        print(f"✅ Successfully cached {len(measurements)} measurements to {cache_path}")
        print(f"📊 Cache file size: {cache_path.stat().st_size / 1024:.2f} KB")

        return True

    except Exception as e:
        print(f"❌ Error parsing and caching AFM data: {e}")
        import traceback
        traceback.print_exc()
        return False


def search_afm_files(query, tool_name='MAP608'):
    """Search AFM files using the cached parsed data"""
    try:
        print(f"🔍 Searching AFM files for query: '{query}' in tool: {tool_name}")
        
        # Load all measurements from cache
        measurements = load_afm_file_list(tool_name)
        if not measurements:
            return []
        
        if not query or not query.strip():
            return measurements
        
        query = query.lower().strip()
        filtered_results = []
        
        for measurement in measurements:
            # Search in multiple fields
            searchable_fields = [
                measurement.get('lot_id', ''),
                measurement.get('recipe_name', ''),
                measurement.get('measured_info', ''),
                measurement.get('formatted_date', ''),
                measurement.get('slot_number', ''),
                measurement.get('filename', '')
            ]
            
            # Check if query matches any field
            for field in searchable_fields:
                if query in str(field).lower():
                    filtered_results.append(measurement)
                    break
        
        print(f"📊 Search returned {len(filtered_results)} results for query: '{query}'")
        return filtered_results
        
    except Exception as e:
        print(f"❌ Error searching AFM files: {e}")
        import traceback
        traceback.print_exc()
        return []


def find_pickle_file_path(group_key, tool_name='MAP608'):
    """Find the exact pickle file path for a given group key"""
    try:
        # Parse group_key to find the corresponding pickle file
        # group_key format: lot_id_slot_measured_info (e.g., T7HQR42TA_21_1)
        parts = group_key.split('_')
        if len(parts) < 3:
            return None
        
        lot_id = parts[0]
        slot_number = parts[1]
        measured_info = '_'.join(parts[2:])
        
        # Find matching pickle file in the pickle directory
        data_dir = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_pickle'
        
        if not data_dir.exists():
            return None
        
        # Find matching pickle file
        pickle_files = list(data_dir.glob('*.pkl'))
        
        for pickle_file in pickle_files:
            parsed = parse_filename(pickle_file.name)
            if (parsed and 
                parsed['lot_id'] == lot_id and 
                parsed['slot_number'] == slot_number and 
                parsed['measured_info'] == measured_info):
                return pickle_file
        
        return None
        
    except Exception as e:
        print(f"Error finding pickle file path: {e}")
        return None


def find_profile_file_path(group_key, point_number, tool_name='MAP608'):
    """Find the exact profile file path for a given group key and point number"""
    try:
        # Parse group_key to find the corresponding profile file
        parts = group_key.split('_')
        if len(parts) < 3:
            return None
        
        lot_id = parts[0]
        slot_number = parts[1]
        measured_info = '_'.join(parts[2:])
        
        # Find matching profile file in the profile directory
        profile_dir = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'profile_dir'
        
        if not profile_dir.exists():
            return None
        
        # Find matching profile file
        # Expected format: #date#recipe#lot_id_time#slot_measured_info#_point_Height.pkl
        profile_files = list(profile_dir.glob('*.pkl'))
        
        for profile_file in profile_files:
            filename = profile_file.name
            parsed = parse_filename(filename.replace('_Height.pkl', '.pkl'))
            if (parsed and 
                parsed['lot_id'] == lot_id and 
                parsed['slot_number'] == slot_number and 
                parsed['measured_info'] == measured_info):
                
                # Extract point number from filename
                # Format: ...#_0001_Height.pkl, ...#_0002_Height.pkl, etc.
                point_match = re.search(r'#_(\d+)_Height\.pkl$', filename)
                if point_match:
                    file_point = point_match.group(1)
                    # Convert point_number to same format (pad with zeros)
                    formatted_point = f"{int(point_number):04d}"
                    if file_point == formatted_point:
                        return profile_file
        
        return None
        
    except Exception as e:
        print(f"Error finding profile file path: {e}")
        return None


def find_image_file_path(group_key, point_number, tool_name='MAP608'):
    """Find the exact image file path for a given group key and point number"""
    try:
        # Parse group_key to find the corresponding image file
        parts = group_key.split('_')
        if len(parts) < 3:
            return None
        
        lot_id = parts[0]
        slot_number = parts[1]
        measured_info = '_'.join(parts[2:])
        
        # Find matching image file in the tiff directory
        tiff_dir = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'tiff_dir'
        
        if not tiff_dir.exists():
            return None
        
        # Find matching image file
        # Expected format: #date#recipe#lot_id_time#slot_measured_info#_point_Height.webp
        image_files = list(tiff_dir.glob('*.webp'))
        
        for image_file in image_files:
            filename = image_file.name
            parsed = parse_filename(filename.replace('_Height.webp', '.pkl'))
            if (parsed and 
                parsed['lot_id'] == lot_id and 
                parsed['slot_number'] == slot_number and 
                parsed['measured_info'] == measured_info):
                
                # Extract point number from filename
                # Format: ...#_0001_Height.webp, ...#_0002_Height.webp, etc.
                point_match = re.search(r'#_(\d+)_Height\.webp$', filename)
                if point_match:
                    file_point = point_match.group(1)
                    # Convert point_number to same format (pad with zeros)
                    formatted_point = f"{int(point_number):04d}"
                    if file_point == formatted_point:
                        return image_file
        
        return None
        
    except Exception as e:
        print(f"Error finding image file path: {e}")
        return None


def get_pickle_file_path_by_filename(base_filename, tool_name='MAP608'):
    """Get the pickle file path directly from base filename by changing directory and extension"""
    try:
        # Remove extension from base filename if present
        filename_no_ext = base_filename.replace('.csv', '').replace('.pkl', '')
        
        # Construct pickle file path
        pickle_filename = filename_no_ext + '.pkl'
        pickle_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_pickle' / pickle_filename
        
        print(f"🔍 Looking for pickle file: {pickle_path}")
        
        if pickle_path.exists():
            print(f"✅ Found pickle file: {pickle_path}")
            return pickle_path
        else:
            print(f"❌ Pickle file not found: {pickle_path}")
            return None
            
    except Exception as e:
        print(f"Error getting pickle file path: {e}")
        return None


def get_profile_file_path_by_filename(base_filename, point_number, tool_name='MAP608'):
    """Get the profile file path directly from base filename by changing directory and adding point suffix"""
    try:
        # Remove extension from base filename if present
        filename_no_ext = base_filename.replace('.csv', '').replace('.pkl', '')
        
        # Format point number with padding
        formatted_point = f"{int(point_number):04d}"
        
        # Construct profile file path
        # Format: base_filename#_0001_Height.pkl
        profile_filename = f"{filename_no_ext}#_{formatted_point}_Height.pkl"
        profile_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'profile_dir' / profile_filename
        
        print(f"🔍 Looking for profile file: {profile_path}")
        
        if profile_path.exists():
            print(f"✅ Found profile file: {profile_path}")
            return profile_path
        else:
            print(f"❌ Profile file not found: {profile_path}")
            return None
            
    except Exception as e:
        print(f"Error getting profile file path: {e}")
        return None


def get_image_file_path_by_filename(base_filename, point_number, tool_name='MAP608'):
    """Get the image file path directly from base filename by changing directory and adding point suffix"""
    try:
        # Remove extension from base filename if present
        filename_no_ext = base_filename.replace('.csv', '').replace('.pkl', '')
        
        # Format point number with padding
        formatted_point = f"{int(point_number):04d}"
        
        # Construct image file path
        # Format: base_filename#_0001_Height.webp
        image_filename = f"{filename_no_ext}#_{formatted_point}_Height.webp"
        image_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'tiff_dir' / image_filename
        
        print(f"🔍 Looking for image file: {image_path}")
        
        if image_path.exists():
            print(f"✅ Found image file: {image_path}")
            return image_path
        else:
            print(f"❌ Image file not found: {image_path}")
            return None
            
    except Exception as e:
        print(f"Error getting image file path: {e}")
        return None