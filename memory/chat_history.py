from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from utils.logger import setup_logger

logger = setup_logger()


class ChatHistoryManager:
    """Manages chat history for users"""
    
    def __init__(self, mongo_uri: str, db_name: str, collection_name: str):
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        self.collection_name = collection_name
    
    def get_chat_history(self, session_id: str) -> MongoDBChatMessageHistory:
        """Get persistent chat history for a session"""
        logger.debug(f"Retrieving chat history for session: {session_id}")
        return MongoDBChatMessageHistory(
            session_id=session_id,
            connection_string=self.mongo_uri,
            database_name=self.db_name,
            collection_name=self.collection_name,
        )