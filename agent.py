from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.utils.config import get_store as get_context_store
from langmem import create_manage_memory_tool, create_search_memory_tool
from storage import get_store, get_client, get_embeddings
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
    memory_tools = [
        create_manage_memory_tool(namespace=("user_memories",)),
        create_search_memory_tool(namespace=("user_memories",)),
    ]
    
    logger.info(f"Created agent with {len(memory_tools)} memory tools")
    
    # System prompt generator
    def get_system_prompt(user_metadata):
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        chat_type = user_metadata.get('chat_type', 'unknown')
        chat_context = f"in {user_metadata.get('chat_title', 'a chat')}" if chat_type in ['group', 'supergroup'] else "in a private conversation"
        
        return f"""You are a helpful AI assistant with long-term memory capabilities powered by LangMem.

Current DateTime: {current_datetime}

Current Context:
- Chat ID: {user_metadata.get('chat_id')}
- Chat Type: {chat_type}
- Chat Title: {user_metadata.get('chat_title', 'N/A')}
- This is a {'GROUP CHAT' if chat_type in ['group', 'supergroup'] else 'PRIVATE CHAT'}

Current User Speaking:
- User ID: {user_metadata.get('user_id')}
- Username: @{user_metadata.get('username', 'N/A')}
- Full Name: {user_metadata.get('full_name', 'N/A')}

MEMORY CAPABILITIES:
You have access to LangMem tools that allow you to:
1. **Store memories** about users, their preferences, facts, and context
2. **Search memories** to recall information about any user across all conversations
3. **Update memories** when preferences or information changes
4. **Delete memories** when information becomes obsolete

IMPORTANT INSTRUCTIONS FOR GROUP CHAT MEMORY MANAGEMENT:

When storing memories in group chats:
- ALWAYS include BOTH the user's identity AND the chat context
- Format: "In {user_metadata.get('chat_title', 'group')} (Chat ID: {user_metadata.get('chat_id')}), User @{user_metadata.get('username', 'N/A')} ({user_metadata.get('full_name', 'N/A')}, ID: {user_metadata.get('user_id')}) [action/preference]"
- Track which user said what in which group
- Store group-level preferences separately from individual preferences
- Remember group discussions and decisions

Examples of good memories for group chats:
- "In Project Team Chat (Chat ID: -100123), User @john_doe (John Smith, ID: 123) prefers morning standup meetings at 9 AM"
- "In Gaming Squad (Chat ID: -100456), User @alice (Alice Johnson, ID: 789) is the team leader, coordinates strategy"
- "In Book Club (Chat ID: -100789), User @sarah (Sarah Williams, ID: 456) recommended 'The Great Gatsby', loves classic literature"
- "In Family Group (Chat ID: -100321), User @mike (Mike Brown, ID: 321) is vegetarian, allergic to peanuts"

When storing memories for individual users (across all chats):
- Store personal preferences that apply everywhere
- Format: "User @{user_metadata.get('username', 'N/A')} ({user_metadata.get('full_name', 'N/A')}, ID: {user_metadata.get('user_id')}) [global preference]"
- Example: "User @john_doe (John Smith, ID: 123) timezone is EST, works as software engineer"

When to store memories:
- User shares preferences or information {chat_context}
- Important group decisions or agreements
- User roles or responsibilities in the group
- User mentions another group member by name or username
- First interaction with a user in this chat

When searching memories:
- Search for both user-specific AND chat-specific memories
- When answering about group history, search by chat title or chat ID
- When answering about a specific user, search by username or full name
- Include context from both individual and group memories

Be conversational and natural. Acknowledge the group context when relevant.
Provide helpful responses using both individual user preferences and group conversation history."""

    async def prompt_with_memories(state):
        """Prepare messages with system prompt and memory search"""
        store = get_store()
        embeddings = get_embeddings()
        
        # Search for relevant memories based on the last user message
        user_metadata = state.get("user_metadata", {})
        user_id = user_metadata.get('user_id')
        chat_id = user_metadata.get('chat_id')
        chat_title = user_metadata.get('chat_title', '')
        
        if state["messages"]:
            last_msg = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else str(state["messages"][-1])
            try:
                # Search for memories using vector similarity
                search_query = f"{last_msg} user {user_id} chat {chat_id} {chat_title}"
                
                # Get embedding for the query
                query_embedding = await embeddings.aembed_query(search_query)
                
                # Search in the store's MongoDB collection directly
                from pymongo import DESCENDING
                client = get_client()
                db = client[DB_NAME]
                collection = db["langmem_store"]
                
                # Perform vector search if supported, otherwise get recent items
                try:
                    # Try vector search
                    pipeline = [
                        {
                            "$vectorSearch": {
                                "index": "vector_index",
                                "path": "embedding",
                                "queryVector": query_embedding,
                                "numCandidates": 50,
                                "limit": 10
                            }
                        }
                    ]
                    results = list(collection.aggregate(pipeline))
                    
                    if results:
                        memory_context = "\n".join([
                            f"- {doc.get('value', {}).get('content', str(doc.get('value', {})))}" 
                            for doc in results
                        ])
                    else:
                        memory_context = "No relevant memories found."
                        
                except Exception as vector_error:
                    logger.warning(f"Vector search not available, using basic search: {vector_error}")
                    # Fallback to basic text search
                    results = list(collection.find(
                        {
                            "$or": [
                                {"key": {"$regex": str(user_id)}},
                                {"key": {"$regex": str(chat_id)}},
                                {"value.content": {"$regex": f".*{user_id}.*|.*{chat_id}.*", "$options": "i"}}
                            ]
                        }
                    ).limit(10))
                    
                    if results:
                        memory_context = "\n".join([
                            f"- {doc.get('value', {}).get('content', str(doc.get('value', {})))}" 
                            for doc in results
                        ])
                    else:
                        memory_context = "No relevant memories found."
                        
            except Exception as e:
                logger.error(f"Error searching memories: {e}", exc_info=True)
                memory_context = "No relevant memories found."
        else:
            memory_context = "No relevant memories found."
        
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


