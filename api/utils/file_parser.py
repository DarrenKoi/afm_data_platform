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


def get_site_mapping_from_pickle(base_filename, tool_name='MAP608'):
    """Get site mapping from pickle file summary data"""
    try:
        pickle_path = get_pickle_file_path_by_filename(base_filename, tool_name)
        if not pickle_path or not pickle_path.exists():
            return {}
        
        with open(pickle_path, 'rb') as f:
            data = pickle.load(f)
        
        # Extract summary data
        data_summary = data.get('summary', {})
        site_mapping = {}
        
        if hasattr(data_summary, 'to_dict'):
            # It's a DataFrame
            summary_records = data_summary.to_dict('records')
        elif isinstance(data_summary, dict) and 'Site' in data_summary:
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
            summary_records = data_summary
        else:
            return {}
        
        # Build site mapping: point_number -> full_site_info
        for record in summary_records:
            if 'Site' in record and record['Site']:
                site_info = str(record['Site'])
                if '_' in site_info:
                    # Extract point number from site info (e.g., "1_UL" -> 1)
                    point_num = site_info.split('_')[0]
                    try:
                        site_mapping[int(point_num)] = site_info
                    except ValueError:
                        continue
        
        print(f"🗺️ Site mapping extracted: {site_mapping}")
        return site_mapping
        
    except Exception as e:
        print(f"Error extracting site mapping: {e}")
        return {}


