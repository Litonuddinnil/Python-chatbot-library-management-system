from pymongo import MongoClient
import config

# Initialize MongoDB client with a strict 5-second connection timeout profile
client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)

def get_collection(collection_name: str):
    """
    Safely establishes connection and extracts the requested collection instance.
    Returns None if the MongoDB host cluster is unreachable.
    """
    try:
        # Force a network verification request ping to check if Cluster0 is alive
        client.server_info()  
        db = client[config.DB_NAME]
        return db[collection_name]
    except Exception as e:
        print(f"CRITICAL DATABASE ERROR: Connection failed for '{collection_name}': {str(e)}")
        return None