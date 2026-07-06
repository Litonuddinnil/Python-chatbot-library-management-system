from chatbot.retriever import retrieve_context
from chatbot.gemini import ask_gemini

def chat_engine(user_message: str) -> str:
    # Query database search algorithm
    context = retrieve_context(user_message)

    if context:
        # Configure data boundaries if records are successfully found in MongoDB
        system_instruction = (
            "You are an expert Library Management System Assistant. Answer the question strictly "
            "using the verified catalog data records provided. If parameters look missing, state you cannot find them locally."
        )
        prompt = f"""
Strict Instruction: Use the following local database context records to fulfill the request.

Local Catalog Context:
{context}

User Input:
{user_message}
"""
    else:
        # Switch behavior dynamically if no local records pass structural verification thresholds
        system_instruction = (
            "You are a helpful general-purpose Library AI helper. Since this item is missing "
            "from the local collection database, leverage your complete knowledge memory base to provide informative advice."
        )
        prompt = f"User Request: {user_message}"

    return ask_gemini(prompt, system_instruction=system_instruction)