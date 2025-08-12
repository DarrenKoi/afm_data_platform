"""
MongoDB client utilities for AFM data platform
Handles storage and retrieval of parsed AFM file data
"""
import os
from datetime import datetime, timedelta
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError, BulkWriteError
import logging
import numpy as np
import pandas as pd
from bson import json_util

# Setup logging
logger = logging.getLogger(__name__)


# Data conversion utilities
def convert_for_mongodb(data):
    """
    Convert numpy/pandas types to Python native types for MongoDB storage
    
    Args:
        data: Data to convert (can be DataFrame, Series, ndarray, dict, list, etc.)
        
    Returns:
        MongoDB-compatible data
    """
    if isinstance(data, np.integer):
        return int(data)
    elif isinstance(data, np.floating):
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, pd.Series):
        return data.tolist()
    elif isinstance(data, pd.DataFrame):
        # Convert to records format for better query flexibility
        return data.to_dict('records')
    elif isinstance(data, dict):
        return {k: convert_for_mongodb(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_for_mongodb(item) for item in data]
    elif pd.isna(data):
        return None
    return data


def sanitize_mongodb_keys(data):
    """
    Sanitize keys for MongoDB (no dots or dollar signs allowed in field names)
    
    Args:
        data: Data with potentially invalid keys
        
    Returns:
        Data with sanitized keys
    """
    if isinstance(data, dict):
        sanitized = {}
        for key, value in data.items():
            # Replace dots and dollar signs with underscores
            safe_key = str(key).replace('.', '_').replace('$', '_')
            # Also handle keys that start with numbers
            if safe_key and safe_key[0].isdigit():
                safe_key = f'field_{safe_key}'
            sanitized[safe_key] = sanitize_mongodb_keys(value)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_mongodb_keys(item) for item in data]
    return data


def check_document_size(doc, size_limit_mb=15):
    """
    Check if document size is within MongoDB's limits
    
    Args:
        doc: Document to check
        size_limit_mb: Size limit in MB (default 15MB to leave margin from 16MB limit)
        
    Returns:
        tuple: (is_valid, size_in_mb)
    """
    try:
        doc_size = len(json_util.dumps(doc))
        size_mb = doc_size / (1024 * 1024)
        
        if size_mb > size_limit_mb:
            logger.warning(f"Document size: {size_mb:.2f}MB exceeds limit of {size_limit_mb}MB")
            return False, size_mb
        
        return True, size_mb
    except Exception as e:
        logger.error(f"Error checking document size: {e}")
        return False, 0


