"""Main entry point for the Telegram bot"""

from config.settings import Settings
from storage.mongodb_client import MongoDBClient
from storage.stores import MemoryStore, UserProfileStore
from memory.user_manager import UserManager
from agents.langmem_agent import LangMemAgent
from config.langfuse_client import LangfuseClient
from langchain_openai import OpenAIEmbeddings
from bot.telegram_bot import TelegramBot
from utils.logger import setup_logger


def main():
    """Initialize and run the bot"""
    # Setup logger
    logger = setup_logger()
    logger.info("Starting Telegram Bot Application")
    
    langfuse_client = None
    db_client = None
    
    try:
        # Load settings
        settings = Settings.from_env()
        logger.info(f"Loaded settings - Database: {settings.db_name}")
        
        # Initialize Langfuse client
        langfuse_client = LangfuseClient(settings)
        
        # Initialize MongoDB client
        db_client = MongoDBClient(settings.mongo_uri)
        
        # Initialize embeddings for semantic search
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Initialize stores (pass embeddings to MemoryStore)
        memory_store = MemoryStore(db_client, settings.db_name, embedder=embeddings)
        profile_store = UserProfileStore(db_client, settings.db_name)
        
        # Initialize user manager
        user_manager = UserManager(profile_store, memory_store)
        
        # Initialize agent with Langfuse
        agent = LangMemAgent(settings, db_client, memory_store, langfuse_client)
        
        # Initialize and run bot
        bot = TelegramBot(settings, agent, user_manager)
        bot.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        if langfuse_client:
            langfuse_client.shutdown()
        if db_client:
            db_client.close()


if __name__ == "__main__":
    main()