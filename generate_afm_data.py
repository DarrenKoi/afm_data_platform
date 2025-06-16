import os
import pickle
import random
from datetime import datetime, timedelta

def parse_filename(filename):
    """Parse AFM filename to extract components"""
    # Remove .csv extension and split by #
    parts = filename.replace('.csv', '').split('#')
    
    if len(parts) >= 4:
        date = parts[1]
        recipe = parts[2]
        lot_info = parts[3]  # Contains lot_id and potentially date/time info
        slot_measurement = parts[4] if len(parts) > 4 else ""
        
        # Extract lot_id (before underscore or bracket)
        if '[' in lot_info:
            lot_id = lot_info.split('[')[0]
        elif '_' in lot_info:
            lot_id = lot_info.split('_')[0]
        else:
            lot_id = lot_info
            
        # Extract slot and measurement info
        slot = "01"
        measurement = "1"
        if slot_measurement:
            if '_' in slot_measurement:
                slot_parts = slot_measurement.split('_')
                slot = slot_parts[0]
                measurement = slot_parts[1] if len(slot_parts) > 1 else "1"
            else:
                slot = slot_measurement
                
        return {
            'date': date,
            'recipe': recipe,
            'lot_id': lot_id,
            'slot': slot,
            'measurement': measurement
        }
    
    return None

def generate_measurement_info(parsed_info):
    """Generate measurement info section"""
    # Convert date format YYMMDD to datetime
    date_str = parsed_info['date']
    year = 2000 + int(date_str[:2])
    month = int(date_str[2:4])
    day = int(date_str[4:6])
    
    start_time = datetime(year, month, day) + timedelta(
        hours=random.randint(8, 18),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    
    return {
        'Lot ID': parsed_info['lot_id'],
        'Recipe ID': parsed_info['recipe'],
        'Carrier ID': f"CAR{random.randint(100, 999)}",
        'Sample ID': f"S{parsed_info['slot']}",
        'Start Time': start_time.strftime("%Y-%m-%d %H:%M:%S"),
        'Tool': 'MAP608',
        'Operator': f"OP{random.randint(1000, 9999)}",
        'Measurement': parsed_info['measurement']
    }

def generate_data_status(num_points):
    """Generate data status section with statistical summary"""
    data_status = {}
    
    # Use the provided number of measurement points
    for i in range(1, num_points + 1):
        point_name = f"{i}_UL"
        
        # Generate base values for consistency
        left_base = random.uniform(50, 150)
        right_base = random.uniform(45, 145)
        ref_base = random.uniform(40, 140)
        
        data_status[point_name] = {
            'ITEM': ['MEAN', 'STDEV', 'MIN', 'MAX', 'RANGE'],
            'Left_H (nm)': [
                round(left_base, 2),
                round(random.uniform(1, 5), 2),
                round(left_base - random.uniform(5, 15), 2),
                round(left_base + random.uniform(5, 15), 2),
                round(random.uniform(10, 30), 2)
            ],
            'Right_H (nm)': [
                round(right_base, 2),
                round(random.uniform(1, 5), 2),
                round(right_base - random.uniform(5, 15), 2),
                round(right_base + random.uniform(5, 15), 2),
                round(random.uniform(10, 30), 2)
            ],
            'Ref_H (nm)': [
                round(ref_base, 2),
                round(random.uniform(1, 5), 2),
                round(ref_base - random.uniform(5, 15), 2),
                round(ref_base + random.uniform(5, 15), 2),
                round(random.uniform(10, 30), 2)
            ]
        }
    
    return data_status

def generate_data_detail(num_points):
    """Generate detailed measurement data for each point"""
    data_detail = {}
    
    # Use the provided number of measurement points
    for i in range(1, num_points + 1):
        point_name = f"{i}_UL"
        
        # Number of measurement points for this location
        num_measurements = random.randint(20, 50)
        
        point_data = {
            'Point No': list(range(1, num_measurements + 1)),
            'X (um)': [round(random.uniform(-1000, 1000), 1) for _ in range(num_measurements)],
            'Y (um)': [round(random.uniform(-1000, 1000), 1) for _ in range(num_measurements)],
            'Method ID': [random.randint(1, 5) for _ in range(num_measurements)],
            'State': [random.choice(['OK', 'NG', 'WARN']) for _ in range(num_measurements)],
            'Valid': [random.choice([True, False]) for _ in range(num_measurements)],
            'Left_H (nm)': [round(random.uniform(40, 160), 2) for _ in range(num_measurements)],
            'Left_H_Valid': [random.choice([True, False]) for _ in range(num_measurements)],
            'Right_H (nm)': [round(random.uniform(35, 155), 2) for _ in range(num_measurements)],
            'Right_H_Valid': [random.choice([True, False]) for _ in range(num_measurements)],
            'Ref_H (nm)': [round(random.uniform(30, 150), 2) for _ in range(num_measurements)],
            'Ref_H_Valid': [random.choice([True, False]) for _ in range(num_measurements)],
            'Pick Up Count': [random.randint(1, 10) for _ in range(num_measurements)],
            'Sample Count': [random.randint(1, 5) for _ in range(num_measurements)],
            'Approach Count': [random.randint(1, 3) for _ in range(num_measurements)],
            'Mileage': [round(random.uniform(0, 100), 1) for _ in range(num_measurements)]
        }
        
        data_detail[point_name] = point_data
    
    return data_detail

def generate_afm_data_file(filename):
    """Generate complete AFM data structure for a given filename"""
    parsed_info = parse_filename(filename)
    if not parsed_info:
        return None
    
    # Generate consistent number of measurement points (5-10)
    num_points = random.randint(5, 10)
    
    # Generate all three data sections with consistent point count
    info = generate_measurement_info(parsed_info)
    data_status = generate_data_status(num_points)
    data_detail = generate_data_detail(num_points)
    
    return {
        'info': info,
        'data_status': data_status,
        'data_detail': data_detail
    }

def main():
    # Read the file list
    list_file_path = '/mnt/c/Python_Projects/afm_data_platform/itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/data_dir_list.txt'
    data_dir_path = '/mnt/c/Python_Projects/afm_data_platform/itc-afm-data-platform-pjt-shared/AFM_DB/MAP608/data_dir'
    
    # Create data_dir if it doesn't exist
    os.makedirs(data_dir_path, exist_ok=True)
    
    # Read all filenames
    with open(list_file_path, 'r') as f:
        filenames = [line.strip() for line in f if line.strip()]
    
    print(f"Generating {len(filenames)} AFM data files...")
    
    for i, filename in enumerate(filenames):
        if filename.endswith('.csv'):
            # Generate pickle filename (replace .csv with .pkl)
            pkl_filename = filename.replace('.csv', '.pkl')
            pkl_path = os.path.join(data_dir_path, pkl_filename)
            
            # Generate data
            afm_data = generate_afm_data_file(filename)
            
            if afm_data:
                # Save as pickle file
                with open(pkl_path, 'wb') as f:
                    pickle.dump(afm_data, f)
                
                if (i + 1) % 20 == 0:
                    print(f"Generated {i + 1}/{len(filenames)} files...")
    
    print(f"Successfully generated {len(filenames)} AFM data files in {data_dir_path}")

if __name__ == "__main__":
    main()