def prepare_afm_measurement_for_mongodb(parsed_file, pickle_data=None):
    """
    Prepare AFM measurement data for MongoDB storage
    
    Args:
        parsed_file: Parsed file information from file_parser
        pickle_data: Optional pickle data containing DataFrames and nested dicts
        
    Returns:
        dict: MongoDB-ready document
    """
    # Base measurement info
    document = {
        'unique_key': parsed_file['unique_key'],
        'filename': parsed_file['filename'],
        'date': parsed_file['date'],
        'formatted_date': parsed_file.get('formatted_date', parsed_file['date']),
        'recipe_name': parsed_file['recipe_name'],
        'lot_id': parsed_file['lot_id'],
        'slot_number': parsed_file['slot_number'],
        'time': parsed_file.get('time'),
        'measured_info': parsed_file.get('measured_info'),
        'tool_name': parsed_file.get('tool_name', 'MAP608'),
        
        # File availability
        'profile_dir_list': parsed_file.get('profile_dir_list'),
        'data_dir_list': parsed_file.get('data_dir_list'),
        'tiff_dir_list': parsed_file.get('tiff_dir_list'),
        'align_dir_list': parsed_file.get('align_dir_list'),
        'tip_dir_list': parsed_file.get('tip_dir_list'),
    }
    
    # Handle nested data from pickle if provided
    if pickle_data:
        # Info dict - usually small, store as-is
        if 'info' in pickle_data:
            document['info'] = convert_for_mongodb(pickle_data['info'])
        
        # Summary DataFrame - convert to records
        if 'summary' in pickle_data:
            if isinstance(pickle_data['summary'], pd.DataFrame):
                document['summary'] = pickle_data['summary'].to_dict('records')
            else:
                document['summary'] = convert_for_mongodb(pickle_data['summary'])
        
        # Profile data - check size before including
        if 'profileData' in pickle_data:
            profile_data = convert_for_mongodb(pickle_data['profileData'])
            
            # Check size of profile data
            test_doc = {'profileData': profile_data}
            is_valid, size_mb = check_document_size(test_doc, size_limit_mb=5)
            
            if is_valid:
                document['profileData'] = profile_data
            else:
                # Store reference only for large data
                logger.info(f"Profile data too large ({size_mb:.2f}MB), storing reference only")
                document['profileData'] = {
                    'type': 'reference',
                    'collection': 'profile_data',
                    'key': parsed_file['unique_key'],
                    'size_mb': size_mb
                }
        
        # Data detail - nested dict with site information
        if 'data_detail' in pickle_data:
            detail_data = convert_for_mongodb(pickle_data['data_detail'])
            document['data_detail'] = sanitize_mongodb_keys(detail_data)
        
        # Available points
        if 'available_points' in pickle_data:
            document['available_points'] = pickle_data['available_points']
    
    # Sanitize all keys
    document = sanitize_mongodb_keys(document)
    
    # Final size check
    is_valid, size_mb = check_document_size(document)
    if not is_valid:
        logger.error(f"Final document too large ({size_mb:.2f}MB) for {parsed_file['unique_key']}")
        # Remove large fields if necessary
        if 'profileData' in document and not isinstance(document.get('profileData'), dict):
            del document['profileData']
        if 'data_detail' in document:
            del document['data_detail']
    
    return document


