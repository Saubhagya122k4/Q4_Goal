"""Main entry point for the Telegram bot"""

import asyncio
import signal
from config.settings import Settings
from storage.mongodb_client import MongoDBClient
from storage.stores import MemoryStore, UserProfileStore
from memory.user_manager import UserManager
from agents.langmem_agent import LangMemAgent
from langchain_openai import OpenAIEmbeddings
from bot.telegram_bot import TelegramBot
from utils.logger import setup_logger


async def initialize_app():
    """Initialize all async components"""
    logger = setup_logger()
    logger.info("Starting Telegram Bot Application")
    
    try:
        # Load settings
        settings = Settings.from_env()
        logger.info(f"Loaded settings - Database: {settings.db_name}")
        
        # Initialize MongoDB client
        db_client = MongoDBClient()
        await db_client.initialize(settings.mongo_uri)
        
        # Initialize embeddings
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # Initialize stores
        memory_store = MemoryStore(db_client, settings.db_name, embedder=embeddings)
        await memory_store.initialize()
        
        profile_store = UserProfileStore(db_client, settings.db_name)
        await profile_store.initialize()
        
        # Initialize user manager
        user_manager = UserManager(profile_store, memory_store)
        
        # Initialize agent
        agent = LangMemAgent(settings, db_client, memory_store)
        await agent.initialize()
        
        # Initialize bot
        bot = TelegramBot(settings, agent, user_manager)
        
        return bot, db_client
        
    except Exception as e:
        logger.error(f"Failed to initialize app: {e}", exc_info=True)
        raise


async def main():
    """Main entry point"""
    logger = setup_logger()
    db_client = None
    bot = None
    
    try:
        bot, db_client = await initialize_app()
        await bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except asyncio.CancelledError:
        logger.info("Bot task cancelled")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        if db_client:
            await db_client.close()
        logger.info("Application shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")