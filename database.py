import logging
from pymongo import MongoClient
import config

logger = logging.getLogger(__name__)

# Initialize MongoDB client with a strict 5-second connection timeout profile
try:
    client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
except Exception as e:
    logger.error(f"Failed to create MongoClient: {e}")
    client = None

def get_collection(collection_name: str):
    """
    Safely establishes connection and extracts the requested collection instance.
    Returns None if the MongoDB host cluster is unreachable.
    """
    if client is None:
        print(f"CRITICAL: MongoClient is not initialized.")
        return None
    try:
        # Force a network verification request ping to check if Cluster0 is alive
        client.server_info()  
        db = client[config.DB_NAME]
        return db[collection_name]
    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: Connection failed for '{collection_name}': {str(e)}")
        return None
