from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from agent import get_agent_response


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm an AI assistant with advanced memory.\n"
        "I can remember information about you and other users you mention.\n"
        "Just chat naturally and I'll remember important details!"
    )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = str(user.id)
    user_input = update.message.text
    
    # Collect user metadata
    user_metadata = {
        "user_id": user_id,
        "username": user.username or "N/A",
        "first_name": user.first_name or "",
        "last_name": user.last_name or "",
        "full_name": user.full_name or "N/A",
        "language_code": user.language_code or "en"
    }

    # Get response from agent
    response = await get_agent_response(user_id, user_input, user_metadata)

    await update.message.reply_text(response)


def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Telegram bot with LangMem is running...")
    app.run_polling()


if __name__ == "__main__":
    main()