class AFMMongoClient:
    """MongoDB client for AFM data storage and retrieval"""
    
    def __init__(self, connection_string=None):
        """
        Initialize MongoDB client
        
        Args:
            connection_string: MongoDB connection string (defaults to env variable)
        """
        # Use provided connection string or get from environment
        self.connection_string = connection_string or os.getenv('MONGODB_CONNECTION_STRING')
        
        if not self.connection_string:
            logger.warning("MongoDB connection string not provided. MongoDB features will be disabled.")
            self.client = None
            self.db = None
            return
            
        try:
            # Initialize MongoDB client
            self.client = MongoClient(self.connection_string)
            self.db = self.client['itc-afm-data-platform-mongodb']
            
            # Test connection
            self.client.server_info()
            logger.info("Successfully connected to MongoDB")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def _get_collection(self, tool_name):
        """Get collection for specific tool"""
        if not self.db:
            return None
        return self.db[tool_name]
    
    def create_indexes(self, tool_name):
        """
        Create indexes for optimal query performance
        
        Args:
            tool_name: AFM tool name (e.g., 'MAP608', 'MAPC01')
        """
        if not self.db:
            logger.warning("MongoDB not connected. Cannot create indexes.")
            return False
            
        try:
            collection = self._get_collection(tool_name)
            
            # Create indexes for fast queries
            indexes = [
                # Unique index on unique_key to prevent duplicates
                ('unique_key', ASCENDING),
                
                # Compound indexes for common queries
                ([('date', DESCENDING), ('recipe_name', ASCENDING)]),
                ([('lot_id', ASCENDING), ('slot_number', ASCENDING)]),
                ([('recipe_name', ASCENDING), ('date', DESCENDING)]),
                
                # Text index for full-text search
                ([('filename', 'text'), ('recipe_name', 'text'), ('lot_id', 'text')]),
                
                # Individual field indexes
                ('date', DESCENDING),
                ('formatted_date', DESCENDING),
                ('recipe_name', ASCENDING),
                ('lot_id', ASCENDING),
                ('slot_number', ASCENDING),
                ('measured_info', ASCENDING),
            ]
            
            for index in indexes:
                if isinstance(index, tuple):
                    # Single field index
                    field, direction = index
                    collection.create_index([(field, direction)])
                else:
                    # Compound or text index
                    collection.create_index(index)
            
            # Create unique constraint on unique_key
            collection.create_index('unique_key', unique=True)
            
            logger.info(f"Created indexes for tool: {tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating indexes for {tool_name}: {e}")
            return False
    
    def store_measurements(self, tool_name, measurements, batch_size=1000, validate_data=True):
        """
        Store multiple AFM measurements in MongoDB with data validation
        
        Args:
            tool_name: AFM tool name
            measurements: List of parsed measurement dictionaries (can include pickle data)
            batch_size: Number of documents to insert at once
            validate_data: Whether to validate and convert data before storing
            
        Returns:
            dict: Result with success status and statistics
        """
        if not self.db:
            return {
                'success': False,
                'error': 'MongoDB not connected',
                'inserted': 0,
                'updated': 0,
                'errors': 0,
                'skipped': 0
            }
        
        try:
            collection = self._get_collection(tool_name)
            
            # Ensure indexes exist
            self.create_indexes(tool_name)
            
            # Statistics
            inserted = 0
            updated = 0
            errors = 0
            skipped = 0
            
            # Process in batches
            for i in range(0, len(measurements), batch_size):
                batch = measurements[i:i + batch_size]
                
                # Prepare bulk operations
                operations = []
                for measurement in batch:
                    try:
                        # Prepare measurement data if validation is enabled
                        if validate_data:
                            # Check if measurement has pickle data
                            if 'pickle_data' in measurement:
                                pickle_data = measurement.pop('pickle_data')
                                prepared_doc = prepare_afm_measurement_for_mongodb(measurement, pickle_data)
                            else:
                                prepared_doc = prepare_afm_measurement_for_mongodb(measurement)
                        else:
                            prepared_doc = measurement
                        
                        # Add metadata
                        prepared_doc['_updated_at'] = datetime.now()
                        prepared_doc['_version'] = '1.1.0'
                        
                        # Final size check
                        is_valid, size_mb = check_document_size(prepared_doc)
                        if not is_valid:
                            logger.warning(f"Skipping document {prepared_doc.get('unique_key')} - too large ({size_mb:.2f}MB)")
                            skipped += 1
                            continue
                        
                        # Create upsert operation
                        operations.append({
                            'filter': {'unique_key': prepared_doc['unique_key']},
                            'update': {'$set': prepared_doc},
                            'upsert': True
                        })
                        
                    except Exception as e:
                        logger.error(f"Error preparing measurement {measurement.get('unique_key')}: {e}")
                        errors += 1
                
                # Execute bulk write if we have valid operations
                if operations:
                    try:
                        result = collection.bulk_write([
                            {
                                'updateOne': op
                            } for op in operations
                        ])
                        
                        inserted += result.upserted_count
                        updated += result.modified_count
                        
                    except BulkWriteError as bwe:
                        errors += len(bwe.details['writeErrors'])
                        logger.error(f"Bulk write error: {bwe.details}")
            
            logger.info(f"Stored measurements for {tool_name}: "
                       f"inserted={inserted}, updated={updated}, errors={errors}, skipped={skipped}")
            
            return {
                'success': True,
                'tool_name': tool_name,
                'total_processed': len(measurements),
                'inserted': inserted,
                'updated': updated,
                'errors': errors,
                'skipped': skipped
            }
            
        except Exception as e:
            logger.error(f"Error storing measurements: {e}")
            return {
                'success': False,
                'error': str(e),
                'inserted': 0,
                'updated': 0,
                'errors': len(measurements),
                'skipped': 0
            }
    
    def retrieve_all_measurements(self, tool_name, filters=None, projection=None):
        """
        Retrieve all measurements for a tool with optional filtering
        
        Args:
            tool_name: AFM tool name
            filters: MongoDB query filters (optional)
            projection: Fields to include/exclude (optional)
            
        Returns:
            list: List of measurement documents
        """
        if not self.db:
            logger.warning("MongoDB not connected")
            return []
        
        try:
            collection = self._get_collection(tool_name)
            
            # Default filters
            query = filters or {}
            
            # Default projection (exclude MongoDB internal fields)
            if projection is None:
                projection = {'_id': 0, '_updated_at': 0, '_version': 0}
            
            # Query with sorting by date (newest first)
            cursor = collection.find(query, projection).sort('date', DESCENDING)
            
            # Convert cursor to list
            measurements = list(cursor)
            
            logger.info(f"Retrieved {len(measurements)} measurements for {tool_name}")
            return measurements
            
        except Exception as e:
            logger.error(f"Error retrieving measurements: {e}")
            return []
    
    def search_measurements(self, tool_name, search_query, limit=None):
        """
        Search measurements using text search or pattern matching
        
        Args:
            tool_name: AFM tool name
            search_query: Search string
            limit: Maximum number of results (optional)
            
        Returns:
            list: List of matching measurements
        """
        if not self.db:
            return []
        
        try:
            collection = self._get_collection(tool_name)
            
            # Try text search first
            try:
                query = {'$text': {'$search': search_query}}
                projection = {'_id': 0, '_updated_at': 0, '_version': 0, 'score': {'$meta': 'textScore'}}
                
                cursor = collection.find(query, projection).sort([('score', {'$meta': 'textScore'})])
                
                if limit:
                    cursor = cursor.limit(limit)
                
                results = list(cursor)
                
                # If text search returns results, use them
                if results:
                    return results
                    
            except Exception as text_error:
                logger.debug(f"Text search failed, falling back to regex: {text_error}")
            
            # Fallback to regex search
            regex_pattern = {'$regex': search_query, '$options': 'i'}
            query = {
                '$or': [
                    {'filename': regex_pattern},
                    {'recipe_name': regex_pattern},
                    {'lot_id': regex_pattern},
                    {'unique_key': regex_pattern}
                ]
            }
            
            projection = {'_id': 0, '_updated_at': 0, '_version': 0}
            cursor = collection.find(query, projection).sort('date', DESCENDING)
            
            if limit:
                cursor = cursor.limit(limit)
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Error searching measurements: {e}")
            return []
    
    def get_measurement_by_key(self, tool_name, unique_key):
        """
        Get a single measurement by its unique key
        
        Args:
            tool_name: AFM tool name
            unique_key: Unique measurement key
            
        Returns:
            dict: Measurement document or None
        """
        if not self.db:
            return None
        
        try:
            collection = self._get_collection(tool_name)
            
            projection = {'_id': 0, '_updated_at': 0, '_version': 0}
            measurement = collection.find_one({'unique_key': unique_key}, projection)
            
            return measurement
            
        except Exception as e:
            logger.error(f"Error getting measurement by key: {e}")
            return None
    
    def get_measurements_by_date_range(self, tool_name, start_date, end_date):
        """
        Get measurements within a date range
        
        Args:
            tool_name: AFM tool name
            start_date: Start date string (YYMMDD format)
            end_date: End date string (YYMMDD format)
            
        Returns:
            list: List of measurements in date range
        """
        if not self.db:
            return []
        
        try:
            collection = self._get_collection(tool_name)
            
            query = {
                'date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            projection = {'_id': 0, '_updated_at': 0, '_version': 0}
            cursor = collection.find(query, projection).sort('date', DESCENDING)
            
            return list(cursor)
            
        except Exception as e:
            logger.error(f"Error getting measurements by date range: {e}")
            return []
    
    def get_recipe_statistics(self, tool_name):
        """
        Get statistics about recipes in the database
        
        Args:
            tool_name: AFM tool name
            
        Returns:
            list: Recipe statistics
        """
        if not self.db:
            return []
        
        try:
            collection = self._get_collection(tool_name)
            
            # Aggregate to get recipe counts
            pipeline = [
                {
                    '$group': {
                        '_id': '$recipe_name',
                        'count': {'$sum': 1},
                        'latest_date': {'$max': '$date'},
                        'earliest_date': {'$min': '$date'}
                    }
                },
                {
                    '$sort': {'count': -1}
                }
            ]
            
            results = list(collection.aggregate(pipeline))
            
            # Format results
            statistics = [
                {
                    'recipe_name': item['_id'],
                    'measurement_count': item['count'],
                    'latest_date': item['latest_date'],
                    'earliest_date': item['earliest_date']
                }
                for item in results if item['_id']  # Skip null recipe names
            ]
            
            return statistics
            
        except Exception as e:
            logger.error(f"Error getting recipe statistics: {e}")
            return []
    
    def delete_measurement(self, tool_name, unique_key):
        """
        Delete a measurement by its unique key
        
        Args:
            tool_name: AFM tool name
            unique_key: Unique measurement key
            
        Returns:
            bool: True if deleted, False otherwise
        """
        if not self.db:
            return False
        
        try:
            collection = self._get_collection(tool_name)
            result = collection.delete_one({'unique_key': unique_key})
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting measurement: {e}")
            return False
    
    def get_collection_stats(self, tool_name):
        """
        Get statistics about the collection
        
        Args:
            tool_name: AFM tool name
            
        Returns:
            dict: Collection statistics
        """
        if not self.db:
            return {}
        
        try:
            collection = self._get_collection(tool_name)
            
            # Get collection stats
            stats = self.db.command('collStats', tool_name)
            
            # Get document count
            count = collection.count_documents({})
            
            # Get date range
            oldest = collection.find_one({}, sort=[('date', ASCENDING)])
            newest = collection.find_one({}, sort=[('date', DESCENDING)])
            
            return {
                'tool_name': tool_name,
                'document_count': count,
                'storage_size': stats.get('storageSize', 0),
                'index_count': len(stats.get('indexSizes', {})),
                'oldest_date': oldest['date'] if oldest else None,
                'newest_date': newest['date'] if newest else None
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def cleanup_old_measurements(self, tool_name, days_to_keep=300, dry_run=False):
        """
        Delete measurements older than specified days based on date field
        
        Args:
            tool_name: AFM tool name
            days_to_keep: Number of days to keep (default 300)
            dry_run: If True, only count documents without deleting
            
        Returns:
            dict: Cleanup results
        """
        if not self.db:
            return {
                'success': False,
                'error': 'MongoDB not connected'
            }
        
        try:
            collection = self._get_collection(tool_name)
            
            # Calculate cutoff date (YYMMDD format)
            cutoff_datetime = datetime.now() - timedelta(days=days_to_keep)
            cutoff_date = cutoff_datetime.strftime('%y%m%d')
            
            logger.info(f"Cleanup: Looking for measurements before {cutoff_date} "
                       f"(older than {days_to_keep} days)")
            
            # Build query for old documents
            query = {
                'date': {'$lt': cutoff_date}
            }
            
            # Count documents to be deleted
            count_to_delete = collection.count_documents(query)
            
            if count_to_delete == 0:
                logger.info(f"No old measurements found for {tool_name}")
                return {
                    'success': True,
                    'tool_name': tool_name,
                    'days_to_keep': days_to_keep,
                    'cutoff_date': cutoff_date,
                    'found': 0,
                    'deleted': 0,
                    'dry_run': dry_run
                }
            
            # Get sample of documents to be deleted for logging
            sample_docs = list(collection.find(
                query, 
                {'unique_key': 1, 'date': 1, 'recipe_name': 1},
                limit=5
            ))
            
            logger.info(f"Found {count_to_delete} measurements to clean up")
            logger.info(f"Sample documents to delete: {sample_docs}")
            
            deleted_count = 0
            
            if not dry_run:
                # Perform deletion
                result = collection.delete_many(query)
                deleted_count = result.deleted_count
                logger.info(f"Deleted {deleted_count} old measurements from {tool_name}")
            else:
                logger.info(f"DRY RUN: Would delete {count_to_delete} measurements")
            
            return {
                'success': True,
                'tool_name': tool_name,
                'days_to_keep': days_to_keep,
                'cutoff_date': cutoff_date,
                'found': count_to_delete,
                'deleted': deleted_count,
                'dry_run': dry_run,
                'sample_deleted': sample_docs
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old measurements: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool_name': tool_name
            }
    
    def cleanup_all_tools(self, days_to_keep=300, dry_run=False):
        """
        Cleanup old measurements for all tools
        
        Args:
            days_to_keep: Number of days to keep (default 300)
            dry_run: If True, only count documents without deleting
            
        Returns:
            dict: Cleanup results for all tools
        """
        tools = ['MAP608', 'MAPC01', '5EAP1501']
        results = {}
        total_deleted = 0
        total_found = 0
        
        for tool in tools:
            result = self.cleanup_old_measurements(tool, days_to_keep, dry_run)
            results[tool] = result
            
            if result['success']:
                total_found += result['found']
                total_deleted += result['deleted']
        
        return {
            'timestamp': datetime.now().isoformat(),
            'days_to_keep': days_to_keep,
            'dry_run': dry_run,
            'total_found': total_found,
            'total_deleted': total_deleted,
            'results': results
        }
    
    def get_date_statistics(self, tool_name):
        """
        Get statistics about measurement dates for planning cleanup
        
        Args:
            tool_name: AFM tool name
            
        Returns:
            dict: Date statistics
        """
        if not self.db:
            return {}
        
        try:
            collection = self._get_collection(tool_name)
            
            # Get date distribution
            pipeline = [
                {
                    '$group': {
                        '_id': {
                            'year': {'$substr': ['$date', 0, 2]},
                            'month': {'$substr': ['$date', 2, 2]}
                        },
                        'count': {'$sum': 1},
                        'oldest_date': {'$min': '$date'},
                        'newest_date': {'$max': '$date'}
                    }
                },
                {
                    '$sort': {'_id.year': 1, '_id.month': 1}
                }
            ]
            
            date_distribution = list(collection.aggregate(pipeline))
            
            # Calculate age statistics
            today = datetime.now()
            age_buckets = {
                '0-30_days': 0,
                '31-90_days': 0,
                '91-180_days': 0,
                '181-300_days': 0,
                'over_300_days': 0
            }
            
            for bucket in date_distribution:
                # Convert YYMMDD to datetime
                year = int('20' + bucket['_id']['year'])
                month = int(bucket['_id']['month'])
                
                # Approximate age calculation
                bucket_date = datetime(year, month, 15)  # Use middle of month
                age_days = (today - bucket_date).days
                
                count = bucket['count']
                
                if age_days <= 30:
                    age_buckets['0-30_days'] += count
                elif age_days <= 90:
                    age_buckets['31-90_days'] += count
                elif age_days <= 180:
                    age_buckets['91-180_days'] += count
                elif age_days <= 300:
                    age_buckets['181-300_days'] += count
                else:
                    age_buckets['over_300_days'] += count
            
            return {
                'tool_name': tool_name,
                'date_distribution': date_distribution,
                'age_buckets': age_buckets,
                'total_measurements': sum(age_buckets.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting date statistics: {e}")
            return {}
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
_mongo_client = None


def get_mongo_client(connection_string=None):
    """
    Get or create MongoDB client singleton
    
    Args:
        connection_string: MongoDB connection string (optional)
        
    Returns:
        AFMMongoClient: MongoDB client instance
    """
    global _mongo_client
    
    if _mongo_client is None:
        _mongo_client = AFMMongoClient(connection_string)
    
    return _mongo_client


# Convenience functions for common operations
def store_afm_measurements(tool_name, measurements):
    """Store AFM measurements in MongoDB"""
    client = get_mongo_client()
    return client.store_measurements(tool_name, measurements)


def search_afm_measurements(tool_name, search_query, limit=100):
    """Search AFM measurements in MongoDB"""
    client = get_mongo_client()
    return client.search_measurements(tool_name, search_query, limit)


def get_all_afm_measurements(tool_name, filters=None):
    """Get all AFM measurements from MongoDB"""
    client = get_mongo_client()
    return client.retrieve_all_measurements(tool_name, filters)


def get_afm_measurement(tool_name, unique_key):
    """Get single AFM measurement by unique key"""
    client = get_mongo_client()
    return client.get_measurement_by_key(tool_name, unique_key)