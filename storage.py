from pymongo import MongoClient
from langgraph.store.mongodb import MongoDBStore, create_vector_index_config
from config import MONGO_URI, DB_NAME


_store = None
_client = None


def get_client():
    """
    Get or create the MongoDB client instance
    """
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
        print(f"✅ Connected to MongoDB at {MONGO_URI}")
    return _client


def get_store():
    """
    Get or create the MongoDB storage backend for LangMem.
    Uses MongoDBStore from langgraph for persistent memory.
    """
    global _store
    
    if _store is None:
        # Get client and create collection reference
        client = get_client()
        db = client[DB_NAME]
        collection = db["memory_store"]
        
        # Create proper vector index configuration
        index_config = create_vector_index_config(
            dims=1536,
            embed="openai:text-embedding-3-small",
            fields=["value"],  # This is the required field parameter
            name="vector_index",
            relevance_score_fn="cosine"
        )
        
        # Create MongoDBStore with the collection object
        _store = MongoDBStore(
            collection=collection,
            index_config=index_config
        )
        
        print(f"✅ Using MongoDB Store for persistent memory")
        print(f"   Database: {DB_NAME}")
        print(f"   Collection: memory_store")
        print(f"   Vector search enabled with OpenAI embeddings")
    
    return _store