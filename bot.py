from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_BOT_TOKEN, logger
from chain import get_response
from user_manager import get_user_profile


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    logger.info(f"User {user.id} (@{user.username}) started the bot in chat {chat.id} ({chat.type})")
    
    await update.message.reply_text(
        "👋 Hi! I'm an AI assistant powered by OpenAI GPT-4o Mini.\n"
        "I can remember conversations in this group and individual preferences.\n"
        "Just chat naturally and I'll help you!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    user_id = str(user.id)
    chat_id = str(chat.id)
    user_input = update.message.text
    
    logger.info(f"Received message from {user_id} (@{user.username}) in chat {chat_id} ({chat.type}): {user_input[:50]}...")
    
    # Enhanced user metadata with chat context
    user_metadata = {
        "user_id": user_id,
        "username": user.username or "N/A",
        "full_name": user.full_name or "N/A",
        "chat_id": chat_id,
        "chat_type": chat.type,  # 'private', 'group', 'supergroup', 'channel'
        "chat_title": chat.title if hasattr(chat, 'title') else "Private Chat",
    }

    try:
        # Get response from chain - uses chat_id for shared context
        response = await get_response(chat_id, user_id, user_input, user_metadata)
        await update.message.reply_text(response)
        logger.info(f"Sent response to user {user_id} in chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error handling message from user {user_id} in chat {chat_id}: {str(e)}", exc_info=True)
        await update.message.reply_text(
            "Sorry, I encountered an error processing your message. Please try again."
        )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's stored profile information"""
    user = update.effective_user
    user_id = str(user.id)
    
    logger.info(f"User {user_id} requested their profile")
    
    try:
        profile = await get_user_profile(user_id)
        
        if profile:
            telegram_data = profile.get('telegram_data', {})
            response = (
                "👤 **Your Stored Profile:**\n\n"
                f"🆔 User ID: `{telegram_data.get('user_id')}`\n"
                f"👤 Name: {telegram_data.get('full_name', 'N/A')}\n"
                f"🔖 Username: @{telegram_data.get('username', 'N/A')}\n"
                f"📅 Last Updated: {profile.get('last_updated', 'Unknown')}\n"
            )
        else:
            response = "No profile found. Send me a message first!"
        
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        logger.error(f"Error retrieving profile for {user_id}: {e}", exc_info=True)
        await update.message.reply_text("Error retrieving your profile.")


def main():
    logger.info("Starting Telegram bot...")
    
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        raise ValueError("TELEGRAM_BOT_TOKEN is required")
    
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("profile", profile))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Telegram bot is running...")
    print("🤖 Telegram bot is running... (Press Ctrl+C to stop)")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()