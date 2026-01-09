from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.synchronous.database import Database
from pymongo.synchronous.collection import Collection
from utils.logger import setup_logger

logger = setup_logger()


class MongoDBClient:
    """MongoDB client with both sync and async support"""
    
    _instance: Optional['MongoDBClient'] = None
    _async_client: Optional[AsyncIOMotorClient] = None
    _sync_client: Optional[MongoClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self, mongo_uri: str):
        """Initialize both sync and async MongoDB clients"""
        if self._async_client is None:
            # Async client for most operations
            self._async_client = AsyncIOMotorClient(mongo_uri)
            await self._async_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB (async)")
        
        if self._sync_client is None:
            # Sync client for LangGraph components
            self._sync_client = MongoClient(mongo_uri)
            self._sync_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB (sync)")
    
    @property
    def async_client(self) -> AsyncIOMotorClient:
        """Get async MongoDB client instance"""
        if self._async_client is None:
            raise RuntimeError("MongoDB async client not initialized. Call initialize() first.")
        return self._async_client
    
    @property
    def sync_client(self) -> MongoClient:
        """Get sync MongoDB client instance for LangGraph"""
        if self._sync_client is None:
            raise RuntimeError("MongoDB sync client not initialized. Call initialize() first.")
        return self._sync_client
    
    def get_sync_collection(self, db_name: str, collection_name: str) -> Collection:
        """Get a synchronous collection for LangGraph stores"""
        return self.sync_client[db_name][collection_name]
    
    async def close(self):
        """Close MongoDB connections"""
        if self._async_client is not None:
            self._async_client.close()
            logger.info("MongoDB async client connection closed")
            self._async_client = None
        
        if self._sync_client is not None:
            self._sync_client.close()
            logger.info("MongoDB sync client connection closed")
            self._sync_client = None