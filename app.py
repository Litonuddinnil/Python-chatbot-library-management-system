import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai   
from dotenv import load_dotenv

#  import existing file 
from rag_retriever import retrieve_context
from generate_answer import generate_answer

load_dotenv()

# initial gemini api_key 
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

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
        "good morning", "good evening",
        "হাই", "হ্যালো", "কেমন আছো"
    }
    return text.lower().strip() in small_talk

@app.post("/chat")
async def chat(req: ChatRequest):
    user_msg = req.message.strip()

    if not user_msg:
        return {"reply": "Please ask a question."}

    #  sort gettings chat 
    if is_small_talk(user_msg):
        return {
            "reply": (
                "Hello! I am an academic library assistant. "
                "You can ask me about books, subjects, or lecture notes."
            )
        }

    # MongoDB  to learn model 
    context = retrieve_context(user_msg)

    if not context:
        return {
            "reply": "Sorry, ei bishoye amar kache relevant tottho nai."
        }

    #  Gemini (Primary) + Local Model (Fallback) jora lagaisi
    try:
        print("⚡ Trying Gemini API (New google-genai SDK)...")
        
        prompt = (
            f"You are an expert library academic assistant. Use the following database context "
            f"to answer the student's question accurately. If the context is not enough, use your general knowledge.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {user_msg}\n\n"
            f"Answer:"
        )
        
        #  new SDk method apply
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return {"reply": response.text}

    except Exception as e:
        
        # custom local backup 
        local_answer = generate_answer(user_msg, context)
        return {"reply": local_answer}