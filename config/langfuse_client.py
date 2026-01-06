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
    
    def create_user_callback_handler(
        self, 
        user_id: str, 
        session_id: str,
        user_metadata: Optional[dict] = None
    ) -> Optional[CallbackHandler]:
        """
        Create a user-specific callback handler with user context.
        
        User identification in Langfuse is done via the CallbackHandler initialization
        with user_id and session_id parameters, plus additional metadata.
        
        Args:
            user_id: Telegram user ID (will be used as Langfuse user_id)
            session_id: Session/chat identifier (will be used as Langfuse session_id)
            user_metadata: Additional user metadata (username, full_name, etc.)
        
        Returns:
            CallbackHandler configured with user context
        """
        if not self.is_enabled():
            return None
        
        try:
            # Prepare user metadata for Langfuse
            metadata = {
                "telegram_user_id": user_id,
                "session_id": session_id,
            }
            
            if user_metadata:
                # Add additional user context
                if "username" in user_metadata:
                    metadata["username"] = user_metadata["username"]
                if "full_name" in user_metadata:
                    metadata["full_name"] = user_metadata["full_name"]
                if "chat_type" in user_metadata:
                    metadata["chat_type"] = user_metadata["chat_type"]
                if "chat_title" in user_metadata:
                    metadata["chat_title"] = user_metadata["chat_title"]
                if "chat_id" in user_metadata:
                    metadata["chat_id"] = user_metadata["chat_id"]
            
            # Create callback handler with user_id and session_id
            handler = CallbackHandler(
                user_id=user_id,
                session_id=session_id,
                metadata=metadata,
            )
            
            logger.debug(
                f"Created user-specific callback handler: "
                f"user_id={user_id}, session_id={session_id}"
            )
            return handler
            
        except Exception as e:
            logger.error(f"Error creating user callback handler: {e}")
            return None
    
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
        """Shutdown Langfuse client (synchronous)"""
        if self._client:
            try:
                self.flush()
                self._client.shutdown()
                logger.info("Langfuse client shutdown")
            except Exception as e:
                logger.error(f"Error shutting down Langfuse: {e}")