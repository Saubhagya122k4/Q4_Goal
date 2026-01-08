from datetime import datetime
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent as create_react_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from langmem import create_manage_memory_tool, create_search_memory_tool
from agents.base_agent import BaseAgent
from storage.mongodb_client import MongoDBClient
from storage.stores import MemoryStore
from config.settings import Settings
from prompts.langmem_prompt import SystemPrompts
from utils.logger import setup_logger

logger = setup_logger()


class LangMemAgent(BaseAgent):
    """Agent with LangMem memory capabilities"""
    
    def __init__(
        self, 
        settings: Settings, 
        db_client: MongoDBClient, 
        memory_store: MemoryStore
    ):
        self.settings = settings
        self.db_client = db_client
        self.memory_store = memory_store
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.llm_model,
            temperature=0.3
        )
        
        # Initialize checkpointer
        self.checkpointer = MongoDBSaver(
            client=db_client.client,
            db_name=settings.db_name,
            checkpoint_collection_name="checkpoints"
        )
        
        # Create memory tools
        self.memory_tools = [
            create_manage_memory_tool(namespace=("user_memories",)),
            create_search_memory_tool(namespace=("user_memories",)),
        ]
        
        # Create agent
        self.agent = create_react_agent(
            self.llm,
            tools=self.memory_tools,
            checkpointer=self.checkpointer,
            store=self.memory_store.store,
        )
        
        logger.info(f"Created LangMemAgent with {len(self.memory_tools)} memory tools")
    
    def create_system_prompt(self, user_metadata: Dict[str, Any]) -> str:
        """Create system prompt with user context"""
        return SystemPrompts.get_langmem_agent_prompt(user_metadata)
    
    async def _search_memories(self, user_metadata: Dict[str, Any], query: str) -> str:
        """Search for relevant memories"""
        try:
            user_id = user_metadata.get('user_id')
            chat_id = user_metadata.get('chat_id')
            chat_title = user_metadata.get('chat_title', '')
            
            search_query = f"{query} user {user_id} chat {chat_id} {chat_title}"
            query_embedding = await self.db_client.embeddings.aembed_query(search_query)
            
            db = self.db_client.client[self.settings.db_name]
            collection = db["langmem_store"]
            
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
                    return "\n".join([
                        f"- {doc.get('value', {}).get('content', str(doc.get('value', {})))}" 
                        for doc in results
                    ])
                else:
                    return "No relevant memories found."
                    
            except Exception:
                logger.warning("Vector search not available, using basic search")
                # Fallback to basic search
                results = list(collection.find({
                    "$or": [
                        {"key": {"$regex": str(user_id)}},
                        {"key": {"$regex": str(chat_id)}},
                        {"value.content": {"$regex": f".*{user_id}.*|.*{chat_id}.*", "$options": "i"}}
                    ]
                }).limit(10))
                
                if results:
                    return "\n".join([
                        f"- {doc.get('value', {}).get('content', str(doc.get('value', {})))}" 
                        for doc in results
                    ])
                else:
                    return "No relevant memories found."
                    
        except Exception as e:
            logger.error(f"Error searching memories: {e}", exc_info=True)
            return "No relevant memories found."
    
    async def _prepare_messages(
        self, 
        user_input: str, 
        user_metadata: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Prepare messages with memory context"""
        # Search for relevant memories
        memory_context = await self._search_memories(user_metadata, user_input)
        
        # Create system prompt with memories
        base_prompt = self.create_system_prompt(user_metadata)
        system_prompt = SystemPrompts.get_prompt_with_memories(base_prompt, memory_context)
        
        # Format user message
        user_message = SystemPrompts.format_user_message(user_input, user_metadata)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
    
    async def get_response(
        self, 
        chat_id: str, 
        user_id: str, 
        user_input: str, 
        user_metadata: Dict[str, Any]
    ) -> str:
        """Get response from the agent"""
        try:
            # Prepare messages
            messages = await self._prepare_messages(user_input, user_metadata)
            
            # Configure agent
            config = {
                "configurable": {
                    "thread_id": f"telegram_chat_{chat_id}",
                    "user_id": user_id,
                    "chat_id": chat_id,
                }
            }
            
            logger.debug(f"Invoking agent for user {user_id} in chat {chat_id}")
            
            # Invoke agent
            result = await self.agent.ainvoke(
                {
                    "messages": messages,
                    "user_metadata": user_metadata,
                },
                config=config
            )
            
            # Extract response
            last_message = result["messages"][-1]
            response_content = last_message.content
            
            logger.debug(f"Agent response generated for chat {chat_id}")
            return response_content
            
        except Exception as e:
            logger.error(f"Error in get_response for user {user_id} in chat {chat_id}: {e}", exc_info=True)
            raise