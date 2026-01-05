from datetime import datetime
from typing import Dict, Any, List
from langchain.agents import create_agent
from langgraph.checkpoint.mongodb import MongoDBSaver
from langmem import create_manage_memory_tool, create_search_memory_tool
from agents.base_agent import BaseAgent
from storage.mongodb_client import MongoDBClient
from storage.stores import MemoryStore
from config.settings import Settings
from llm.openai_client import OpenAIClient
from prompts.langmem_prompt import SystemPrompts
from utils.logger import setup_logger

logger = setup_logger()


class LangMemAgent(BaseAgent):
    """
    Agent with LangMem long-term memory capabilities.
    Provides per-chat scoped memory isolation and static system prompts.
    """

    def __init__(
        self,
        settings: Settings,
        db_client: MongoDBClient,
        memory_store: MemoryStore,
    ):
        self.settings = settings
        self.db_client = db_client
        self.memory_store = memory_store

        # Initialize OpenAI client and get LLM from it
        self.openai_client = OpenAIClient(settings)
        self.llm = self.openai_client.llm

        # MongoDB checkpointing for tool/agent state
        self.checkpointer = MongoDBSaver(
            client=db_client.client,
            db_name=settings.db_name,
            checkpoint_collection_name="checkpoints",
        )

        # Static system prompt
        self._static_system_prompt = SystemPrompts.get_static_system_prompt()

        logger.info("LangMemAgent initialized with shared OpenAI LLM client")

    # ---------- INTERNAL HELPERS ----------

    def _create_memory_tools(self, namespace: tuple) -> List[Any]:
        """
        Create a pair of memory tools bound to a namespace.
        """
        return [
            create_manage_memory_tool(
                store=self.memory_store.store,
                namespace=namespace,
            ),
            create_search_memory_tool(
                store=self.memory_store.store,
                namespace=namespace,
            ),
        ]

    def _create_agent_with_tools(self, tools: List[Any]):
        """
        Create an agent configured with the given tools.
        """
        return create_agent(
            self.llm,
            tools=tools,
            checkpointer=self.checkpointer,
            system_prompt=self._static_system_prompt,
            debug=True,
        )

    async def _prepare_messages(
        self,
        user_input: str,
        user_metadata: Dict[str, Any],
    ) -> List[Dict[str, str]]:
        """
        Build the contextual user message including metadata.
        """
        current_datetime = datetime.now().strftime(
            "%A, %B %d, %Y at %I:%M %p"
        )

        chat_type = user_metadata.get("chat_type", "unknown")
        chat_title = user_metadata.get("chat_title", "a chat")
        chat_id = user_metadata.get("chat_id")
        user_id = user_metadata.get("user_id")
        username = user_metadata.get("username", "N/A")
        full_name = user_metadata.get("full_name", "N/A")

        contextual_header = (
            f"Context:\n"
            f"- Time: {current_datetime}\n"
            f"- User: {full_name} (@{username}, ID: {user_id})\n"
            f"- Chat: {chat_title} (ID: {chat_id}, Type: {chat_type})\n\n"
        )

        formatted_user_message = SystemPrompts.format_user_message(
            user_input, user_metadata
        )

        return [
            {
                "role": "user",
                "content": contextual_header + formatted_user_message,
            }
        ]

    # ---------- PUBLIC API ----------

    async def get_response(
        self,
        chat_id: str,
        user_id: str,
        user_input: str,
        user_metadata: Dict[str, Any],
    ) -> str:
        """
        Generate a response using per-chat memory and scoped tools.
        """

        try:
            # Prepare full message context
            messages = await self._prepare_messages(user_input, user_metadata)

            # Define per-chat namespace
            namespace = (f"chat_{chat_id}")

            # Build chat-scoped memory tools
            memory_tools = self._create_memory_tools(namespace)

            # Build agent bound to those tools
            agent = self._create_agent_with_tools(memory_tools)

            config = {
                "configurable": {
                    "thread_id": f"telegram_chat_{chat_id}",
                    "user_id": user_id,
                    "chat_id": chat_id,
                }
            }

            result = await agent.ainvoke(
                {
                    "messages": messages,
                    "user_metadata": user_metadata,
                },
                config=config,
            )

            last_message = result["messages"][-1]
            response = last_message.content

            logger.debug(
                f"Agent response generated successfully for chat_id={chat_id}"
            )

            return response

        except Exception as exc:
            logger.error(
                f"LangMemAgent failed for user={user_id}, chat={chat_id}: {exc}",
                exc_info=True,
            )
            raise RuntimeError(
                "Failed to generate agent response. Check logs for details."
            ) from exc

    def create_system_prompt(self, user_metadata: Dict[str, Any]) -> str:
        """Return the system prompt (static for now, can be extended with metadata)."""
        # Use the static system prompt; extend using user_metadata if needed
        return self._static_system_prompt
