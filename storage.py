from pymongo import MongoClient
from langgraph.store.mongodb import MongoDBStore
from langchain_openai import OpenAIEmbeddings
from config import MONGO_URI, DB_NAME, logger


_store = None
_client = None


def get_client():
    """
    Get or create the MongoDB client instance
    """
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI)
        logger.info(f"✅ Connected to MongoDB at {MONGO_URI}")
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
        collection = db["langmem_store"]
        
        # Initialize embeddings for vector search
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Remove custom index to use defaults and avoid conflicts
        _store = MongoDBStore(
            collection=collection,
            embeddings=embeddings
        )
        
        logger.info("✅ LangMem MongoDB Store initialized")
        logger.info(f"   Database: {DB_NAME}")
        logger.info(f"   Collection: langmem_store")
        logger.info("   Vector search enabled with OpenAI embeddings")
    
    return _store


def close_connections():
    """
    Close MongoDB connections gracefully
    """
    global _client, _store
    if _client is not None:
        _client.close()
        logger.info("MongoDB client connection closed")
        _client = None
        _store = None