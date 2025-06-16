import random
import time
from datetime import datetime, timedelta

def get_dummy_afm_data():
    """Generate dummy AFM measurement data"""
    
    # Generate height map data (simplified 2D array)
    height_map = []
    for i in range(50):
        row = []
        for j in range(50):
            # Create some realistic height variations
            height = 10 + 5 * random.random() * (i/50) + 3 * random.random() * (j/50)
            height += random.uniform(-2, 2)  # Add noise
            row.append(round(height, 2))
        height_map.append(row)
    
    # Generate measurement metadata
    measurement_data = {
        'id': f'AFM_{int(time.time())}',
        'timestamp': datetime.now().isoformat(),
        'sample_info': {
            'name': f'Sample_{random.randint(1, 100)}',
            'material': random.choice(['Silicon', 'Gold', 'Graphene', 'PMMA', 'SiO2']),
            'preparation_date': (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat()
        },
        'scan_parameters': {
            'scan_size': '1.0 μm × 1.0 μm',
            'resolution': '50 × 50 pixels',
            'scan_rate': f'{random.uniform(0.5, 2.0):.1f} Hz',
            'setpoint': f'{random.uniform(0.1, 1.0):.2f} nN'
        },
        'height_map': height_map,
        'statistics': {
            'min_height': min(min(row) for row in height_map),
            'max_height': max(max(row) for row in height_map),
            'mean_height': sum(sum(row) for row in height_map) / (50 * 50),
            'roughness': random.uniform(0.5, 3.0)
        }
    }
    
    return measurement_data

def get_trend_data():
    """Generate dummy trend analysis data"""
    
    # Generate time series data for the last 30 days
    dates = []
    measurements = []
    roughness_values = []
    
    base_date = datetime.now() - timedelta(days=30)
    
    for i in range(30):
        current_date = base_date + timedelta(days=i)
        dates.append(current_date.strftime('%Y-%m-%d'))
        
        # Simulate daily measurement count with some trend
        daily_count = max(1, int(10 + 5 * random.random() + 2 * (i/30)))
        measurements.append(daily_count)
        
        # Simulate roughness trend
        roughness = 1.5 + 0.5 * random.random() + 0.3 * (i/30)
        roughness_values.append(round(roughness, 2))
    
    trend_data = {
        'time_series': {
            'dates': dates,
            'measurement_count': measurements,
            'average_roughness': roughness_values
        },
        'summary': {
            'total_measurements': sum(measurements),
            'average_daily_measurements': round(sum(measurements) / len(measurements), 1),
            'roughness_trend': 'Increasing' if roughness_values[-1] > roughness_values[0] else 'Decreasing',
            'period': '30 days'
        },
        'quality_metrics': {
            'successful_scans': random.randint(85, 98),
            'average_scan_time': f'{random.uniform(5, 15):.1f} minutes',
            'data_quality_score': random.randint(85, 100)
        }
    }
    
    return trend_data

def get_analysis_results():
    """Generate dummy analysis results"""
    
    results = []
    analysis_types = ['Surface Roughness', 'Grain Analysis', 'Step Height', 'Particle Analysis', 'Defect Detection']
    
    for i in range(5):
        result = {
            'id': f'analysis_{i+1}',
            'type': analysis_types[i],
            'timestamp': (datetime.now() - timedelta(hours=random.randint(1, 48))).isoformat(),
            'status': random.choice(['Completed', 'In Progress', 'Failed', 'Pending']),
            'progress': random.randint(0, 100) if random.choice([True, False]) else 100,
            'results': {
                'value': round(random.uniform(0.1, 10.0), 2),
                'unit': random.choice(['nm', 'μm', 'nm²', '%', 'count']),
                'confidence': random.randint(70, 99)
            },
            'sample_id': f'Sample_{random.randint(1, 50)}'
        }
        results.append(result)
    
    analysis_data = {
        'results': results,
        'summary': {
            'total_analyses': len(results),
            'completed': len([r for r in results if r['status'] == 'Completed']),
            'in_progress': len([r for r in results if r['status'] == 'In Progress']),
            'failed': len([r for r in results if r['status'] == 'Failed'])
        },
        'last_updated': datetime.now().isoformat()
    }
    
    return analysis_data

def get_profile_data(group_key, point):
    """Generate profile data for AFM visualization"""
    
    # Use group_key and point to create deterministic but varied data
    seed = hash(f"{group_key}_{point}") % 1000000
    random.seed(seed)
    
    # Generate 3D surface profile data
    surface_width = 10.0  # micrometers
    surface_height = 10.0  # micrometers
    base_z = random.uniform(5.0, 15.0)  # base height
    
    profile_points = []
    points_per_axis = 100  # 100x100 grid for detailed surface
    
    for i in range(points_per_axis):
        for j in range(points_per_axis):
            x = (i / (points_per_axis - 1)) * surface_width
            y = (j / (points_per_axis - 1)) * surface_height
            
            # Create realistic surface features
            normalized_x = i / (points_per_axis - 1)
            normalized_y = j / (points_per_axis - 1)
            
            # Main surface pattern
            surface_pattern = (
                2.0 * random.random() * 
                (0.5 + 0.3 * (normalized_x - 0.5) + 0.2 * (normalized_y - 0.5))
            )
            
            # Add some noise and microstructure
            noise = random.uniform(-0.3, 0.3)
            micro_features = 0.1 * random.random() * (
                1 + 0.5 * (normalized_x * normalized_y)
            )
            
            z = base_z + surface_pattern + noise + micro_features
            
            profile_points.append({
                'x': round(x, 4),
                'y': round(y, 4),
                'z': round(z, 6)
            })
    
    profile_data = {
        'group_key': group_key,
        'point': point,
        'timestamp': datetime.now().isoformat(),
        'surface_dimensions': {
            'width': surface_width,
            'height': surface_height,
            'unit': 'μm'
        },
        'grid_resolution': {
            'x_points': points_per_axis,
            'y_points': points_per_axis,
            'total_points': len(profile_points)
        },
        'profile_data': profile_points,
        'statistics': {
            'min_z': min(p['z'] for p in profile_points),
            'max_z': max(p['z'] for p in profile_points),
            'mean_z': sum(p['z'] for p in profile_points) / len(profile_points),
            'z_range': max(p['z'] for p in profile_points) - min(p['z'] for p in profile_points)
        }
    }
    
    return profile_data

def get_summary_data(group_key):
    """Generate summary data for measurement points"""
    
    # Use group_key to create deterministic data
    seed = hash(group_key) % 1000000
    random.seed(seed)
    
    # Generate summary for multiple measurement points
    num_points = random.randint(3, 10)
    summary_points = []
    
    for i in range(num_points):
        point_data = {
            'point': i + 1,
            'no_x': round(random.uniform(1000, 11000), 2),
            'no_y': round(random.uniform(-50000, 50000), 2),
            'id': i + 1,
            'state': 'TRUE' if random.random() > 0.1 else 'FALSE',
            'left_h': round(random.uniform(2.0, 7.0), 3),
            'right_h': round(random.uniform(2.0, 7.0), 3),
            'measurement_quality': random.choice(['Excellent', 'Good', 'Fair', 'Poor']),
            'scan_time': round(random.uniform(30, 300), 1)  # seconds
        }
        summary_points.append(point_data)
    
    summary_data = {
        'group_key': group_key,
        'timestamp': datetime.now().isoformat(),
        'total_points': num_points,
        'summary_points': summary_points,
        'overall_statistics': {
            'valid_measurements': len([p for p in summary_points if p['state'] == 'TRUE']),
            'average_left_h': round(sum(p['left_h'] for p in summary_points) / num_points, 3),
            'average_right_h': round(sum(p['right_h'] for p in summary_points) / num_points, 3),
            'total_scan_time': round(sum(p['scan_time'] for p in summary_points), 1)
        }
    }
    
    return summary_data