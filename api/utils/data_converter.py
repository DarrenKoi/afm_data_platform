"""
Data conversion utilities for AFM measurement data
"""


def convert_data_status_to_records(data_status):
    """
    Convert data_status structure from generate_data_status to DataFrame records format
    
    Input format:
    {
        '1_UL': {
            'ITEM': ['MEAN', 'STDEV', 'MIN', 'MAX', 'RANGE'],
            'Left_H (nm)': [129.61, 4.52, 121.64, 141.05, 15.74],
            'Right_H (nm)': [93.46, 3.24, 79.39, 99.66, 18.54],
            'Ref_H (nm)': [84.42, 4.52, 70.65, 94.31, 26.78]
        }
    }
    
    Output format:
    [
        {'ITEM': 'MEAN', '1_UL': 129.61, 'Left_H (nm)': 129.61, 'Right_H (nm)': 93.46, 'Ref_H (nm)': 84.42},
        {'ITEM': 'STDEV', '1_UL': 4.52, 'Left_H (nm)': 4.52, 'Right_H (nm)': 3.24, 'Ref_H (nm)': 4.52},
        ...
    ]
    """
    print(f"🔄 [convert_data_status_to_records] Input data_status: {data_status}")
    print(f"🔄 [convert_data_status_to_records] Input type: {type(data_status)}")
    
    if not data_status:
        print(f"⚠️ [convert_data_status_to_records] No data_status provided")
        return []
    
    records = []
    
    # Get the first point to determine the ITEM structure
    first_point_key = list(data_status.keys())[0]
    first_point_data = data_status[first_point_key]
    print(f"🔄 [convert_data_status_to_records] First point key: {first_point_key}")
    print(f"🔄 [convert_data_status_to_records] First point data: {first_point_data}")
    
    if 'ITEM' not in first_point_data:
        print(f"❌ [convert_data_status_to_records] No ITEM key in first point data")
        return []
    
    items = first_point_data['ITEM']
    print(f"🔄 [convert_data_status_to_records] ITEM list: {items}")
    
    # Create a record for each statistic (MEAN, STDEV, etc.)
    for i, item_name in enumerate(items):
        print(f"🔄 [convert_data_status_to_records] Processing item {i}: {item_name}")
        record = {'ITEM': item_name}
        
        # Add values from each measurement point and parameter
        for point_key, point_data in data_status.items():
            print(f"🔄 [convert_data_status_to_records] Processing point: {point_key}")
            for param_key, param_values in point_data.items():
                if param_key != 'ITEM' and isinstance(param_values, list) and i < len(param_values):
                    print(f"🔄 [convert_data_status_to_records] Adding {param_key}[{i}] = {param_values[i]}")
                    # Use point_key for measurement points (e.g., '1_UL')
                    if point_key not in record:
                        record[point_key] = param_values[i]
                    # Also add with parameter name for other columns
                    record[param_key] = param_values[i]
        
        print(f"🔄 [convert_data_status_to_records] Created record: {record}")
        records.append(record)
    
    print(f"✅ [convert_data_status_to_records] Final records: {records}")
    return records


def convert_data_detail_to_records(data_detail):
    """
    Convert data_detail structure to records format for frontend
    """
    if not data_detail:
        return []
    
    all_records = []
    
    for point_key, point_data in data_detail.items():
        if 'Point No' in point_data:
            point_numbers = point_data['Point No']
            num_points = len(point_numbers)
            
            for i in range(num_points):
                record = {'measurement_point': point_key, 'index': i}
                
                for param_key, param_values in point_data.items():
                    if isinstance(param_values, list) and i < len(param_values):
                        record[param_key] = param_values[i]
                
                all_records.append(record)
    
    return all_records