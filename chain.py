from agent import get_agent_response
from config import logger
from user_manager import store_user_profile, update_user_interaction_count, store_chat_context


async def get_response(chat_id: str, user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get AI response using LangMem-powered agent for persistent memory
    
    Args:
        chat_id: The chat/group ID (used for shared conversation context)
        user_id: The individual user ID (used for personal profile)
        user_input: The message text
        user_metadata: User and chat metadata
    """
    try:
        logger.info(f"Processing message from user {user_id} (@{user_metadata.get('username', 'N/A')}) in chat {chat_id} ({user_metadata.get('chat_type')})")
        
        # Store/update user profile in user_profiles collection
        await store_user_profile(user_metadata)
        
        # Store chat context (who is in which chat)
        await store_chat_context(chat_id, user_metadata)
        
        # Update interaction tracking for the user
        await update_user_interaction_count(user_id)
        
        # Use the agent with LangMem capabilities
        # Pass chat_id for shared conversation context
        response = await get_agent_response(chat_id, user_id, user_input, user_metadata)
        
        logger.info(f"Generated response for user {user_id} in chat {chat_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing message for user {user_id} in chat {chat_id}: {e}", exc_info=True)
        raise