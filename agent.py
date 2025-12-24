from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.utils.config import get_store as get_context_store  # Keep for potential future use, but not here
from langmem import create_manage_memory_tool, create_search_memory_tool
from storage import get_store, get_client  # Add get_store import
from config import LLM_MODEL, DB_NAME, logger


def create_agent():
    """
    Create a LangGraph agent with LangMem memory capabilities
    """
    store = get_store()
    client = get_client()
    
    # Initialize OpenAI LLM
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=0.7
    )
    
    # Use MongoDB for checkpointing (short-term memory/conversation state)
    checkpointer = MongoDBSaver(
        client=client,
        db_name=DB_NAME,
        checkpoint_collection_name="checkpoints"
    )
    
    # Create memory tools for the agent using langmem
    # Each user will have their own namespace dynamically configured
    memory_tools = [
        create_manage_memory_tool(namespace=("user_memories",)),
        create_search_memory_tool(namespace=("user_memories",)),
    ]
    
    logger.info(f"Created agent with {len(memory_tools)} memory tools")
    
    # System prompt generator
    def get_system_prompt(user_metadata):
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        
        return f"""You are a helpful AI assistant with long-term memory capabilities powered by LangMem.

Current DateTime: {current_datetime}

Current User Information:
- User ID: {user_metadata.get('user_id')}
- Username: @{user_metadata.get('username', 'N/A')}
- Full Name: {user_metadata.get('full_name', 'N/A')}

MEMORY CAPABILITIES:
You have access to LangMem tools that allow you to:
1. **Store memories** about users, their preferences, facts, and context
2. **Search memories** to recall information about any user across all conversations
3. **Update memories** when preferences or information changes
4. **Delete memories** when information becomes obsolete

IMPORTANT INSTRUCTIONS FOR MEMORY MANAGEMENT:

When storing memories:
- ALWAYS include the user's Telegram data for context
- Use descriptive memory content that clearly states WHO and WHAT
- Include context: "User @{user_metadata.get('username', 'N/A')} (ID: {user_metadata.get('user_id')}) prefers..."
- Store preferences, important facts, personal information, and context
- Be proactive - store important information without being explicitly asked
- Use consistent formatting for similar types of information
- Store user's display name ({user_metadata.get('full_name', 'N/A')}) alongside username

Examples of good memories:
- "User @john_doe aka John Smith (ID: 123) prefers dark mode in applications"
- "User Sarah Williams (ID: 456, @sarah_w) birthday is March 15th, loves chocolate cake"
- "User @alice (Alice Johnson, ID: 789) works as a software engineer at Google, speaks Python and JavaScript"
- "User Mike Brown (ID: 321, @mike_b) allergic to peanuts, vegetarian, prefers Italian cuisine"
- "User @emma (Emma Davis, ID: 654) timezone is EST, available for calls after 6 PM"

When to store memories:
- User shares personal preferences or information
- User mentions important dates, facts, or context
- User corrects or updates previous information
- User expresses likes, dislikes, or interests
- User shares work, hobbies, or lifestyle information
- First interaction with the user (store their Telegram profile data)

When searching memories:
- Before answering questions about past conversations
- When user asks "do you remember..." or similar queries
- To provide personalized responses based on known preferences
- When user mentions another person by name or username
- Use the user's full name or username for better search results

Be conversational and natural. Don't announce that you're storing memories unless asked.
Provide helpful, context-aware responses using the information you've stored.
When greeting returning users, acknowledge that you remember them using their preferred name."""

    async def prompt_with_memories(state):
        """Prepare messages with system prompt and memory search"""
        # Use the global store instead of get_context_store()
        store = get_store()
        
        # Search for relevant memories based on the last user message
        user_metadata = state.get("user_metadata", {})
        user_id = user_metadata.get('user_id')
        if state["messages"]:
            last_msg = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else str(state["messages"][-1])
            try:
                # Use async search in global namespace, filter by user_id in query if needed
                memories = await store.asearch(
                    ("user_memories",),
                    query=f"{last_msg} user {user_id}",  # Include user_id for relevance
                    limit=5
                )
                memory_context = "\n".join([f"- {mem.value.get('content', str(mem.value))}" for mem in memories]) if memories else "No relevant memories found."
            except:
                memory_context = "No relevant memories found."
        else:
            memory_context = "No relevant memories found."
        
        # Get user metadata from config (will be set during invocation)
        user_metadata = state.get("user_metadata", {})
        system_msg = get_system_prompt(user_metadata)
        
        # Add memory context to system message
        system_msg_with_memories = f"""{system_msg}

## Retrieved Memories
<memories>
{memory_context}
</memories>"""
        
        return [{"role": "system", "content": system_msg_with_memories}, *state["messages"]]

    agent = create_react_agent(
        llm,
        tools=memory_tools,
        checkpointer=checkpointer,
        store=store,
    )
    
    return agent, get_system_prompt, prompt_with_memories


# Global agent instance
agent, get_system_prompt, prompt_with_memories = create_agent()


async def get_agent_response(user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get response from the agent with LangMem memory context
    """
    try:
        # Prepare initial messages
        messages = [
            {"role": "user", "content": user_input}
        ]
        
        # Prepare full messages with system prompt and memories
        state = {
            "messages": messages,
            "user_metadata": user_metadata,
        }
        full_messages = await prompt_with_memories(state)
        
        # Invoke agent with thread_id and user_metadata in state
        config = {
            "configurable": {
                "thread_id": f"telegram_user_{user_id}",
                "user_id": user_id,
            }
        }
        
        logger.debug(f"Invoking agent for user {user_id}")
        
        result = await agent.ainvoke(
            {
                "messages": full_messages,
                "user_metadata": user_metadata,  # Pass metadata in state
            },
            config=config
        )
        
        # Extract the last message content
        last_message = result["messages"][-1]
        response_content = last_message.content
        
        logger.debug(f"Agent response generated: {response_content}...")
        
        return response_content
        
    except Exception as e:
        logger.error(f"Error in get_agent_response for user {user_id}: {e}", exc_info=True)
        raise
  

async def search_user_memories(user_id: str, query: str, limit: int = 5):
    """
    Utility function to search memories for a specific user
    Uses the store directly to search memories
    """
    try:
        from storage import get_store
        store = get_store()
        user_namespace = ("user_memories",)  # Change to global
        memories = await store.asearch(namespace=user_namespace, query=f"{query} user {user_id}", limit=limit)  # Filter by user
        return memories
    except Exception as e:
        logger.error(f"Error searching memories for user {user_id}: {e}", exc_info=True)
        return []


async def get_all_user_memories(user_id: str):
    """
    Utility function to get all memories for a specific user
    Uses the store directly to list memories
    """
    try:
        from storage import get_store
        store = get_store()
        user_namespace = ("user_memories",)  # Change to global
        memories = []
        async for item in store.alist(namespace_prefix=user_namespace):
            if str(user_id) in item.key or f"user {user_id}" in str(item.value):  # Filter by user
                memories.append(item)
        return memories
    except Exception as e:
        logger.error(f"Error getting all memories for user {user_id}: {e}", exc_info=True)
        return []