def get_profile_file_path_by_filename(base_filename, site_id_param, tool_name='MAP608', site_info=None):
    """Get the profile file path using comprehensive filename pattern matching"""
    try:
        print(f"\n=== PROFILE FILE REQUEST ===")
        print(f"📂 Base filename (before encoding): {base_filename}")
        print(f"🎯 Site ID parameter: {site_id_param}")
        print(f"🔧 Tool name: {tool_name}")
        print(f"📍 Complete site info: {site_info}")
        
        # Remove extension from base filename if present
        filename_no_ext = base_filename.replace('.csv', '').replace('.pkl', '')
        print(f"🧹 Cleaned filename: {filename_no_ext}")
        
        # Extract information from site_info or fallback to site_id_param
        if site_info and site_info.get('point_no') is not None:
            point_no = site_info['point_no']  # Already integer from Flask route
            actual_site_id = site_info.get('site_id', site_id_param)  # String
            site_x = site_info.get('site_x')  # String (could be like '-1578.2')
            site_y = site_info.get('site_y')  # String (could be like '-310.6')
        else:
            # Fallback: extract point number from site_id_param (e.g., '1_UL' -> 1)
            try:
                if '_' in str(site_id_param):
                    point_no = int(site_id_param.split('_')[0])
                else:
                    point_no = int(site_id_param)
                actual_site_id = site_id_param
                site_x = None
                site_y = None
            except (ValueError, TypeError):
                point_no = 1
                actual_site_id = site_id_param
                site_x = None
                site_y = None
        
        point_no_4digit = f"{point_no:04d}"
        
        print(f"🎯 Site ID: '{actual_site_id}' (type: {type(actual_site_id)})")
        print(f"🔢 Point No: {point_no} -> 4-digit: {point_no_4digit}")
        print(f"📍 Site X: '{site_x}' (type: {type(site_x)}), Site Y: '{site_y}' (type: {type(site_y)})")
        
        # Build filename patterns based on site information
        patterns_to_try = []
        
        # Pattern 1: With Site_ID, Site_X, Site_Y, Point_No (most specific)
        if site_x is not None and site_y is not None:
            pattern = f"_{actual_site_id}_{site_x}_{site_y}_{point_no_4digit}_Height.pkl"
            patterns_to_try.append((pattern, "Site_ID + Site_X + Site_Y + Point_No"))
        
        # Pattern 2: With Site_ID and Point_No (actual_site_id like '1_UL')
        if actual_site_id:
            pattern = f"_{actual_site_id}_{point_no_4digit}_Height.pkl"
            patterns_to_try.append((pattern, "Site_ID + Point_No"))
        
        # Pattern 3: Just Point_No (no Site_ID)
        pattern = f"_{point_no_4digit}_Height.pkl"
        patterns_to_try.append((pattern, "Point_No only"))
        
        # Pattern 4: Try extracting position from Site_ID and combining with point number
        if '_' in str(actual_site_id):
            try:
                site_num, position = str(actual_site_id).split('_', 1)
                pattern = f"_{site_num}_{position}_{point_no_4digit}_Height.pkl"
                patterns_to_try.append((pattern, f"Site_Num + Position + Point_No"))
            except ValueError:
                pass
        
        # Pattern 5: Try with common position codes if Site_ID doesn't have position
        if '_' not in str(actual_site_id):
            position_codes = ['UL', 'UR', 'LL', 'LR', 'C']
            for position in position_codes:
                pattern = f"_{actual_site_id}_{position}_{point_no_4digit}_Height.pkl"
                patterns_to_try.append((pattern, f"Site_ID + {position} + Point_No"))
        
        print(f"\n🔍 TRYING {len(patterns_to_try)} FILENAME PATTERNS:")
        
        # Try each pattern
        for i, (pattern, description) in enumerate(patterns_to_try, 1):
            # Handle filename ending with # or not
            if filename_no_ext.endswith('#'):
                test_filename = f"{filename_no_ext}{pattern}"
            else:
                test_filename = f"{filename_no_ext}#{pattern}"
            
            test_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'profile_dir' / test_filename
            
            print(f"  {i}. Pattern: {description}")
            print(f"     Filename: {test_filename}")
            print(f"     Path: {test_path}")
            
            if test_path.exists():
                print(f"     ✅ FOUND!")
                print(f"\n=== PROFILE FILE MATCHED ===")
                print(f"📄 Final filename: {test_filename}")
                print(f"📂 Full path: {test_path}")
                return test_path
            else:
                print(f"     ❌ Not found")
        
        print(f"\n❌ NO PROFILE FILE FOUND after trying {len(patterns_to_try)} patterns")
        print(f"Summary:")
        print(f"  Site ID: {actual_site_id}")
        print(f"  Point No: {point_no} (4-digit: {point_no_4digit})")
        print(f"  Site coordinates: X={site_x}, Y={site_y}")
        return None
            
    except Exception as e:
        print(f"❌ Error getting profile file path: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_image_file_path_by_filename(base_filename, site_id_param, tool_name='MAP608', site_info=None):
    """Get the image file path using comprehensive filename pattern matching"""
    try:
        print(f"\n=== IMAGE FILE REQUEST ===")
        print(f"📂 Base filename (before encoding): {base_filename}")
        print(f"🎯 Site ID parameter: {site_id_param}")
        print(f"🔧 Tool name: {tool_name}")
        print(f"📍 Complete site info: {site_info}")
        
        # Remove extension from base filename if present
        filename_no_ext = base_filename.replace('.csv', '').replace('.pkl', '')
        print(f"🧹 Cleaned filename: {filename_no_ext}")
        
        # Extract information from site_info or fallback to site_id_param
        if site_info and site_info.get('point_no') is not None:
            point_no = site_info['point_no']  # Already integer from Flask route
            actual_site_id = site_info.get('site_id', site_id_param)  # String
            site_x = site_info.get('site_x')  # String (could be like '-1578.2')
            site_y = site_info.get('site_y')  # String (could be like '-310.6')
        else:
            # Fallback: extract point number from site_id_param (e.g., '1_UL' -> 1)
            try:
                if '_' in str(site_id_param):
                    point_no = int(site_id_param.split('_')[0])
                else:
                    point_no = int(site_id_param)
                actual_site_id = site_id_param
                site_x = None
                site_y = None
            except (ValueError, TypeError):
                point_no = 1
                actual_site_id = site_id_param
                site_x = None
                site_y = None
        
        point_no_4digit = f"{point_no:04d}"
        
        print(f"🎯 Site ID: '{actual_site_id}' (type: {type(actual_site_id)})")
        print(f"🔢 Point No: {point_no} -> 4-digit: {point_no_4digit}")
        print(f"📍 Site X: '{site_x}' (type: {type(site_x)}), Site Y: '{site_y}' (type: {type(site_y)})")
        
        # Build filename patterns based on site information
        patterns_to_try = []
        
        # Pattern 1: With Site_ID, Site_X, Site_Y, Point_No (most specific)
        if site_x is not None and site_y is not None:
            pattern = f"_{actual_site_id}_{site_x}_{site_y}_{point_no_4digit}_Height.webp"
            patterns_to_try.append((pattern, "Site_ID + Site_X + Site_Y + Point_No"))
        
        # Pattern 2: With Site_ID and Point_No (actual_site_id like '1_UL')
        if actual_site_id:
            pattern = f"_{actual_site_id}_{point_no_4digit}_Height.webp"
            patterns_to_try.append((pattern, "Site_ID + Point_No"))
        
        # Pattern 3: Just Point_No (no Site_ID)
        pattern = f"_{point_no_4digit}_Height.webp"
        patterns_to_try.append((pattern, "Point_No only"))
        
        # Pattern 4: Try extracting position from Site_ID and combining with point number
        if '_' in str(actual_site_id):
            try:
                site_num, position = str(actual_site_id).split('_', 1)
                pattern = f"_{site_num}_{position}_{point_no_4digit}_Height.webp"
                patterns_to_try.append((pattern, f"Site_Num + Position + Point_No"))
            except ValueError:
                pass
        
        # Pattern 5: Try with common position codes if Site_ID doesn't have position
        if '_' not in str(actual_site_id):
            position_codes = ['UL', 'UR', 'LL', 'LR', 'C']
            for position in position_codes:
                pattern = f"_{actual_site_id}_{position}_{point_no_4digit}_Height.webp"
                patterns_to_try.append((pattern, f"Site_ID + {position} + Point_No"))
        
        print(f"\n🔍 TRYING {len(patterns_to_try)} FILENAME PATTERNS:")
        
        # Try each pattern
        for i, (pattern, description) in enumerate(patterns_to_try, 1):
            # Handle filename ending with # or not
            if filename_no_ext.endswith('#'):
                test_filename = f"{filename_no_ext}{pattern}"
            else:
                test_filename = f"{filename_no_ext}#{pattern}"
            
            test_path = Path('itc-afm-data-platform-pjt-shared') / 'AFM_DB' / tool_name / 'tiff_dir' / test_filename
            
            print(f"  {i}. Pattern: {description}")
            print(f"     Filename: {test_filename}")
            print(f"     Path: {test_path}")
            
            if test_path.exists():
                print(f"     ✅ FOUND!")
                print(f"\n=== IMAGE FILE MATCHED ===")
                print(f"📄 Final filename: {test_filename}")
                print(f"📂 Full path: {test_path}")
                return test_path
            else:
                print(f"     ❌ Not found")
        
        print(f"\n❌ NO IMAGE FILE FOUND after trying {len(patterns_to_try)} patterns")
        print(f"Summary:")
        print(f"  Site ID: {actual_site_id}")
        print(f"  Point No: {point_no} (4-digit: {point_no_4digit})")
        print(f"  Site coordinates: X={site_x}, Y={site_y}")
        return None
            
    except Exception as e:
        print(f"❌ Error getting image file path: {e}")
        import traceback
        traceback.print_exc()
        return None