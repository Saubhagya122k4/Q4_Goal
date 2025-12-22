"""
Script to verify your .env configuration
Run this before starting the bot to check if all API keys are set correctly
"""
import os
from dotenv import load_dotenv

print("=" * 60)
print("🔍 Checking Environment Configuration")
print("=" * 60)

# Load .env file
load_dotenv()

# Check all required variables
checks = {
    "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
    "MONGO_URI": os.getenv("MONGO_URI", "mongodb://localhost:27017"),
    "DB_NAME": os.getenv("DB_NAME", "telegram_bot_langmem"),
}

all_good = True

for key, value in checks.items():
    if value:
        # Show only first/last few chars for security
        if len(value) > 20:
            masked = f"{value[:8]}...{value[-8:]}"
        else:
            masked = f"{value[:4]}...{value[-4:]}"
        print(f"✅ {key}: {masked}")
    else:
        print(f"❌ {key}: NOT SET")
        all_good = False

print("=" * 60)

if all_good:
    print("✨ All environment variables are set correctly!")
    print("   You can now run: python bot.py")
else:
    print("⚠️  Some environment variables are missing!")
    print("   Please check your .env file and make sure all keys are set.")
    print("\n📝 Your .env file should look like this:")
    print("-" * 60)
    print("""
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
GOOGLE_API_KEY=AIzaSyD_your_key_here
OPENAI_API_KEY=sk-proj-your_key_here
MONGO_URI=mongodb://localhost:27017
DB_NAME=telegram_bot_langmem
    """)
    print("-" * 60)

print()