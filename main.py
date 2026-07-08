import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv

# Import existing files from parent directory/local path
from rag_retriever import retrieve_context
from generate_answer import generate_answer

load_dotenv()

# Initialize Gemini API client (used as Secondary LLM)
client = None
try:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("DeepSeek_Api_KEY")
    if api_key:
        client = genai.Client(api_key=api_key)
        print("Gemini Client successfully initialized.")
    else:
        print("Warning: Neither GEMINI_API_KEY nor DeepSeek_Api_KEY was found in environment.")
except Exception as e:
    print(f"Failed to initialize Gemini Client: {e}")

app = FastAPI(title="Library Academic Chatbot Backend")

# CORS settings to allow communication with the React frontend / Node backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


def is_bengali(text: str) -> bool:
    bengali_chars = any(u"\u0980" <= char <= u"\u09ff" for char in text)
    common_banglish = any(
        word in text.lower()
        for word in ["boi", "ache", "pabo", "fine", "rule", "kobe", "koto", "ki", "taka"]
    )
    return bengali_chars or common_banglish


def is_small_talk(text: str) -> bool:
    small_talk = {
        "hi", "hello", "hey", "hola",
        "thanks", "thank you",
        "good morning", "good evening", "good afternoon",
        "হাই", "হ্যালো", "কেমন আছো", "ধন্যবাদ", "kemon acho"
    }
    return text.lower().strip().replace("?", "").replace(".", "") in small_talk


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Academic Library Chatbot API",
        "ollama_enabled": os.getenv("USE_OLLAMA", "true").lower() == "true"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)