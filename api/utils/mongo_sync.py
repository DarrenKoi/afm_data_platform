"""
MongoDB synchronization script for AFM data
Syncs parsed AFM file data to MongoDB for fast access
"""
import logging
from pathlib import Path
from datetime import datetime

from .file_parser import load_afm_file_list
from .mongo_client import get_mongo_client, store_afm_measurements

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_tool_data_to_mongodb(tool_name='MAP608', connection_string=None):
    """
    Sync AFM data for a specific tool to MongoDB
    
    Args:
        tool_name: AFM tool name (e.g., 'MAP608', 'MAPC01')
        connection_string: MongoDB connection string (optional)
        
    Returns:
        dict: Sync results
    """
    try:
        logger.info(f"Starting MongoDB sync for tool: {tool_name}")
        
        # Load AFM file list from parsed data
        logger.info("Loading AFM measurements from file system...")
        measurements = load_afm_file_list(tool_name)
        
        if not measurements:
            logger.warning(f"No measurements found for tool: {tool_name}")
            return {
                'success': False,
                'error': 'No measurements found',
                'tool_name': tool_name
            }
        
        logger.info(f"Found {len(measurements)} measurements to sync")
        
        # Get MongoDB client
        client = get_mongo_client(connection_string)
        
        if not client.db:
            logger.error("MongoDB client not initialized")
            return {
                'success': False,
                'error': 'MongoDB connection failed',
                'tool_name': tool_name
            }
        
        # Store measurements in MongoDB
        logger.info("Storing measurements in MongoDB...")
        result = client.store_measurements(tool_name, measurements)
        
        # Add sync metadata
        result['sync_timestamp'] = datetime.utcnow().isoformat()
        result['source'] = 'file_system'
        
        logger.info(f"Sync completed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error during sync: {e}")
        return {
            'success': False,
            'error': str(e),
            'tool_name': tool_name
        }


def sync_all_tools_to_mongodb(connection_string=None):
    """
    Sync data for all configured AFM tools to MongoDB
    
    Args:
        connection_string: MongoDB connection string (optional)
        
    Returns:
        dict: Sync results for all tools
    """
    # Define all available tools
    tools = ['MAP608', 'MAPC01', '5EAP1501']
    
    results = {}
    
    for tool in tools:
        logger.info(f"\n{'='*50}")
        logger.info(f"Syncing tool: {tool}")
        logger.info(f"{'='*50}")
        
        result = sync_tool_data_to_mongodb(tool, connection_string)
        results[tool] = result
    
    # Summary
    total_success = sum(1 for r in results.values() if r.get('success', False))
    total_measurements = sum(r.get('total_processed', 0) for r in results.values())
    
    summary = {
        'timestamp': datetime.utcnow().isoformat(),
        'tools_synced': total_success,
        'total_tools': len(tools),
        'total_measurements': total_measurements,
        'results': results
    }
    
    logger.info(f"\n{'='*50}")
    logger.info("SYNC SUMMARY")
    logger.info(f"{'='*50}")
    logger.info(f"Tools synced: {total_success}/{len(tools)}")
    logger.info(f"Total measurements: {total_measurements}")
    
    return summary


def verify_mongodb_data(tool_name='MAP608', sample_size=5):
    """
    Verify MongoDB data by retrieving sample measurements
    
    Args:
        tool_name: AFM tool name
        sample_size: Number of sample measurements to retrieve
        
    Returns:
        dict: Verification results
    """
    try:
        client = get_mongo_client()
        
        if not client.db:
            return {
                'success': False,
                'error': 'MongoDB not connected'
            }
        
        # Get collection stats
        stats = client.get_collection_stats(tool_name)
        
        # Get sample measurements
        sample_measurements = client.retrieve_all_measurements(
            tool_name, 
            filters={}, 
            projection={'unique_key': 1, 'filename': 1, 'date': 1, 'recipe_name': 1}
        )[:sample_size]
        
        # Test search functionality
        if sample_measurements:
            first_recipe = sample_measurements[0].get('recipe_name', '')
            search_results = client.search_measurements(tool_name, first_recipe, limit=10)
        else:
            search_results = []
        
        return {
            'success': True,
            'tool_name': tool_name,
            'stats': stats,
            'sample_count': len(sample_measurements),
            'samples': sample_measurements,
            'search_test_count': len(search_results)
        }
        
    except Exception as e:
        logger.error(f"Error verifying MongoDB data: {e}")
        return {
            'success': False,
            'error': str(e)
        }


if __name__ == "__main__":
    # Example usage
    import os
    
    # Set MongoDB connection string (will be provided by company)
    # os.environ['MONGODB_CONNECTION_STRING'] = 'mongodb://...'
    
    # Sync single tool
    # result = sync_tool_data_to_mongodb('MAP608')
    # print(result)
    
    # Sync all tools
    # summary = sync_all_tools_to_mongodb()
    # print(summary)
    
    # Verify data
    # verification = verify_mongodb_data('MAP608')
    # print(verification)
    
    print("MongoDB sync utilities ready. Set MONGODB_CONNECTION_STRING environment variable to use.")