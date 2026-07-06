import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

try:
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import LoraConfig
    from trl import SFTTrainer, SFTConfig
except ImportError:
    print("Please make sure all dependencies in requirements.txt are installed: pip install -r requirements.txt")
    exit(1)

if not os.path.exists("qa_dataset.jsonl"):
    print("qa_dataset.jsonl not found! Please run build_qa_dataset.py first.")
    exit(1)

# Allow customizing base model from environment variable, default to Qwen if no token, or Llama if token is present
default_model = "Qwen/Qwen2.5-3B-Instruct"  # High quality, completely UNGATED, perfect fallback

hf_token = os.getenv("HF_TOKEN")
if hf_token:
    print("Found HF_TOKEN in environment variables. Defaulting to Meta Llama-3.2.")
    base_model_id = os.getenv("BASE_MODEL_ID", "meta-llama/Llama-3.2-3B-Instruct")
else:
    print("\n⚠️ NOTE: No HF_TOKEN detected in your .env file.")
    print("meta-llama/Llama-3.2-3B-Instruct is a gated repository on Hugging Face.")
    print("To use Llama 3.2, you must:")
    print("1. Create an account on https://huggingface.co")
    print("2. Request access at https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct")
    print("3. Generate a read token at https://huggingface.co/settings/tokens")
    print("4. Add 'HF_TOKEN=your_token_here' to your .env file\n")
    print(f"🔄 Falling back to completely UNGATED state-of-the-art model: '{default_model}' (No login required!)")
    base_model_id = os.getenv("BASE_MODEL_ID", default_model)

print(f"\nLoading base model and tokenizer for {base_model_id}...")
try:
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(base_model_id, device_map="auto", token=hf_token)
except Exception as e:
    err_msg = str(e).lower()
    is_gated_error = any(kw in err_msg for kw in ["gated", "401", "403", "unauthorized", "review", "forbidden"])
    
    if is_gated_error and base_model_id != default_model:
        print(f"\n⚠️ Access denied/gated error for {base_model_id}: {e}")
        print(f"🔄 Automatically falling back to completely UNGATED SOTA model: '{default_model}'...")
        base_model_id = default_model
        try:
            tokenizer = AutoTokenizer.from_pretrained(base_model_id)
            model = AutoModelForCausalLM.from_pretrained(base_model_id, device_map="auto")
        except Exception as fallback_err:
            print(f"\n❌ Error loading fallback model {base_model_id}: {fallback_err}")
            exit(1)
    else:
        print(f"\n❌ Error loading model {base_model_id}: {e}")
        exit(1)

dataset = load_dataset("json", data_files="qa_dataset.jsonl", split="train")

lora_config = LoraConfig(
    r=16, 
    lora_alpha=32, 
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    task_type="CAUSAL_LM",
)

def format_example(ex):
    return {"text": f"{ex['prompt']} {ex['response']}"}

dataset = dataset.map(format_example)

sft_config = SFTConfig(
    output_dir="./my-library-llm",
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=8,
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy="epoch",
)

print("Initializing SFTTrainer and beginning LoRA adapter fine-tuning...")
trainer = SFTTrainer(
    model=model,
    args=sft_config,
    train_dataset=dataset,
    peft_config=lora_config,
    dataset_text_field="text",
)

trainer.train()
trainer.save_model("./my-library-llm")
tokenizer.save_pretrained("./my-library-llm")
print("Successfully fine-tuned and saved LoRA adapter model to ./my-library-llm")
