import json
from rag_retriever import gather_all_library_knowledge

docs = gather_all_library_knowledge()

with open("library_dataset.jsonl", "w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps({
            "text": d.page_content,
            "category": d.metadata.get("category"),
            "title": d.metadata.get("title", "")
        }, ensure_ascii=False) + "\n")

print(f"Exported {len(docs)} documents to library_dataset.jsonl")
