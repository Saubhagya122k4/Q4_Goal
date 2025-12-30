from typing import Optional
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from utils.logger import setup_logger

logger = setup_logger()


class MongoDBClient:
    """MongoDB client singleton"""
    
    _instance: Optional['MongoDBClient'] = None
    _client: Optional[MongoClient] = None
    _embeddings: Optional[OpenAIEmbeddings] = None
    
    def __new__(cls, mongo_uri: str, embeddings_model: str = "text-embedding-3-small"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(mongo_uri, embeddings_model)
        return cls._instance
    
    def _initialize(self, mongo_uri: str, embeddings_model: str):
        """Initialize MongoDB client and embeddings"""
        if self._client is None:
            self._client = MongoClient(mongo_uri)
            logger.info(f"✅ Connected to MongoDB at {mongo_uri}")
        
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(model=embeddings_model)
            logger.info(f"✅ OpenAI Embeddings initialized with model: {embeddings_model}")
    
    @property
    def client(self) -> MongoClient:
        """Get MongoDB client instance"""
        if self._client is None:
            raise RuntimeError("MongoDB client not initialized")
        return self._client
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Get embeddings instance"""
        if self._embeddings is None:
            raise RuntimeError("Embeddings not initialized")
        return self._embeddings
    
    def close(self):
        """Close MongoDB connection"""
        if self._client is not None:
            self._client.close()
            logger.info("MongoDB client connection closed")
            self._client = None
            self._embeddings = None