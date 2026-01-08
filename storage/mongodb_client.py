from typing import Optional
from pymongo import MongoClient
from utils.logger import setup_logger

logger = setup_logger()


class MongoDBClient:
    """MongoDB client singleton"""
    
    _instance: Optional['MongoDBClient'] = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls, mongo_uri: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(mongo_uri)
        return cls._instance
    
    def _initialize(self, mongo_uri: str):
        """Initialize MongoDB client"""
        if self._client is None:
            self._client = MongoClient(mongo_uri)
            logger.info(f"✅ Connected to MongoDB at {mongo_uri}")
    
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client instance"""
        if self._client is None:
            raise RuntimeError("MongoDB client not initialized")
        return self._client
    
    def close(self):
        """Close MongoDB connection"""
        if self._client is not None:
            self._client.close()
            logger.info("MongoDB client connection closed")
            self._client = None