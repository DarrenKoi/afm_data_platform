"""
MongoDB integration for API routes
Provides functions to use MongoDB as primary data source with file system fallback
"""
import os
import logging
from typing import List, Dict, Optional

from .mongo_client import get_mongo_client
from .file_parser import load_afm_file_list

logger = logging.getLogger(__name__)


def is_mongodb_enabled():
    """Check if MongoDB is enabled and configured"""
    return bool(os.getenv('MONGODB_CONNECTION_STRING')) and os.getenv('USE_MONGODB', 'false').lower() == 'true'


def get_afm_measurements_with_fallback(tool_name: str) -> List[Dict]:
    """
    Get AFM measurements from MongoDB with file system fallback
    
    Args:
        tool_name: AFM tool name
        
    Returns:
        List of measurement dictionaries
    """
    try:
        if is_mongodb_enabled():
            logger.info(f"Attempting to load measurements from MongoDB for tool: {tool_name}")
            
            client = get_mongo_client()
            if client.db:
                measurements = client.retrieve_all_measurements(tool_name)
                
                if measurements:
                    logger.info(f"Successfully loaded {len(measurements)} measurements from MongoDB")
                    return measurements
                else:
                    logger.warning("No measurements found in MongoDB, falling back to file system")
        
    except Exception as e:
        logger.error(f"Error loading from MongoDB: {e}, falling back to file system")
    
    # Fallback to file system
    logger.info(f"Loading measurements from file system for tool: {tool_name}")
    return load_afm_file_list(tool_name)


def search_measurements_with_fallback(tool_name: str, search_query: str, limit: int = 100) -> List[Dict]:
    """
    Search AFM measurements with MongoDB optimization
    
    Args:
        tool_name: AFM tool name
        search_query: Search string
        limit: Maximum results
        
    Returns:
        List of matching measurements
    """
    try:
        if is_mongodb_enabled() and search_query:
            logger.info(f"Searching MongoDB for: {search_query}")
            
            client = get_mongo_client()
            if client.db:
                results = client.search_measurements(tool_name, search_query, limit)
                
                if results:
                    logger.info(f"Found {len(results)} results in MongoDB")
                    return results
    
    except Exception as e:
        logger.error(f"MongoDB search error: {e}")
    
    # Fallback to loading all and filtering locally
    logger.info("Using local search fallback")
    measurements = get_afm_measurements_with_fallback(tool_name)
    
    if not search_query:
        return measurements[:limit] if limit else measurements
    
    # Simple local search
    search_lower = search_query.lower()
    filtered = [
        m for m in measurements
        if search_lower in m.get('filename', '').lower()
        or search_lower in m.get('recipe_name', '').lower()
        or search_lower in m.get('lot_id', '').lower()
    ]
    
    return filtered[:limit] if limit else filtered


def get_measurement_by_unique_key(tool_name: str, unique_key: str) -> Optional[Dict]:
    """
    Get single measurement by unique key with MongoDB optimization
    
    Args:
        tool_name: AFM tool name
        unique_key: Unique measurement key
        
    Returns:
        Measurement dictionary or None
    """
    try:
        if is_mongodb_enabled():
            client = get_mongo_client()
            if client.db:
                measurement = client.get_measurement_by_key(tool_name, unique_key)
                if measurement:
                    logger.info(f"Found measurement in MongoDB: {unique_key}")
                    return measurement
    
    except Exception as e:
        logger.error(f"MongoDB lookup error: {e}")
    
    # Fallback to file system search
    measurements = get_afm_measurements_with_fallback(tool_name)
    
    for m in measurements:
        if m.get('unique_key') == unique_key:
            return m
    
    return None


def get_measurements_by_date_range(tool_name: str, start_date: str, end_date: str) -> List[Dict]:
    """
    Get measurements within date range with MongoDB optimization
    
    Args:
        tool_name: AFM tool name
        start_date: Start date (YYMMDD)
        end_date: End date (YYMMDD)
        
    Returns:
        List of measurements in date range
    """
    try:
        if is_mongodb_enabled():
            client = get_mongo_client()
            if client.db:
                measurements = client.get_measurements_by_date_range(tool_name, start_date, end_date)
                if measurements:
                    logger.info(f"Found {len(measurements)} measurements in date range from MongoDB")
                    return measurements
    
    except Exception as e:
        logger.error(f"MongoDB date range query error: {e}")
    
    # Fallback to file system with local filtering
    measurements = get_afm_measurements_with_fallback(tool_name)
    
    filtered = [
        m for m in measurements
        if start_date <= m.get('date', '') <= end_date
    ]
    
    return filtered


def get_recipe_statistics(tool_name: str) -> List[Dict]:
    """
    Get recipe statistics with MongoDB aggregation
    
    Args:
        tool_name: AFM tool name
        
    Returns:
        List of recipe statistics
    """
    try:
        if is_mongodb_enabled():
            client = get_mongo_client()
            if client.db:
                stats = client.get_recipe_statistics(tool_name)
                if stats:
                    logger.info(f"Got recipe statistics from MongoDB: {len(stats)} recipes")
                    return stats
    
    except Exception as e:
        logger.error(f"MongoDB aggregation error: {e}")
    
    # Fallback to local calculation
    measurements = get_afm_measurements_with_fallback(tool_name)
    
    # Calculate statistics locally
    from collections import defaultdict
    recipe_stats = defaultdict(lambda: {'count': 0, 'dates': []})
    
    for m in measurements:
        recipe = m.get('recipe_name')
        if recipe:
            recipe_stats[recipe]['count'] += 1
            recipe_stats[recipe]['dates'].append(m.get('date', ''))
    
    # Format results
    stats = []
    for recipe, data in recipe_stats.items():
        dates = sorted(data['dates'])
        stats.append({
            'recipe_name': recipe,
            'measurement_count': data['count'],
            'earliest_date': dates[0] if dates else None,
            'latest_date': dates[-1] if dates else None
        })
    
    # Sort by count
    stats.sort(key=lambda x: x['measurement_count'], reverse=True)
    
    return stats


# Example usage in routes.py:
"""
from api.utils.mongo_integration import (
    get_afm_measurements_with_fallback,
    search_measurements_with_fallback,
    get_measurement_by_unique_key
)

@app.route('/api/afm-files')
def get_afm_files():
    tool_name = request.args.get('tool', 'MAP608')
    search_query = request.args.get('search', '')
    
    if search_query:
        measurements = search_measurements_with_fallback(tool_name, search_query)
    else:
        measurements = get_afm_measurements_with_fallback(tool_name)
    
    return jsonify({
        'success': True,
        'data': measurements,
        'total': len(measurements),
        'source': 'mongodb' if is_mongodb_enabled() else 'filesystem'
    })
"""