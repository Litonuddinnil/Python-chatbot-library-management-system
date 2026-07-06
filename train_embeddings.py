# train_embeddings.py
import json
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

pairs = [json.loads(l) for l in open("train_pairs.jsonl", encoding="utf-8")]
train_examples = [InputExample(texts=[p["query"], p["passage"]]) for p in pairs]

model = SentenceTransformer("all-MiniLM-L6-v2")  # start from the pretrained base
train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=5,
    warmup_steps=int(0.1 * len(train_dataloader)),
    output_path="./my-library-embedding-model",
    show_progress_bar=True,
)
print("Saved fine-tuned embedding model to ./my-library-embedding-model")