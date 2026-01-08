from typing import Optional
from langgraph.store.mongodb import MongoDBStore, create_vector_index_config
from langchain_core.embeddings import Embeddings
from storage.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger()


class BaseStore:
    """Base class for MongoDB stores"""
    
    def __init__(
        self, 
        db_client: MongoDBClient, 
        db_name: str, 
        collection_name: str,
        embedder: Optional[Embeddings] = None
    ):
        self.db_client = db_client
        self.db_name = db_name
        self.collection_name = collection_name
        self.embedder = embedder
        self._store: Optional[MongoDBStore] = None
    
    @property
    def store(self) -> MongoDBStore:
        """Get or create MongoDBStore instance"""
        if self._store is None:
            db = self.db_client.client[self.db_name]
            collection = db[self.collection_name]
            
            # Configure vector index if embedder is available
            if self.embedder:
                index_config = create_vector_index_config(
                    dims=1536,  # text-embedding-3-small dimension
                    embed=self.embedder,
                    name="embedding",
                    relevance_score_fn="cosine"
                )
                # Set auto_index_timeout to 0 to not block on index creation
                # Index must be created manually in MongoDB Atlas
                self._store = MongoDBStore(
                    collection=collection,
                    index_config=index_config,
                    auto_index_timeout=0
                )
                logger.info(f"Vector index created in MongoDB Atlas")
            else:
                self._store = MongoDBStore(collection=collection)
                logger.info(f"⚠️  Vector index must be created manually in MongoDB Atlas")
            
            logger.info(f"✅ {self.__class__.__name__} initialized")
            logger.info(f"   Database: {self.db_name}")
            logger.info(f"   Collection: {self.collection_name}")
            logger.info(f"   Embedder: {'Enabled' if self.embedder else 'Disabled'}")
        
        return self._store


class MemoryStore(BaseStore):
    """Store for LangMem memories"""
    
    def __init__(
        self, 
        db_client: MongoDBClient, 
        db_name: str,
        embedder: Optional[Embeddings] = None
    ):
        super().__init__(db_client, db_name, "langmem_store", embedder)


class UserProfileStore(BaseStore):
    """Store for user profiles"""
    
    def __init__(self, db_client: MongoDBClient, db_name: str):
        super().__init__(db_client, db_name, "user_profiles")