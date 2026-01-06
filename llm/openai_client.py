from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger()


class OpenAIClient:
    """Manages OpenAI LLM and embeddings"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._llm = None
        self._embeddings = None
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get ChatOpenAI instance"""
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=self.settings.llm_model,
                temperature=0.3,
            )
            logger.info(f"✅ Initialized ChatOpenAI with model: {self.settings.llm_model}")
        return self._llm
    
    @property
    def embeddings(self) -> OpenAIEmbeddings:
        """Get OpenAI embeddings instance"""
        if self._embeddings is None:
            self._embeddings = OpenAIEmbeddings(
                model="text-embedding-3-small"
            )
            logger.info("✅ Initialized OpenAI Embeddings (text-embedding-3-small)")
        return self._embeddings