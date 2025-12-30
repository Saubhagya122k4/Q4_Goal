from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseAgent(ABC):
    """Base class for AI agents"""
    
    @abstractmethod
    async def get_response(
        self, 
        chat_id: str, 
        user_id: str, 
        user_input: str, 
        user_metadata: Dict[str, Any]
    ) -> str:
        """Get response from the agent"""
        pass
    
    @abstractmethod
    def create_system_prompt(self, user_metadata: Dict[str, Any]) -> str:
        """Create system prompt for the agent"""
        pass