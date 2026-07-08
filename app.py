import spaces  # MUST be the very first import (before torch/sentence_transformers get loaded indirectly)

import os
import gradio as gr
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import requests as req_lib

# Import existing application logic from main.py and other files
from main import app as fastapi_app, is_bengali, is_small_talk, client, ChatRequest
from rag_retriever import retrieve_context
from generate_answer import generate_answer


@spaces.GPU(duration=1)
def _warmup_gpu():
    """
    Dummy function required by Hugging Face ZeroGPU startup check.
    This app doesn't actually need GPU compute (uses external APIs +
    lightweight CPU sentence-transformers), but ZeroGPU hardware requires
    at least one @spaces.GPU-decorated function to be detected at startup.
    """
    return True


def gradio_chat_respond(message, history):
    """
    Core response generation logic.
    Returns:
        reply (str): The chatbot response.
        context (str): The retrieved database context.
        source (str): The LLM engine source.
    """
    user_msg = message.strip()
    if not user_msg:
        return "Please ask a question.", "", "empty"

    # 1. Handle small talk directly
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
        return reply, "N/A (Small Talk)", "Small Talk Handler"

    # 2. Retrieve RAG Context
    context = ""
    try:
        context = retrieve_context(user_msg, top_k=4)
    except Exception as e:
        print(f"RAG Retrieval failed: {e}")
        context = "Failed to fetch context."

    # Build prompts
    system_prompt = (
        "You are a hybrid AI assistant built for an Academic Library.\n"
        "Provide accurate, concise, student-friendly answers.\n"
        "Style: Professional, clear, step-by-step for technical explanations, suitable for student-level understanding.\n"
        "ABSOLUTE RULES:\n"
        "- Responses must be JSX-safe plain text. No HTML, no raw CSS, no style tags.\n"
        "- Plain text only, line breaks are allowed, absolutely NO emojis.\n"
        "- Language: Bangla/Banglish input -> Bangla/Banglish output. English input -> English output.\n"
        "- Prefer using MongoDB learned data/retrieved context when available.\n"
        "- If no context exists, respond using general intelligence to help the student.\n"
        "- Never mention API limits, quota, fallback, or internal errors.\n"
        "- Never return empty, null, or error-like responses."
    )
    user_prompt = f"Retrieved Context:\n{context}\n\nQuestion: {user_msg}"

    # 3. Try DeepSeek API as Primary
    deepseek_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("DeepSeek_Api_KEY")
    if deepseek_key:
        try:
            print("[Gradio] Trying DeepSeek API as Primary LLM...")
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
            resp = req_lib.post("https://api.deepseek.com/chat/completions", json=payload, headers=headers, timeout=6)
            if resp.status_code == 200:
                result_json = resp.json()
                reply = result_json["choices"][0]["message"]["content"].strip()
                if reply:
                    return reply, context, "DeepSeek API"
            print(f"[Gradio] DeepSeek returned status {resp.status_code}. Automatically falling back...")
        except Exception as e:
            print(f"[Gradio] DeepSeek call failed: {e}. Automatically falling back...")

    # 4. Try Gemini API as Secondary
    if client:
        try:
            print("[Gradio] Trying Gemini API as Secondary LLM...")
            prompt = f"{system_prompt}\n\n{user_prompt}\n\nAnswer:"
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            reply = response.text.strip()
            if reply:
                return reply, context, "Gemini API"
        except Exception as e:
            print(f"[Gradio] Gemini API generation failed: {e}. Automatically falling back to local...")

    # 5. Try Ollama/Local LLM as Tertiary
    try:
        print("[Gradio] Trying Local LLM / Ollama...")
        local_answer = generate_answer(user_msg, context)
        if not local_answer or "error" in local_answer.lower():
            if is_bengali(user_msg):
                local_answer = "দুঃখিত, এই বিষয়টি নিয়ে এই মুহূর্তে কোনো তথ্য পাওয়া যায়নি। অনুগ্রহ করে অন্যভাবে চেষ্টা করুন।"
            else:
                local_answer = "I apologize, but I could not find specific information for your query. Please let me know how else I can assist."
        return local_answer, context, "Local LLM / Ollama"
    except Exception as e:
        print(f"[Gradio] Local answer generation failed: {e}")
        fallback_msg = (
            "দুঃখিত, এই মুহূর্তে নেটওয়ার্ক সমস্যার কারণে সাহায্য করতে পারছি না। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
            if is_bengali(user_msg) else
            "I apologize, but I am currently having trouble retrieving that information. Please try asking again in a moment."
        )
        return fallback_msg, context, "Error Recovery Fallback"


def simple_chat(message):
    reply, context, source = gradio_chat_respond(message, [])
    return reply


# Minimal Gradio interface: just an input box and an output box
demo = gr.Interface(
    fn=simple_chat,
    inputs=gr.Textbox(label="Question"),
    outputs=gr.Textbox(label="Answer"),
    title="Academic Library Assistant",
)

# Trigger GPU function detection at startup (required for ZeroGPU Spaces)
_warmup_gpu()

 
@fastapi_app.post("/api/chat")
def api(data: ChatRequest):
    print("Received:", data.message)

    reply, context, source = gradio_chat_respond(data.message, [])

    print("Reply:", repr(reply))
    print("Context:", repr(context))
    print("Source:", repr(source))

    return {
        "reply": reply,
        "context": context,
        "engine": source
    }


 
demo.queue()
fastapi_app = gr.mount_gradio_app(fastapi_app, demo, path="/", ssr_mode=False)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 7860))
    print(f"Starting server on port {port}...") 
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)