async def get_agent_response(chat_id: str, user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get response from the agent with LangMem memory context
    
    Args:
        chat_id: The chat/group ID (used for conversation thread)
        user_id: The individual user ID
        user_input: The message text
        user_metadata: User and chat metadata
    """
    try:
        # Prepare initial messages with user identifier in group chats
        chat_type = user_metadata.get('chat_type', 'private')
        username = user_metadata.get('username', 'User')
        full_name = user_metadata.get('full_name', 'User')
        
        # In group chats, prefix messages with who is speaking
        if chat_type in ['group', 'supergroup']:
            prefixed_input = f"[{full_name} (@{username})]: {user_input}"
        else:
            prefixed_input = user_input
        
        messages = [
            {"role": "user", "content": prefixed_input}
        ]
        
        # Prepare full messages with system prompt and memories
        state = {
            "messages": messages,
            "user_metadata": user_metadata,
        }
        full_messages = await prompt_with_memories(state)
        
        # Use chat_id for thread (shared group context)
        # Store user_id for tracking who said what
        config = {
            "configurable": {
                "thread_id": f"telegram_chat_{chat_id}",
                "user_id": user_id,
                "chat_id": chat_id,
            }
        }
        
        logger.debug(f"Invoking agent for user {user_id} in chat {chat_id}")
        
        result = await agent.ainvoke(
            {
                "messages": full_messages,
                "user_metadata": user_metadata,
            },
            config=config
        )
        
        # Extract the last message content
        last_message = result["messages"][-1]
        response_content = last_message.content
        
        logger.debug(f"Agent response generated for chat {chat_id}: {response_content[:50]}...")
        
        return response_content
        
    except Exception as e:
        logger.error(f"Error in get_agent_response for user {user_id} in chat {chat_id}: {e}", exc_info=True)
        raise
  

async def search_user_memories(user_id: str, query: str, limit: int = 5):
    """
    Utility function to search memories for a specific user
    """
    try:
        client = get_client()
        db = client[DB_NAME]
        collection = db["langmem_store"]
        
        results = list(collection.find(
            {"key": {"$regex": str(user_id)}}
        ).limit(limit))
        
        return results
    except Exception as e:
        logger.error(f"Error searching memories for user {user_id}: {e}", exc_info=True)
        return []


async def search_chat_memories(chat_id: str, query: str, limit: int = 10):
    """
    Utility function to search memories for a specific chat/group
    """
    try:
        client = get_client()
        db = client[DB_NAME]
        collection = db["langmem_store"]
        
        results = list(collection.find(
            {"key": {"$regex": str(chat_id)}}
        ).limit(limit))
        
        return results
    except Exception as e:
        logger.error(f"Error searching memories for chat {chat_id}: {e}", exc_info=True)
        return []


async def get_all_user_memories(user_id: str):
    """
    Utility function to get all memories for a specific user
    """
    try:
        client = get_client()
        db = client[DB_NAME]
        collection = db["langmem_store"]
        
        results = list(collection.find(
            {
                "$or": [
                    {"key": {"$regex": str(user_id)}},
                    {"value.content": {"$regex": str(user_id)}}
                ]
            }
        ))
        
        return results
    except Exception as e:
        logger.error(f"Error getting all memories for user {user_id}: {e}", exc_info=True)
        return []