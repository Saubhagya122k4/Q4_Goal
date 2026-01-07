from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from bot.handlers import BotHandlers
from config.settings import Settings
from agents.base_agent import BaseAgent
from memory.user_manager import UserManager
from utils.logger import setup_logger

logger = setup_logger()


class TelegramBot:
    """Telegram bot application"""
    
    def __init__(self, settings: Settings, agent: BaseAgent, user_manager: UserManager):
        self.settings = settings
        self.agent = agent
        self.user_manager = user_manager
        self.handlers = BotHandlers(agent, user_manager)
        self.app = ApplicationBuilder().token(settings.telegram_bot_token).build()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all message handlers"""
        self.app.add_handler(CommandHandler("start", self.handlers.start_handler))
        self.app.add_handler(CommandHandler("profile", self.handlers.profile_handler))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.message_handler)
        )
    
    async def run(self):
        """Start the bot with async/await"""
        logger.info("🤖 Telegram bot is running...")
        print("🤖 Telegram bot is running... (Press Ctrl+C to stop)")
        
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(allowed_updates=["message"])
        
        # Keep running until interrupted
        import asyncio
        try:
            await asyncio.Event().wait()
        except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
            logger.info("Received stop signal, shutting down...")
        finally:
            # Proper shutdown sequence
            logger.info("Stopping updater...")
            await self.app.updater.stop()
            logger.info("Stopping application...")
            await self.app.stop()
            logger.info("Shutting down application...")
            await self.app.shutdown()
            logger.info("Bot shutdown complete")