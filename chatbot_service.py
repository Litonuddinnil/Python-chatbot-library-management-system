from rag_retriever import retrieve_context
from generate_answer import generate_answer

def handle_user_message(question: str) -> str:
    context = retrieve_context(question, top_k=4)
    return generate_answer(question, context)
