"""
File parsing utilities using pathlib for cross-platform compatibility
"""
import re
from pathlib import Path
import pickle

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
    """Load AFM file list from pre-parsed pickle file, generate cache if not exists"""
    try:
        print(f"🔍 Loading AFM file list for tool: {tool_name}")
        
        # Use pathlib for cross-platform file paths
        parsed_pickle_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'data_dir_list_parsed.pkl'
        
        print(f"📂 Loading parsed file list from: {parsed_pickle_path}")
        
        if not parsed_pickle_path.exists():
            print(f"❌ Parsed pickle file not found: {parsed_pickle_path}")
            print("🔄 Generating cache file for future use...")
            # Parse and cache the data
            success = parse_and_cache_afm_data(tool_name)
            if success and parsed_pickle_path.exists():
                print("✅ Cache file generated successfully")
                # Now load from the newly created cache
                with open(parsed_pickle_path, 'rb') as f:
                    data = pickle.load(f)
                measurements = data.get('measurements', [])
                metadata = data.get('metadata', {})
                print(f"✅ Successfully loaded {len(measurements)} measurements from new cache")
                return measurements
            else:
                print("⚠️ Cache generation failed, using live parsing")
                return load_afm_file_list_live(tool_name)
        
        # Load the pre-parsed data from pickle file

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

                parsed_file = parse_filename(line)
                if parsed_file:
                    # Only include files that have corresponding pickle files
                    if check_pickle_file_exists(parsed_file, tool_name):

                        parsed_file['tool_name'] = tool_name
                        parsed_data.append(parsed_file)
                    else:
                        skipped_files.append(line)
        
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

        print(f"🔄 Starting parsing and caching for tool: {tool_name}")

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
                'generated_at': datetime.now().isoformat()
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
        
        # Handle different point_number formats
        # If point_number contains underscore (e.g., "1_UL"), use it as is
        # If it's just a number, we need to find the correct site suffix
        if '_' in str(point_number):
            # Already has site info (e.g., "1_UL")
            site_suffix = f"_{point_number}"
            # Extract just the number for formatting
            point_num = point_number.split('_')[0]
            formatted_point = f"{int(point_num):04d}"
        else:
            # Just a number, need to find the site suffix
            # Try common site suffixes
            site_suffixes = ['_UL', '_UR', '_LL', '_LR', '_C']
            for suffix in site_suffixes:
                test_point = f"{int(point_number):04d}"
                # Check if filename already ends with # to avoid double ##
                if filename_no_ext.endswith('#'):
                    test_filename = f"{filename_no_ext}_{point_number}{suffix}_{test_point}_Height.pkl"
                else:
                    test_filename = f"{filename_no_ext}#_{point_number}{suffix}_{test_point}_Height.pkl"
                test_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'profile_dir' / test_filename
                if test_path.exists():
                    print(f"✅ Found profile file with suffix {suffix}: {test_path}")
                    return test_path
            
            # If no file found with suffixes, try without site info (fallback)
            formatted_point = f"{int(point_number):04d}"
            site_suffix = ""
        
        # Construct profile file path
        # Format: base_filename#_1_UL_0001_Height.pkl
        # Check if filename already ends with # to avoid double ##
        if filename_no_ext.endswith('#'):
            profile_filename = f"{filename_no_ext}{site_suffix}_{formatted_point}_Height.pkl"
        else:
            profile_filename = f"{filename_no_ext}#{site_suffix}_{formatted_point}_Height.pkl"
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
        
        # Handle different point_number formats
        # If point_number contains underscore (e.g., "1_UL"), use it as is
        # If it's just a number, we need to find the correct site suffix
        if '_' in str(point_number):
            # Already has site info (e.g., "1_UL")
            site_suffix = f"_{point_number}"
            # Extract just the number for formatting
            point_num = point_number.split('_')[0]
            formatted_point = f"{int(point_num):04d}"
        else:
            # Just a number, need to find the site suffix
            # Try common site suffixes
            site_suffixes = ['_UL', '_UR', '_LL', '_LR', '_C']
            for suffix in site_suffixes:
                test_point = f"{int(point_number):04d}"
                # Check if filename already ends with # to avoid double ##
                if filename_no_ext.endswith('#'):
                    test_filename = f"{filename_no_ext}_{point_number}{suffix}_{test_point}_Height.webp"
                else:
                    test_filename = f"{filename_no_ext}#_{point_number}{suffix}_{test_point}_Height.webp"
                test_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'tiff_dir' / test_filename
                if test_path.exists():
                    print(f"✅ Found image file with suffix {suffix}: {test_path}")
                    return test_path
            
            # If no file found with suffixes, try without site info (fallback)
            formatted_point = f"{int(point_number):04d}"
            site_suffix = ""
        
        # Construct image file path
        # Format: base_filename#_1_UL_0001_Height.webp
        # Check if filename already ends with # to avoid double ##
        if filename_no_ext.endswith('#'):
            image_filename = f"{filename_no_ext}{site_suffix}_{formatted_point}_Height.webp"
        else:
            image_filename = f"{filename_no_ext}#{site_suffix}_{formatted_point}_Height.webp"
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