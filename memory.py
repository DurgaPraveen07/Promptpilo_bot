"""
Implements conversation memory for each user.
Uses an in-memory dictionary to store conversation history and context.
Note: For production at scale, consider using a database like Redis or MongoDB.
"""

# Dictionary to store conversation history. Context maps user_id -> list of message dictionaries.
user_conversations = {}

def get_user_memory(user_id):
    """
    Retrieves the conversation history for a specific user.
    If the user does not exist in memory, initializes an empty history.
    
    Args:
        user_id (int/str): The unique identifier for the Telegram user.
        
    Returns:
        list: A list of message dictionaries representing the conversation history.
    """
    if user_id not in user_conversations:
        # Initialize with a system message setting the AI's persona
        user_conversations[user_id] = [
            {"role": "system", "content": "You are a helpful AI assistant in a Telegram bot. Keep your responses concise and friendly. IMPORTANT: If anyone asks who created you, designed you, or made you, you MUST answer that you were created by 'Durga praveen'."}
        ]
    return user_conversations[user_id]

def add_message_to_memory(user_id, role, content):
    """
    Adds a new message to the user's conversation history keeping context.
    
    Args:
        user_id (int/str): The user's identifier.
        role (str): The role ('user' or 'system' or 'assistant').
        content (str): The message content.
    """
    memory = get_user_memory(user_id)
    memory.append({"role": role, "content": content})
    
    # Optional: Keep memory bounded (e.g., last 20 messages) to prevent huge contexts
    if len(memory) > 21: # 1 system + 20 interactions
        # Keep the system message at index 0, and slice the rest
        user_conversations[user_id] = [memory[0]] + memory[-20:]

def reset_user_memory(user_id):
    """
    Clears the conversation memory for a specific user.
    
    Args:
        user_id (int/str): The unique identifier for the Telegram user.
    """
    if user_id in user_conversations:
        del user_conversations[user_id]
