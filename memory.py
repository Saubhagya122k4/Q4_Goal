from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from config import MONGO_URI, DB_NAME, COLLECTION_NAME, logger


def get_chat_history(session_id: str):
    """
    Get persistent chat history for a Telegram user
    """
    logger.debug(f"Retrieving chat history for session: {session_id}")
    return MongoDBChatMessageHistory(
        session_id=session_id,
        connection_string=MONGO_URI,
        database_name=DB_NAME,
        collection_name=COLLECTION_NAME,
    )