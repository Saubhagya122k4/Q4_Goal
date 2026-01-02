import os
from typing import Optional
from dotenv import load_dotenv
from dataclasses import dataclass


@dataclass
class Settings:
    """Application configuration settings"""
    
    # Telegram Configuration
    telegram_bot_token: str
    
    # LLM Configuration
    openai_api_key: str
    llm_model: str = "gpt-4o-mini"
    
    # MongoDB Configuration
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "telegram_bot"
    
    def __post_init__(self):
        """Set environment variables after initialization"""
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """Load settings from environment variables"""
        load_dotenv()
        
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        if not telegram_token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        return cls(
            telegram_bot_token=telegram_token,
            openai_api_key=openai_key,
            llm_model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            mongo_uri=os.getenv("MONGO_URI", "mongodb://localhost:27017"),
            db_name=os.getenv("DB_NAME", "telegram_bot"),
        )