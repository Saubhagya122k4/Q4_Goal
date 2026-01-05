from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from config.settings import Settings
from config.langfuse_client import LangfuseClient
from utils.logger import setup_logger

logger = setup_logger()


class OpenAIClient:
    """Manages OpenAI LLM and embeddings with Langfuse tracing"""
    
    def __init__(self, settings: Settings, langfuse_client: Optional[LangfuseClient] = None):
        self.settings = settings
        self.langfuse_client = langfuse_client
        self._llm = None
        self._embeddings = None
    
    @property
    def llm(self) -> ChatOpenAI:
        """Get ChatOpenAI instance with optional Langfuse callbacks"""
        if self._llm is None:
            callbacks = []
            if self.langfuse_client and self.langfuse_client.is_enabled():
                callbacks.append(self.langfuse_client.callback_handler)
            
            self._llm = ChatOpenAI(
                model=self.settings.llm_model,
                temperature=0.3,
                callbacks=callbacks if callbacks else None,
            )
            logger.info(f"✅ Initialized ChatOpenAI with model: {self.settings.llm_model}")
            if callbacks:
                logger.info("   Langfuse tracing: Enabled")
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