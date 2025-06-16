"""
AFM Measurement Data Service
Handles AFM measurement metadata and file location information
"""

import os
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class AFMDataService:
    def __init__(self):
        self.data_cache = None
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes cache
        
    def _generate_dummy_data(self, num_records: int = 15000) -> List[Dict[str, Any]]:
        """Generate dummy AFM measurement metadata"""
        
        # Set seed for reproducible data
        random.seed(42)
        
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
                'measurement_timestamp': measurement_date.isoformat(),
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
        
        return data
    
    def _load_from_parquet(self, file_path: str) -> Optional[List[Dict[str, Any]]]:
        """Load data from parquet file if available"""
        try:
            import pandas as pd
            if os.path.exists(file_path):
                df = pd.read_parquet(file_path)
                # Convert datetime columns to ISO format strings
                if 'measurement_timestamp' in df.columns:
                    df['measurement_timestamp'] = df['measurement_timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
                return df.to_dict('records')
        except ImportError:
            print("Pandas not available, using generated dummy data")
        except Exception as e:
            print(f"Error loading parquet file: {e}")
        return None
    
    def get_measurement_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """Get AFM measurement data from parquet file or generate dummy data"""
        
        # Check cache
        if not force_refresh and self.data_cache is not None and self.cache_timestamp is not None:
            if (datetime.now() - self.cache_timestamp).seconds < self.cache_duration:
                return self.data_cache
        
        # Try to load from parquet file first
        parquet_path = os.path.join('..', 'shared-data', 'afm_measurements.parquet')
        data = self._load_from_parquet(parquet_path)
        
        # If parquet file doesn't exist or can't be loaded, generate dummy data
        if data is None:
            data = self._generate_dummy_data()
        
        # Cache the data
        self.data_cache = data
        self.cache_timestamp = datetime.now()
        
        return data
    
    def search_measurements(self, query: str = "", limit: int = 100, offset: int = 0) -> Dict[str, Any]:
        """Search AFM measurements with optional filtering - optimized for large datasets"""
        
        data = self.get_measurement_data()
        
        # Filter data based on search query
        filtered_data = data
        if query and query.strip():
            query_terms = query.strip().lower().split()  # Split multiple terms
            filtered_data = []
            
            for record in data:
                # Create searchable text (concatenated fields for faster searching)
                searchable_text = ' '.join([
                    str(record.get('lot_id', '')),
                    str(record.get('fab_id', '')),
                    str(record.get('tool_name', '')),
                    str(record.get('recipe_name', '')),
                    str(record.get('material', '')),
                    str(record.get('process_step', '')),
                    str(record.get('measurement_id', '')),
                    str(record.get('wafer_id', '')),
                    str(record.get('operator', ''))
                ]).lower()
                
                # Check if ALL query terms match (AND logic)
                if all(term in searchable_text for term in query_terms):
                    filtered_data.append(record)
        
        # Sort by timestamp (newest first)
        filtered_data.sort(key=lambda x: x.get('measurement_timestamp', ''), reverse=True)
        
        # Apply pagination
        total_count = len(filtered_data)
        paginated_data = filtered_data[offset:offset + limit]
        
        return {
            'data': paginated_data,
            'total': total_count,
            'limit': limit,
            'offset': offset,
            'query': query,
            'has_more': offset + limit < total_count
        }
    
    def get_quick_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Get quick search suggestions for autocomplete"""
        if not query or len(query) < 2:
            return []
        
        data = self.get_measurement_data()
        suggestions = set()
        query_lower = query.lower()
        
        # Collect unique values that start with or contain the query
        for record in data:
            fields_to_check = [
                record.get('lot_id', ''),
                record.get('fab_id', ''),
                record.get('tool_name', ''),
                record.get('recipe_name', ''),
                record.get('material', ''),
                record.get('process_step', '')
            ]
            
            for field_value in fields_to_check:
                field_str = str(field_value)
                if query_lower in field_str.lower():
                    suggestions.add(field_str)
                    if len(suggestions) >= limit:
                        break
            
            if len(suggestions) >= limit:
                break
        
        return sorted(list(suggestions))[:limit]
    
    def get_measurement_by_id(self, measurement_id: str) -> Optional[Dict[str, Any]]:
        """Get specific measurement by ID"""
        data = self.get_measurement_data()
        
        for record in data:
            if record.get('measurement_id') == measurement_id:
                return record
        
        return None
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics for all measurements"""
        data = self.get_measurement_data()
        
        if not data:
            return {}
        
        # Count by various categories
        fab_counts = {}
        tool_counts = {}
        recipe_counts = {}
        status_counts = {}
        
        for record in data:
            fab_id = record.get('fab_id', 'Unknown')
            tool_name = record.get('tool_name', 'Unknown')
            recipe_name = record.get('recipe_name', 'Unknown')
            status = record.get('status', 'Unknown')
            
            fab_counts[fab_id] = fab_counts.get(fab_id, 0) + 1
            tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            recipe_counts[recipe_name] = recipe_counts.get(recipe_name, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_measurements': len(data),
            'fab_distribution': fab_counts,
            'tool_distribution': tool_counts,
            'recipe_distribution': recipe_counts,
            'status_distribution': status_counts,
            'date_range': {
                'earliest': min(record.get('measurement_timestamp', '') for record in data),
                'latest': max(record.get('measurement_timestamp', '') for record in data)
            }
        }

# Global instance
afm_data_service = AFMDataService()