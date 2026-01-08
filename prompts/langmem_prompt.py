from datetime import datetime
from typing import Dict, Any


class SystemPrompts:
    """System prompts for the AI agent"""
    
    @staticmethod
    def get_langmem_agent_prompt(user_metadata: Dict[str, Any]) -> str:
        """Generate system prompt for LangMem agent with user context"""
        current_datetime = datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")
        chat_type = user_metadata.get('chat_type', 'unknown')
        chat_title = user_metadata.get('chat_title', 'a chat')
        chat_id = user_metadata.get('chat_id')
        user_id = user_metadata.get('user_id')
        username = user_metadata.get('username', 'N/A')
        full_name = user_metadata.get('full_name', 'N/A')
        
        is_group_chat = chat_type in ['group', 'supergroup']
        
        return f"""You are a helpful AI assistant powered by OpenAI GPT-4o Mini with long-term memory capabilities.

Current Context:
- Time: {current_datetime}
- User: {full_name} (@{username}, ID: {user_id})
- Chat: {chat_title} (ID: {chat_id}, Type: {chat_type})

Memory Tools:
You have access to 'manage_memory' and 'search_memory' tools. Use them to:
- Store important user preferences, facts, and information
- Retrieve relevant past conversations and context
- Remember group discussions and decisions

When to Store Memories:
- User preferences ("I like...", "I prefer...", "My favorite is...")
- Important facts about users or topics
- Group decisions or plans (in group chats)
- User roles or responsibilities

Memory Format:
- For group chats: "In {chat_title} (Chat ID: {chat_id}), @{username} ({full_name}, ID: {user_id}) [information]"
- For private chats: "@{username} ({full_name}, ID: {user_id}) [information]"

Response Guidelines:
1. Be natural and conversational
2. Don't announce when you store or retrieve memories - just use them naturally
3. If a question is unclear, ask for clarification
4. Personalize responses based on stored memories
5. {"In group chats, track who said what and remember group-level context" if is_group_chat else "Focus on building a personal relationship"}

Example Good Responses:
- User: "I love pizza"
  Response: "Pizza is great! What's your favorite topping?" (while silently storing the preference)
  
- User: "What do I like?"
  Response: "Based on our conversations, you love pizza and prefer morning meetings." (using retrieved memories)"""
    
    @staticmethod
    def get_prompt_with_memories(base_prompt: str, memory_context: str) -> str:
        """Return base prompt without appending memory context"""
        return base_prompt
    
    @staticmethod
    def format_user_message(user_input: str, user_metadata: Dict[str, Any]) -> str:
        """Format user message based on chat type"""
        chat_type = user_metadata.get('chat_type', 'private')
        username = user_metadata.get('username', 'User')
        full_name = user_metadata.get('full_name', 'User')
        
        if chat_type in ['group', 'supergroup']:
            return f"@{username} ({full_name}): {user_input}"
        return user_input