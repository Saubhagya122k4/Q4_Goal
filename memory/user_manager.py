from datetime import datetime
from typing import Dict, Optional, Any
from storage.stores import UserProfileStore, MemoryStore
from utils.logger import setup_logger

logger = setup_logger()


class UserManager:
    """Manages user profiles and interactions"""
    
    def __init__(self, profile_store: UserProfileStore, memory_store: MemoryStore):
        self.profile_store = profile_store
        self.memory_store = memory_store
    
    async def store_user_profile(self, user_metadata: Dict[str, Any]) -> None:
        """Store or update user's Telegram profile"""
        try:
            user_id = user_metadata.get('user_id')
            
            profile_memory = {
                "content": f"Telegram User Profile: {user_metadata.get('full_name', 'N/A')} (@{user_metadata.get('username', 'N/A')}, ID: {user_id})",
                "telegram_data": {
                    "user_id": user_id,
                    "username": user_metadata.get('username'),
                    "full_name": user_metadata.get('full_name'),
                },
                "last_updated": datetime.now().isoformat(),
                "profile_type": "telegram_user_profile"
            }
            
            namespace = ("profiles",)
            await self.profile_store.store.aput(
                namespace=namespace,
                key=f"profile_{user_id}",
                value=profile_memory
            )
            
            logger.info(f"Stored/Updated profile for user {user_id} (@{user_metadata.get('username')})")
            
        except Exception as e:
            logger.error(f"Error storing user profile for {user_metadata.get('user_id')}: {e}", exc_info=True)
    
    async def store_chat_context(self, chat_id: str, user_metadata: Dict[str, Any]) -> None:
        """Store chat context - track which users participate in which chats"""
        try:
            user_id = user_metadata.get('user_id')
            chat_type = user_metadata.get('chat_type')
            chat_title = user_metadata.get('chat_title', 'Unknown Chat')
            
            chat_context = {
                "content": f"User {user_metadata.get('full_name')} (@{user_metadata.get('username')}, ID: {user_id}) is member of {chat_title} (Chat ID: {chat_id}, Type: {chat_type})",
                "chat_data": {
                    "chat_id": chat_id,
                    "chat_type": chat_type,
                    "chat_title": chat_title,
                },
                "user_data": {
                    "user_id": user_id,
                    "username": user_metadata.get('username'),
                    "full_name": user_metadata.get('full_name'),
                },
                "last_activity": datetime.now().isoformat(),
            }
            
            namespace = ("chat_memberships",)
            await self.profile_store.store.aput(
                namespace=namespace,
                key=f"chat_{chat_id}_user_{user_id}",
                value=chat_context
            )
            
            logger.debug(f"Updated chat context for user {user_id} in chat {chat_id}")
            
        except Exception as e:
            logger.error(f"Error storing chat context: {e}", exc_info=True)
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user's stored Telegram profile"""
        try:
            namespace = ("profiles",)
            profile = await self.profile_store.store.aget(
                namespace=namespace,
                key=f"profile_{user_id}"
            )
            return profile.value if profile else None
            
        except Exception as e:
            logger.error(f"Error retrieving user profile for {user_id}: {e}", exc_info=True)
            return None
    
    async def update_interaction_count(self, user_id: str) -> None:
        """Track number of interactions with the bot"""
        try:
            namespace = ("profiles",)
            stats_key = f"stats_{user_id}"
            stats = await self.profile_store.store.aget(namespace=namespace, key=stats_key)
            
            if stats:
                interaction_count = stats.value.get('interaction_count', 0) + 1
                first_interaction = stats.value.get('first_interaction')
            else:
                interaction_count = 1
                first_interaction = datetime.now().isoformat()
            
            stats_value = {
                "interaction_count": interaction_count,
                "first_interaction": first_interaction,
                "last_interaction": datetime.now().isoformat(),
            }
            
            await self.profile_store.store.aput(
                namespace=namespace,
                key=stats_key,
                value=stats_value
            )
            
            logger.debug(f"Updated interaction count for user {user_id}: {interaction_count}")
            
        except Exception as e:
            logger.error(f"Error updating interaction count for {user_id}: {e}", exc_info=True)