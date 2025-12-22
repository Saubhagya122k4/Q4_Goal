from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from memory import get_chat_history

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.7
)


async def get_response(user_id: str, user_input: str, user_metadata: dict) -> str:
    """
    Get AI response with chat history context and user metadata
    """
    # Get chat history for this user
    chat_history = get_chat_history(user_id)
    
    # Get previous messages
    previous_messages = chat_history.messages
    
    # Create message list with history
    messages = previous_messages + [HumanMessage(content=user_input)]
    
    # Get AI response
    response = await llm.ainvoke(messages)
    
    # Save both user message and AI response to history with metadata
    chat_history.add_message(
        HumanMessage(
            content=user_input,
            additional_kwargs={"metadata": user_metadata}
        )
    )
    chat_history.add_message(
        AIMessage(
            content=response.content,
            additional_kwargs={"metadata": {"response_to": user_id}}
        )
    )
    
    return response.content