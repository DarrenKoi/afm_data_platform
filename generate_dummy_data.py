#!/usr/bin/env python3
"""
Generate dummy AFM measurement data in parquet format
This script creates realistic metadata for AFM measurements
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

def generate_afm_measurement_data(num_records=500):
    """Generate dummy AFM measurement metadata"""
    
    # Set seed for reproducible data
    random.seed(42)
    np.random.seed(42)
    
    # AFM measurement metadata
    fabs = ['SK_Hynix_M14', 'SK_Hynix_M15', 'SK_Hynix_M16', 'SK_Hynix_Cheongju', 'SK_Hynix_Wuxi']
    tools = ['AFM_Scanner_01', 'AFM_Scanner_02', 'AFM_Scanner_03', 'AFM_Scanner_04', 'AFM_Scanner_05']
    recipes = ['Standard_Scan', 'High_Resolution', 'Fast_Scan', 'Deep_Analysis', 'Surface_Profile', 'Defect_Detection']
    materials = ['Silicon', 'SiO2', 'Gold', 'Graphene', 'PMMA', 'Copper', 'Aluminum', 'GaN', 'InGaAs']
    processes = ['Lithography', 'Etching', 'Deposition', 'CMP', 'Cleaning', 'Annealing', 'Ion_Implant']
    
    data = []
    base_date = datetime.now() - timedelta(days=365)  # Start from 1 year ago
    
    for i in range(num_records):
        # Generate measurement timestamp
        measurement_date = base_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        # Generate lot ID (semiconductor industry format)
        lot_id = f"LOT{random.randint(100000, 999999)}"
        
        # Generate wafer ID
        wafer_id = f"W{random.randint(1, 25):02d}"
        
        # Generate measurement ID
        measurement_id = f"AFM_{measurement_date.strftime('%Y%m%d_%H%M%S')}_{i:04d}"
        
        # Generate file location in shared-data folder
        year_month = measurement_date.strftime('%Y%m')
        file_location = f"shared-data/afm_measurements/{year_month}/{lot_id}/{wafer_id}/{measurement_id}.afm"
        
        # Generate scan parameters
        scan_size_options = ['1.0x1.0', '2.0x2.0', '5.0x5.0', '10.0x10.0', '20.0x20.0']
        resolution_options = ['256x256', '512x512', '1024x1024', '2048x2048']
        
        record = {
            'measurement_id': measurement_id,
            'lot_id': lot_id,
            'wafer_id': wafer_id,
            'fab_id': random.choice(fabs),
            'tool_name': random.choice(tools),
            'recipe_name': random.choice(recipes),
            'material': random.choice(materials),
            'process_step': random.choice(processes),
            'measurement_timestamp': measurement_date,
            'file_location': file_location,
            
            # Scan parameters
            'scan_size_um': random.choice(scan_size_options),
            'resolution': random.choice(resolution_options),
            'scan_rate_hz': round(random.uniform(0.1, 2.0), 2),
            'setpoint_nN': round(random.uniform(0.1, 5.0), 2),
            
            # Measurement results (summary statistics)
            'rms_roughness_nm': round(random.uniform(0.1, 10.0), 3),
            'mean_height_nm': round(random.uniform(-50.0, 50.0), 3),
            'max_height_nm': round(random.uniform(0.0, 100.0), 3),
            'min_height_nm': round(random.uniform(-100.0, 0.0), 3),
            'surface_area_um2': round(random.uniform(1.0, 400.0), 2),
            
            # Quality metrics
            'measurement_quality': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
            'scan_duration_minutes': round(random.uniform(2.0, 30.0), 1),
            'data_completeness_percent': random.randint(85, 100),
            
            # Process information
            'operator': f"Operator_{random.randint(1, 20):02d}",
            'shift': random.choice(['Day', 'Night', 'Weekend']),
            'temperature_c': round(random.uniform(20.0, 25.0), 1),
            'humidity_percent': random.randint(30, 60),
            
            # Status and flags
            'status': random.choice(['Completed', 'In_Progress', 'Failed', 'Under_Review']),
            'has_defects': random.choice([True, False]),
            'requires_followup': random.choice([True, False]),
            'data_archived': random.choice([True, False])
        }
        
        data.append(record)
    
    return pd.DataFrame(data)

def main():
    """Generate and save dummy AFM data"""
    print("Generating dummy AFM measurement data...")
    
    # Create shared-data directory structure
    shared_data_dir = "../shared-data"
    os.makedirs(shared_data_dir, exist_ok=True)
    
    # Generate data
    df = generate_afm_measurement_data(500)  # Generate 500 records
    
    # Save as parquet file
    parquet_file = os.path.join(shared_data_dir, "afm_measurements.parquet")
    df.to_parquet(parquet_file, index=False)
    
    print(f"Generated {len(df)} records")
    print(f"Saved to: {parquet_file}")
    print(f"File size: {os.path.getsize(parquet_file) / 1024:.1f} KB")
    
    # Display sample data
    print("\nSample data:")
    print(df.head().to_string())
    
    # Display column info
    print(f"\nDataset info:")
    print(f"Columns: {list(df.columns)}")
    print(f"Data types: {dict(df.dtypes)}")
    
    # Display some statistics
    print(f"\nData statistics:")
    print(f"Date range: {df['measurement_timestamp'].min()} to {df['measurement_timestamp'].max()}")
    print(f"Unique lots: {df['lot_id'].nunique()}")
    print(f"Unique fabs: {df['fab_id'].nunique()}")
    print(f"Unique tools: {df['tool_name'].nunique()}")
    print(f"Unique recipes: {df['recipe_name'].nunique()}")

if __name__ == "__main__":
    main()