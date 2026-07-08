import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai   
from dotenv import load_dotenv

# Import existing files from parent directory/local path
from rag_retriever import retrieve_context
from generate_answer import generate_answer

load_dotenv()

# Initialize Gemini API client (used as Primary, or can be toggled)
# Note: google-genai is used here
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

# CORS settings to allow communication with the React frontend
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
    # Check for Bengali characters or common banglish vocabulary
    bengali_chars = any(u"\u0980" <= char <= u"\u09ff" for char in text)
    common_banglish = any(word in text.lower() for word in ["boi", "ache", "pabo", "fine", "rule", "kobe", "koto", "ki", "taka"])
    return bengali_chars or common_banglish

def is_small_talk(text: str) -> bool:
    small_talk = {
        "hi", "hello", "hey", "hola",
        "thanks", "thank you",
        "good morning", "good evening", "good afternoon",
        "হাই", "হ্যালো", "কেমন আছো", "ধন্যবাদ", "kemon acho"
    }
    return text.lower().strip().replace("?", "").replace(".", "") in small_talk

@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Academic Library Chatbot API",
        "ollama_enabled": os.getenv("USE_OLLAMA", "true").lower() == "true"
    }

@app.post("/chat")
@app.post("/api/chat")
async def chat(req: ChatRequest):
    user_msg = req.message.strip()

    if not user_msg:
        return {"reply": "Please ask a question."}

    # Handle greetings / small talk directly
    if is_small_talk(user_msg):
        if is_bengali(user_msg):
            reply = (
                "হ্যালো! আমি আপনার একাডেমিক লাইব্রেরি অ্যাসিস্ট্যান্ট। "
                "আমি আপনাকে কীভাবে সাহায্য করতে পারি? আপনি আমাকে লাইব্রেরির সময়সূচী, বই ধার নেওয়ার নিয়মাবলী, জরিমানা বা নির্দিষ্ট কোনো বই বা লেকচার নোট সম্পর্কে জিজ্ঞাসা করতে পারেন।"
            )
        else:
            reply = (
                "Hello! I am your Academic Library Assistant. "
                "How can I help you today? You can ask me about library hours, borrowing policies, late fines, "
                "or search for specific textbooks and course lecture notes."
            )
        return {
            "reply": reply,
            "source": "small_talk"
        }

    # Retrieve context from MongoDB using BM25 and Vector Search (FAISS)
    context = ""
    try:
        context = retrieve_context(user_msg, top_k=4)
    except Exception as e:
        print(f"RAG Retrieval failed: {e}")

    # Build system prompt containing strict hybrid AI instructions
    system_prompt = (
        "You are a hybrid AI assistant built for an Academic Library. "
        "Provide accurate, concise, student-friendly answers. "
        "Style: Professional, clear, step-by-step for technical explanations, suitable for student-level understanding. "
        "ABSOLUTE RULES:\n"
        "- Responses must be JSX-safe plain text. No HTML (unless explicitly requested), no raw CSS, no style tags.\n"
        "- Plain text only, line breaks are allowed, absolutely NO emojis.\n"
        "- Language: Bangla/Banglish input -> Bangla/Banglish output. English input -> English output.\n"
        "- Prefer using MongoDB learned data/retrieved context when available.\n"
        "- If no context exists, respond using general intelligence to help the student.\n"
        "- Never mention API limits, quota, fallback, or internal errors.\n"
        "- Never return empty, null, or error-like responses."
    )

    user_prompt = f"Retrieved Context:\n{context}\n\nQuestion: {user_msg}"

    # Try Primary Flow: DeepSeek API
    deepseek_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DeepSeek_Api_KEY")
    if deepseek_key:
        try:
            print("Trying DeepSeek API as Primary LLM...")
            import requests as req_lib
            headers = {
                "Authorization": f"Bearer {deepseek_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3
            }
            # Timeout set to 6 seconds to ensure swift response
            resp = req_lib.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=6)
            if resp.status_code == 200:
                result_json = resp.json()
                reply = result_json["choices"][0]["message"]["content"].strip()
                if reply:
                    return {
                        "reply": reply,
                        "context": context,
                        "source": "deepseek"
                    }
            print(f"DeepSeek returned status {resp.status_code}. Automatically falling back...")
        except Exception as e:
            print(f"DeepSeek call failed: {e}. Automatically falling back...")

    # Secondary API Flow: Gemini API (google-genai SDK)
    if client:
        try:
            print("Trying Gemini API as secondary LLM flow...")
            prompt = f"{system_prompt}\n\n{user_prompt}\n\nAnswer:"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            reply = response.text.strip()
            if reply:
                return {
                    "reply": reply,
                    "context": context,
                    "source": "gemini"
                }
        except Exception as e:
            print(f"Gemini API generation failed: {e}. Automatically falling back to Local/Ollama...")

    # Tertiary Fallback Flow: Ollama Local LLM / PEFT Response Generation
    try:
        print("Using Fallback Flow: Ollama Local LLM...")
        local_answer = generate_answer(user_msg, context)
        # Apply strict rules on local_answer if needed, ensuring no error or empty response
        if not local_answer or "error" in local_answer.lower():
            if is_bengali(user_msg):
                local_answer = "দুঃখিত, এই বিষয়টি নিয়ে এই মুহূর্তে কোনো তথ্য পাওয়া যায়নি। অনুগ্রহ করে অন্যভাবে চেষ্টা করুন।"
            else:
                local_answer = "I apologize, but I could not find specific information for your query. Please let me know how else I can assist."
        
        return {
            "reply": local_answer,
            "context": context,
            "source": "local_llm"
        }
    except Exception as e:
        print(f"Local answer generation failed: {e}")
        # Always return a beautiful, non-error message using general intelligence style
        fallback_msg = (
            "দুঃখিত, এই মুহূর্তে নেটওয়ার্ক সমস্যার কারণে সাহায্য করতে পারছি না। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
            if is_bengali(user_msg) else
            "I apologize, but I am currently having trouble retrieving that information. Please try asking again in a moment."
        )
        return {
            "reply": fallback_msg,
            "context": context,
            "source": "fallback_error_recovery"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
