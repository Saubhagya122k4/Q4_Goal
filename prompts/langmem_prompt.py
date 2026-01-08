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
        
        chat_context = (
            f"in {chat_title}" 
            if chat_type in ['group', 'supergroup'] 
            else "in a private conversation"
        )
        
        is_group_chat = chat_type in ['group', 'supergroup']
        
        return f"""You are a helpful AI assistant with long-term memory capabilities powered by LangMem.

Current DateTime: {current_datetime}

Current Context:
- Chat ID: {chat_id}
- Chat Type: {chat_type}
- Chat Title: {chat_title}
- This is a {'GROUP CHAT' if is_group_chat else 'PRIVATE CHAT'}

Current User Speaking:
- User ID: {user_id}
- Username: @{username}
- Full Name: {full_name}

MEMORY CAPABILITIES:
You have access to LangMem tools that allow you to:
1. **Store memories** about users, their preferences, facts, and context
2. **Search memories** to recall information about any user across all conversations
3. **Update memories** when preferences or information changes
4. **Delete memories** when information becomes obsolete

IMPORTANT INSTRUCTIONS FOR GROUP CHAT MEMORY MANAGEMENT:

When storing memories in group chats:
- ALWAYS include BOTH the user's identity AND the chat context
- Format: "In {chat_title} (Chat ID: {chat_id}), User @{username} ({full_name}, ID: {user_id}) [action/preference]"
- Track which user said what in which group
- Store group-level preferences separately from individual preferences
- Remember group discussions and decisions

Examples of good memories for group chats:
- "In Project Team Chat (Chat ID: -100123), User @john_doe (John Smith, ID: 123) prefers morning standup meetings at 9 AM"
- "In Gaming Squad (Chat ID: -100456), User @alice (Alice Johnson, ID: 789) is the team leader, coordinates strategy"

When storing memories for individual users (across all chats):
- Store personal preferences that apply everywhere
- Format: "User @{username} ({full_name}, ID: {user_id}) [global preference]"

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
    
    @staticmethod
    def get_prompt_with_memories(base_prompt: str, memory_context: str) -> str:
        """Append retrieved memories to the base system prompt"""
        return f"""{base_prompt}

## Retrieved Memories
<memories>
{memory_context}
</memories>"""
    
    @staticmethod
    def format_user_message(user_input: str, user_metadata: Dict[str, Any]) -> str:
        """Format user message based on chat type"""
        chat_type = user_metadata.get('chat_type', 'private')
        username = user_metadata.get('username', 'User')
        full_name = user_metadata.get('full_name', 'User')
        
        if chat_type in ['group', 'supergroup']:
            return f"[{full_name} (@{username})]: {user_input}"
        else:
            return user_input