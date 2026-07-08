# train_embeddings.py
import json
import os

try:
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader
except ImportError:
    print("Dependencies missing! Run: pip install sentence-transformers torch")
    exit(1)

if not os.path.exists("train_pairs.jsonl"):
    print("train_pairs.jsonl not found! Please run generate_query_pairs.py first.")
    exit(1)

print("Loading query pairs for training...")
pairs = []
with open("train_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            pairs.append(json.loads(line))

train_examples = [InputExample(texts=[p["query"], p["passage"]]) for p in pairs]

print("Initializing sentence transformer model 'all-MiniLM-L6-v2'...")
model = SentenceTransformer("all-MiniLM-L6-v2")  # start from the pretrained base
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

print("Beginning embedding fine-tuning (10 epochs)...")
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=10,
    warmup_steps=int(0.1 * len(train_dataloader)),
    output_path="./my-library-embedding-model",
    show_progress_bar=True,
)
print("Saved fine-tuned embedding model to ./my-library-embedding-model")
