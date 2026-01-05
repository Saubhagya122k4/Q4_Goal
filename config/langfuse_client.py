from typing import Optional
from langfuse import Langfuse
from langfuse.langchain import CallbackHandler
from config.settings import Settings
from utils.logger import setup_logger

logger = setup_logger()


class LangfuseClient:
    """Manages Langfuse tracing client and callback handler"""
    
    _instance: Optional['LangfuseClient'] = None
    
    def __new__(cls, settings: Settings):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(settings)
        return cls._instance
    
    def _initialize(self, settings: Settings):
        """Initialize Langfuse client"""
        self.settings = settings
        self._client: Optional[Langfuse] = None
        self._callback_handler: Optional[CallbackHandler] = None
        
        if self._is_configured():
            try:
                # Initialize Langfuse client
                self._client = Langfuse(
                    secret_key=settings.langfuse_secret_key,
                    public_key=settings.langfuse_public_key,
                    host=settings.langfuse_base_url,
                )
                
                # Initialize callback handler (reads from environment variables)
                self._callback_handler = CallbackHandler()
                
                logger.info("✅ Langfuse tracing enabled")
                logger.info(f"   Host: {settings.langfuse_base_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Langfuse: {e}")
                self._client = None
                self._callback_handler = None
        else:
            logger.warning("⚠️  Langfuse not configured - tracing disabled")
    
    def _is_configured(self) -> bool:
        """Check if Langfuse is properly configured"""
        return all([
            self.settings.langfuse_secret_key,
            self.settings.langfuse_public_key,
            self.settings.langfuse_base_url,
        ])
    
    @property
    def client(self) -> Optional[Langfuse]:
        """Get Langfuse client instance"""
        return self._client
    
    @property
    def callback_handler(self) -> Optional[CallbackHandler]:
        """Get Langfuse callback handler for LangChain"""
        return self._callback_handler
    
    def is_enabled(self) -> bool:
        """Check if Langfuse is enabled and ready"""
        return self._client is not None and self._callback_handler is not None
    
    def flush(self):
        """Flush pending traces to Langfuse"""
        if self._client:
            try:
                self._client.flush()
                logger.debug("Flushed Langfuse traces")
            except Exception as e:
                logger.error(f"Error flushing Langfuse traces: {e}")
    
    def shutdown(self):
        """Shutdown Langfuse client"""
        if self._client:
            try:
                self.flush()
                self._client.shutdown()
                logger.info("Langfuse client shutdown")
            except Exception as e:
                logger.error(f"Error shutting down Langfuse: {e}")