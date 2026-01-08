from storage import get_store, get_user_profile_store
from config import logger
from datetime import datetime


async def store_user_profile(user_metadata: dict):
    """
    Store or update user's Telegram profile in user_profiles collection
    This creates a persistent record of the user's Telegram data
    """
    try:
        # Use dedicated user profile store
        profile_store = get_user_profile_store()
        user_id = user_metadata.get('user_id')
        
        # Create a user profile memory
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
        
        # Store in user profiles collection
        namespace = ("profiles",)
        await profile_store.aput(
            namespace=namespace,
            key=f"profile_{user_id}",
            value=profile_memory
        )
        
        logger.info(f"Stored/Updated profile for user {user_id} (@{user_metadata.get('username')}) in user_profiles collection")
        
    except Exception as e:
        logger.error(f"Error storing user profile for {user_metadata.get('user_id')}: {e}", exc_info=True)


async def store_chat_context(chat_id: str, user_metadata: dict):
    """
    Store chat context - track which users participate in which chats
    Stored in user_profiles collection for organizational purposes
    """
    try:
        profile_store = get_user_profile_store()
        user_id = user_metadata.get('user_id')
        chat_type = user_metadata.get('chat_type')
        chat_title = user_metadata.get('chat_title', 'Unknown Chat')
        
        # Store chat membership
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
        await profile_store.aput(
            namespace=namespace,
            key=f"chat_{chat_id}_user_{user_id}",
            value=chat_context
        )
        
        logger.debug(f"Updated chat context for user {user_id} in chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error storing chat context: {e}", exc_info=True)


async def get_user_profile(user_id: str):
    """
    Retrieve user's stored Telegram profile from user_profiles collection
    """
    try:
        profile_store = get_user_profile_store()
        namespace = ("profiles",)
        
        profile = await profile_store.aget(
            namespace=namespace,
            key=f"profile_{user_id}"
        )
        
        return profile.value if profile else None
        
    except Exception as e:
        logger.error(f"Error retrieving user profile for {user_id}: {e}", exc_info=True)
        return None


async def update_user_interaction_count(user_id: str):
    """
    Track number of interactions with the bot in user_profiles collection
    """
    try:
        profile_store = get_user_profile_store()
        namespace = ("profiles",)
        
        # Get current stats or create new
        stats_key = f"stats_{user_id}"
        stats = await profile_store.aget(namespace=namespace, key=stats_key)
        
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
        
        await profile_store.aput(
            namespace=namespace,
            key=stats_key,
            value=stats_value
        )
        
        logger.debug(f"Updated interaction count for user {user_id}: {interaction_count} in user_profiles collection")
        
    except Exception as e:
        logger.error(f"Error updating interaction count for {user_id}: {e}", exc_info=True)


async def store_user_preference(user_metadata: dict, preference: str):
    """
    Store a user preference in langmem_store collection
    This keeps preferences in the main memory store for AI agent access
    """
    try:
        # Use the main memory store for preferences (NOT profile store)
        store = get_store()
        user_id = user_metadata.get('user_id')
        username = user_metadata.get('username', 'N/A')
        full_name = user_metadata.get('full_name', 'N/A')
        
        memory_content = f"User @{username} ({full_name}, ID: {user_id}) likes {preference}"
        memory = {
            "content": memory_content,
            "telegram_data": {
                "user_id": user_id,
                "username": username,
                "full_name": full_name,
            },
            "created_at": datetime.now().isoformat(),
            "type": "preference"
        }
        
        namespace = ("user_memories",)
        await store.aput(
            namespace=namespace,
            key=f"preference_{preference}_{user_id}",
            value=memory
        )
        
        logger.info(f"Stored preference for user {user_id}: {preference} in langmem_store collection")
        
    except Exception as e:
        logger.error(f"Error storing preference for {user_id}: {e}", exc_info=True)