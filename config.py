import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# LLM Configuration - Using Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

# OpenAI API Key (required for embeddings in LangMem)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set OpenAI API key in environment (required for langchain embeddings)
if OPENAI_API_KEY:
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
else:
    print("⚠️  WARNING: OPENAI_API_KEY not found in .env file!")
    print("   Memory search (embeddings) will not work without it.")

# Set Google API key in environment
if GOOGLE_API_KEY:
    os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY
else:
    print("⚠️  WARNING: GOOGLE_API_KEY not found in .env file!")

# Storage Configuration - MongoDB
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "telegram_bot_langmem")

# Collections will be:
# - memory_store: Long-term memories (LangMem)
# - checkpoints: Short-term conversation state (LangGraph)