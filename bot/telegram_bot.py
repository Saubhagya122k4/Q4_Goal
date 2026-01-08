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
        
        # Build application
        self.app = ApplicationBuilder().token(settings.telegram_bot_token).build()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all message handlers"""
        self.app.add_handler(CommandHandler("start", self.handlers.start_handler))
        self.app.add_handler(CommandHandler("profile", self.handlers.profile_handler))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handlers.message_handler)
        )
    
    def run(self):
        """Start the bot"""
        logger.info("🤖 Telegram bot is running...")
        print("🤖 Telegram bot is running... (Press Ctrl+C to stop)")
        
        try:
            self.app.run_polling()
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot crashed: {e}", exc_info=True)