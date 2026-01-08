from agent import get_agent_response
from config import logger
from user_manager import store_user_profile, update_user_interaction_count


async def get_response(user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get AI response using LangMem-powered agent for persistent memory
    """
    try:
        logger.info(f"Processing message from user {user_id} (@{user_metadata.get('username', 'N/A')})")
        
        # Store/update user profile in memory
        await store_user_profile(user_metadata)
        
        # Update interaction tracking
        await update_user_interaction_count(user_id)
        
        # Use the agent with LangMem capabilities
        response = await get_agent_response(user_id, user_input, user_metadata)
        
        logger.info(f"Generated response for user {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing message for user {user_id}: {e}", exc_info=True)
        raise