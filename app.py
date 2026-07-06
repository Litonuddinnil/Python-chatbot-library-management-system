from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_retriever import retrieve_context
from generate_answer import generate_answer

app = FastAPI(title="Library Academic Chatbot")

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

def is_small_talk(text: str) -> bool:
    small_talk = {
        "hi", "hello", "hey",
        "thanks", "thank you",
        "good morning", "good evening"
    }
    return text.lower().strip() in small_talk

@app.post("/chat")
async def chat(req: ChatRequest):
    user_msg = req.message.strip()

    if not user_msg:
        return {"reply": "Please ask a question."}

    if is_small_talk(user_msg):
        return {
            "reply": (
                "Hello! I am an academic library assistant. "
                "You can ask me about books, subjects, or lecture notes."
            )
        }

    # Retrieve context from MongoDB
    context = retrieve_context(user_msg)

    if not context:
        return {
            "reply": "Sorry, ei bishoye amar kache relevant tottho nai."
        }

    # Generate reply
    answer = generate_answer(user_msg, context)
    return {"reply": answer}