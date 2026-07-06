import os
import requests
import json

# =========================================================
# CONFIG FOR BOTH TRANSFOMERS & OLLAMA MODES
# =========================================================
from dotenv import load_dotenv
load_dotenv()

USE_OLLAMA = os.getenv("USE_OLLAMA", "true").lower() == "true"
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")  # or llama3, mistral, etc.

# Dynamically set BASE_MODEL_ID based on whether HF_TOKEN exists, to match train_llm.py behavior
hf_token = os.getenv("HF_TOKEN")
default_base = "meta-llama/Llama-3.2-3B-Instruct" if hf_token else "Qwen/Qwen2.5-3B-Instruct"
BASE_MODEL_ID = os.getenv("BASE_MODEL_ID", default_base)
LORA_PATH = "./my-library-llm"

# Lazy loaded transformers variables
_tokenizer = None
_model = None

def load_transformers_model():
    global _tokenizer, _model, BASE_MODEL_ID
    if _model is not None:
        return _tokenizer, _model

    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    import torch

    print(f"Loading local base model: {BASE_MODEL_ID}...")
    try:
        _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True, token=hf_token)
        base = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_ID,
            device_map="auto",
            torch_dtype=torch.float16,
            token=hf_token
        )
    except Exception as e:
        err_msg = str(e).lower()
        is_gated_error = any(kw in err_msg for kw in ["gated", "401", "403", "unauthorized", "review", "forbidden"])
        default_model = "Qwen/Qwen2.5-3B-Instruct"
        
        if is_gated_error and BASE_MODEL_ID != default_model:
            print(f"\n⚠️ Access denied/gated error for {BASE_MODEL_ID}: {e}")
            print(f"🔄 Automatically falling back to completely UNGATED SOTA model: '{default_model}'...")
            BASE_MODEL_ID = default_model
            _tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL_ID, use_fast=True)
            base = AutoModelForCausalLM.from_pretrained(
                BASE_MODEL_ID,
                device_map="auto",
                torch_dtype=torch.float16
            )
        else:
            raise e
    
    print(f"Loading LoRA adapter from {LORA_PATH}...")
    _model = PeftModel.from_pretrained(base, LORA_PATH)
    _model.eval()
    return _tokenizer, _model

# =========================================================
# ANSWER GENERATION (DUAL SUPPORT: OLLAMA & PEFT)
# =========================================================
def generate_answer(question: str, context: str) -> str:
    """
    Generates a safe academic answer using RAG context only.
    Supports local Ollama backend or PyTorch PEFT/Transformers.
    """
    if not context or not context.strip():
        return "Sorry, ei bishoye amar kache tottho nai."

    prompt = f"""
You are an academic library assistant.

STRICT RULES:
- Answer ONLY from the given context.
- Do NOT guess or add extra information.
- If the answer is not found in the context, say:
  "Sorry, ei bishoye amar kache tottho nai."
- Never show emails, links, IDs, or system metadata.
- Keep the answer short and clear.

Context:
{context}

Question:
{question}

Answer:
""".strip()

    # --- Mode 1: Ollama Mode (Recommended for lightweight local setup) ---
    if USE_OLLAMA:
        try:
            url = f"{OLLAMA_HOST}/api/generate"
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 150
                }
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "").strip()
                if answer:
                    return answer
            print("Ollama call failed or returned empty. Falling back...")
        except Exception as e:
            print(f"Ollama connection error: {e}. Ensure Ollama is running at {OLLAMA_HOST}")

    # --- Mode 2: PEFT Local Transformers Mode ---
    try:
        tok, md = load_transformers_model()
        import torch
        
        inputs = tok(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048
        ).to(md.device)

        with torch.no_grad():
            outputs = md.generate(
                **inputs,
                max_new_tokens=120,
                temperature=0.3,
                top_p=0.9,
                repetition_penalty=1.1,
                do_sample=True
            )

        decoded = tok.decode(outputs[0], skip_special_tokens=True)

        if "Answer:" in decoded:
            answer = decoded.split("Answer:")[-1].strip()
        else:
            answer = decoded.strip()

        if not answer:
            return "Sorry, ei bishoye amar kache tottho nai."

        return answer

    except Exception as e:
        print(f"Transformers PEFT generation failed: {e}")
        # Universal fallback to make sure app never crashes
        return "Sorry, connection error ba models load korte parini."
