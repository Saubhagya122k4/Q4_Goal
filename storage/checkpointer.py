from langgraph.checkpoint.mongodb import MongoDBSaver
from storage.mongodb_client import MongoDBClient
from utils.logger import setup_logger

logger = setup_logger()


class CheckpointerManager:
    """Manages LangGraph checkpoint storage"""
    
    def __init__(self, db_client: MongoDBClient, db_name: str):
        self.db_client = db_client
        self.db_name = db_name
        self._checkpointer = None
    
    @property
    def checkpointer(self) -> MongoDBSaver:
        """Get or create MongoDBSaver instance"""
        if self._checkpointer is None:
            self._checkpointer = MongoDBSaver(
                client=self.db_client.client,
                db_name=self.db_name,
                checkpoint_collection_name="checkpoints"
            )
            logger.info(f"✅ Checkpointer initialized - Database: {self.db_name}")
        return self._checkpointer