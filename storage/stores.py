from typing import Optional
from langgraph.store.mongodb import MongoDBStore
from storage.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger()


class BaseStore:
    """Base class for MongoDB stores"""
    
    def __init__(self, db_client: MongoDBClient, db_name: str, collection_name: str):
        self.db_client = db_client
        self.db_name = db_name
        self.collection_name = collection_name
        self._store: Optional[MongoDBStore] = None
    
    @property
    def store(self) -> MongoDBStore:
        """Get or create MongoDBStore instance"""
        if self._store is None:
            db = self.db_client.client[self.db_name]
            collection = db[self.collection_name]
            
            self._store = MongoDBStore(collection=collection)
            
            logger.info(f"✅ {self.__class__.__name__} initialized")
            logger.info(f"   Database: {self.db_name}")
            logger.info(f"   Collection: {self.collection_name}")
        
        return self._store


class MemoryStore(BaseStore):
    """Store for LangMem memories"""
    
    def __init__(self, db_client: MongoDBClient, db_name: str):
        super().__init__(db_client, db_name, "langmem_store")


class UserProfileStore(BaseStore):
    """Store for user profiles"""
    
    def __init__(self, db_client: MongoDBClient, db_name: str):
        super().__init__(db_client, db_name, "user_profiles")