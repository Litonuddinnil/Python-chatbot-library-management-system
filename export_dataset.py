import json
from rag_retriever import gather_all_library_knowledge

print("Exporting database documents to library_dataset.jsonl...")
try:
    docs = gather_all_library_knowledge()
    if docs:
        with open("library_dataset.jsonl", "w", encoding="utf-8") as f:
            for d in docs:
                f.write(json.dumps({
                    "text": d.page_content,
                    "category": d.metadata.get("category"),
                    "title": d.metadata.get("title", "")
                }, ensure_ascii=False) + "\n")
        print(f"Successfully exported {len(docs)} documents to library_dataset.jsonl")
    else:
        print("No documents found in database. Please verify MONGODB_URI and collections are seeded.")
except Exception as e:
    print(f"Failed to export: {e}")
