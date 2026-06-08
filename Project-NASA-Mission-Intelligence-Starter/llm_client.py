from typing import Dict, List
from openai import OpenAI
import tiktoken

def generate_response(openai_key: str, user_message: str, context: str, 
                     conversation_history: List[Dict], model: str = "gpt-3.5-turbo") -> str:
    """Generate response using OpenAI with context"""

    messages = []
    # TODO: Define system prompt
    system_prompt = """
You are a NASA mission expert. Your task is to answer questions about NASA missions using the information provided in the context. If the
context does not contain an answer to the user's question, let the user know that you don't have enough information to answer the question.
Answer the question as accurately to the source information as possible and only provide information relevant to the question."""
    messages.append({"role": "system", "content": system_prompt})
    # TODO: Set context in messages
    if context:
        messages.append({"role": "system", "content": f"Here is some relevant information that may help you answer the user's question:\n\n{context}"})
    # TODO: Add chat history
    reduced_history = reduce_history(conversation_history, model)
    messages.extend(reduced_history)
    # TODO: Creaet OpenAI Client
    openai_client = OpenAI(
        base_url="https://openai.vocareum.com/v1",
        api_key=openai_key
    )
    # TODO: Send request to OpenAI
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages + [{"role": "user", "content": user_message}],
        max_tokens=500,
        temperature=0.7
    )
    # TODO: Return response
    return response.choices[0].message.content

def reduce_history(conversation_history: List[Dict], model: str, max_tokens: int = 1500) -> List[Dict]:
    encoding = tiktoken.encoding_for_model(model)
    total_tokens = 0
    reduced_history = []

    for message in reversed(conversation_history):
        message_tokens = len(encoding.encode(message["content"]))
        if total_tokens + message_tokens <= max_tokens:
            reduced_history.append(message)
            total_tokens += message_tokens
        else:
            break
    
    return list(reversed(reduced_history))
