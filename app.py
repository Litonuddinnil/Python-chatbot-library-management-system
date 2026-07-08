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

# Define a function to process chat messages specifically for Gradio
def gradio_chat_respond(message, history):
    """
    Core response generation logic matching main.py but adapted for Gradio.
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
                local_answer = "দুঃখিত, এই বিষয়টি নিয়ে এই মুহূর্তে কোনো তথ্য পাওয়া যায়নি। অনুগ্রহ করে অন্যভাবে চেষ্টা করুন।"
            else:
                local_answer = "I apologize, but I could not find specific information for your query. Please let me know how else I can assist."
        return local_answer, context, "Local LLM / Ollama"
    except Exception as e:
        print(f"[Gradio] Local answer generation failed: {e}")
        fallback_msg = (
            "দুঃখিত, এই মুহূর্তে নেটওয়ার্ক সমস্যার কারণে সাহায্য করতে পারছি না। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।"
            if is_bengali(user_msg) else
            "I apologize, but I am currently having trouble retrieving that information. Please try asking again in a moment."
        )
        return fallback_msg, context, "Error Recovery Fallback"

# Build the Gradio interface
with gr.Blocks(title="Academic Library Assistant", theme=gr.themes.Soft(primary_hue="blue", secondary_hue="slate")) as demo:
    gr.HTML(
        """
        <div style="text-align: center; margin-bottom: 20px; padding: 20px; background-color: #f0f7ff; border-radius: 12px; border: 1px solid #d0e3ff;">
            <h1 style="color: #1e3a8a; margin: 0; font-size: 2.2rem; font-weight: 700;">📚 Academic Library Assistant</h1>
            <p style="color: #4b5563; font-size: 1.1rem; margin-top: 8px;">
                Ask questions about catalog search, library policies, textbooks, late fees, or study room bookings.
            </p>
            <div style="display: flex; justify-content: center; gap: 15px; margin-top: 10px; font-size: 0.9rem; color: #1e40af;">
                <span>⚡ Supports <b>DeepSeek API</b></span> | 
                <span>✨ <b>Gemini API</b></span> | 
                <span>🐳 <b>Local LLM / Ollama Fallback</b></span>
            </div>
        </div>
        """
    )
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(label="Library Chat History", height=500, show_copy_button=True)
            msg_input = gr.Textbox(
                label="Type your message here...",
                placeholder="e.g., What are the library opening hours? / বই ধার নেওয়ার নিয়ম কি?",
                lines=2,
                max_lines=4
            )
            with gr.Row():
                submit_btn = gr.Button("Send Message 🚀", variant="primary")
                clear_btn = gr.ClearButton([chatbot, msg_input], value="Clear Chat 🗑️")
            
            # Example Prompts
            gr.Examples(
                examples=[
                    "What are the library hours during exams?",
                    "বই রিইস্যু করার নিয়ম কি?",
                    "How much is the late fine for overdue books?",
                    "How can I book a group study room?",
                ],
                inputs=msg_input,
                label="Common Student Questions"
            )
            
        with gr.Column(scale=2):
            gr.Markdown("### 🔍 Intelligent RAG Assistant Details")
            engine_box = gr.Textbox(
                label="Active Model / Generation Engine",
                interactive=False,
                value="Waiting for your message..."
            )
            context_box = gr.Markdown(
                label="Retrieved Knowledge Base Context",
                value="*Knowledge retrieved from MongoDB vector store will appear here when you send a message.*"
            )

    # Chat submission handler
    def handle_submit(message, chat_history):
        if not message.strip():
            return "", chat_history, "Waiting...", "Please enter a message."
        
        # Add user message to history
        chat_history = chat_history + [[message, None]]
        yield "", chat_history, "Generating response...", "*Fetching database context...*"
        
        # Get AI response
        reply, context, source = gradio_chat_respond(message, chat_history)
        
        # Update chatbot response in history
        chat_history[-1][1] = reply
        
        # Format the retrieved context nicely for the sidebar
        formatted_context = f"**Source Context Used:**\n\n"
        if context and context != "N/A (Small Talk)" and context != "Failed to fetch context.":
            formatted_context += f"```text\n{context}\n```"
        else:
            formatted_context += f"*{context}*"
            
        yield "", chat_history, source, formatted_context

    # Register actions
    submit_btn.click(
        handle_submit, 
        inputs=[msg_input, chatbot], 
        outputs=[msg_input, chatbot, engine_box, context_box]
    )
    msg_input.submit(
        handle_submit, 
        inputs=[msg_input, chatbot], 
        outputs=[msg_input, chatbot, engine_box, context_box]
    )

# Mount Gradio app into FastAPI
# This allows the React Frontend to hit /api/chat or /chat, 
# while Hugging Face and manual users get the beautiful Gradio Web UI at "/"!
fastapi_app = gr.mount_gradio_app(fastapi_app, demo, path="/")

if __name__ == "__main__":
    # Standard HF Spaces port is 7860
    port = int(os.getenv("PORT", 7860))
    print(f"Starting server on port {port}...")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=port)
