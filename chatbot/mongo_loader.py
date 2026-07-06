from database import get_collection

def get_all_documents(limit: int = 5):
    collection = get_collection()
    if collection is None:
        return []
    docs = collection.find({}, {"_id": 0}).limit(limit)
    return list(docs)