from datetime import datetime
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from langmem import create_manage_memory_tool, create_search_memory_tool
from storage import get_store, get_client
from config import LLM_MODEL, DB_NAME


def create_agent():
    """
    Create a LangGraph agent with LangMem memory capabilities
    """
    store = get_store()
    client = get_client()
    
    # Use MongoDB for checkpointing (short-term memory/conversation state)
    checkpointer = MongoDBSaver(
        client=client,
        db_name=DB_NAME,
        checkpoint_collection_name="checkpoints"
    )
    
    # Create memory tools that can store info about ANY user
    memory_tools = [
        create_manage_memory_tool(
            namespace=("user_memories",)  # Shared namespace for all users
        ),
        create_search_memory_tool(
            namespace=("user_memories",)  # Search across all user memories
        ),
    ]
    
    # System prompt with datetime and instructions
    def get_system_prompt(user_metadata):
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        return f"""You are a helpful AI assistant with long-term memory capabilities.

Current DateTime: {current_datetime}

Current User Information:
- User ID: {user_metadata.get('user_id')}
- Username: @{user_metadata.get('username')}
- Name: {user_metadata.get('full_name')}
- Language: {user_metadata.get('language_code')}

MEMORY CAPABILITIES:
You have access to memory tools that allow you to:
1. Store information about ANY user (not just the current user)
2. Search for information about ANY user
3. Remember preferences, facts, and context across conversations

IMPORTANT INSTRUCTIONS:
- When a user tells you information about themselves or others, use the manage_memory tool to store it
- Store memories with clear context about WHO the information is about
- When asked about any user (by name, username, or user_id), search your memories
- Always include relevant context in memories (dates, relationships, preferences, etc.)
- Memories are shared across all conversations - you can remember info about any user
- Be proactive in storing important information without being asked

Example memory formats:
- "User @john_doe (ID: 123) prefers dark mode"
- "User Sarah (ID: 456) mentioned her birthday is March 15th"
- "User @alice works as a software engineer at Google"

Answer naturally and use your memory tools to provide personalized, context-aware responses."""

    agent = create_react_agent(
        LLM_MODEL,
        tools=memory_tools,
        checkpointer=checkpointer,
        store=store,
    )
    
    return agent, get_system_prompt


# Global agent instance
agent, get_system_prompt = create_agent()


async def get_agent_response(user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get response from the agent with memory context
    """
    # Create system message with current datetime and user context
    system_prompt = get_system_prompt(user_metadata)
    
    # Prepare messages with system prompt
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]
    
    # Invoke agent with thread_id based on user_id
    config = {
        "configurable": {
            "thread_id": f"telegram_user_{user_id}",
        }
    }
    
    result = await agent.ainvoke(
        {"messages": messages},
        config=config
    )
    
    # Extract the last message content
    last_message = result["messages"][-1]
    return last_message.content