#import spaces  # must be imported before torch/sentence-transformers get loaded hugging face a deployment time 

import os
import logging
import threading
import time

import config
from database import get_collection
from preprocess import clean_text

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

# ✅ Safe loading of local or public embedding model
model_path = "./my-library-embedding-model"
if os.path.exists(model_path) and os.path.isdir(model_path):
    try:
        embeddings_model = HuggingFaceEmbeddings(model_name=model_path)
    except Exception as e:
        logger.warning(f"Failed to load local embedding model from {model_path}: {e}. Falling back to public model.")
        embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
else:
    # Fallback to standard model during initialization/training phases
    embeddings_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# ------------------------------------------------------------------
# CACHE
# ------------------------------------------------------------------
_INDEX_CACHE = {
    "keyword_retriever": None,
    "vector_store": None,
    "built_at": 0.0,
}
_INDEX_LOCK = threading.Lock()
_INDEX_TTL_SECONDS = 300


# ------------------------------------------------------------------
# UTILS
# ------------------------------------------------------------------
def _clean(value: str) -> str:
    if not value:
        return ""
    try:
        return clean_text(str(value))
    except Exception:
        return str(value).strip()


def _safe_get_collection(attr_name: str):
    collection_ref = getattr(config, attr_name, None)
    if collection_ref is None:
        logger.warning("Config '%s' not found.", attr_name)
        return None
    return get_collection(collection_ref)


# ------------------------------------------------------------------
# KNOWLEDGE GATHERING (SAFE ONLY)
# ------------------------------------------------------------------
def gather_all_library_knowledge() -> list:
    """
    ONLY academic / public knowledge.
    ❌ No users, emails, IDs, notifications.
    """
    docs = []

    # 1️⃣ BOOKS
    books_col = _safe_get_collection("BooksCollection")
    if books_col is not None:
        try:
            for b in books_col.find({}, {"_id": 0}):
                title = _clean(b.get("title", b.get("book_title", "")))
                desc = _clean(b.get("longDescription", b.get("description", "")))
                author = _clean(b.get("author_name", ""))

                if not title or not desc:
                    continue

                content = (
                    f"Book Title: {title}. "
                    f"Author: {author}. "
                    f"Department: {_clean(b.get('department', ''))}. "
                    f"Semester: {b.get('semester', '')}. "
                    f"Description: {desc}."
                )

                docs.append(Document(
                    page_content=content[:1200],  #  HARD TRUNCATION
                    metadata={"category": "books", "title": title}
                ))
        except Exception as e:
            logger.error(f"Error reading books collection: {e}")

    # 2️⃣ FACULTY NOTES
    notes_col = _safe_get_collection("FacultyNotesCollection")
    if notes_col is not None:
        try:
            for n in notes_col.find({}, {"_id": 0}):
                title = _clean(n.get("title", ""))
                if not title:
                    continue

                content = (
                    f"Lecture Notes Title: {title}. "
                    f"Department: {_clean(n.get('department', ''))}. "
                    f"Semester: {_clean(n.get('semester', ''))}. "
                    f"Topic Description: {_clean(n.get('summary', ''))}."
                )

                docs.append(Document(
                    page_content=content[:1200],
                    metadata={"category": "faculty_notes", "title": title}
                ))
        except Exception as e:
            logger.error(f"Error reading faculty notes: {e}")

    # 3️⃣ REVIEWS (OPTIONAL, SAFE)
    reviews_col = _safe_get_collection("reviewsCollection")
    if reviews_col is not None:
        try:
            for r in reviews_col.find({}, {"_id": 0}):
                comment = _clean(r.get("comment", ""))
                if not comment:
                    continue

                docs.append(Document(
                    page_content=f"Student feedback: {comment}",
                    metadata={"category": "reviews"}
                ))
        except Exception as e:
            logger.error(f"Error reading reviews: {e}")

    logger.info("RAG docs loaded: %d", len(docs))
    return docs


# ------------------------------------------------------------------
# INDEX BUILD
# ------------------------------------------------------------------
def _build_index(top_k: int):
    docs = gather_all_library_knowledge()
    if not docs:
        return None, None

    bm25 = BM25Retriever.from_documents(docs)
    bm25.k = top_k

    faiss_store = FAISS.from_documents(docs, embeddings_model)
    return bm25, faiss_store


def _get_cached_index(top_k: int, force: bool = False):
    now = time.time()
    with _INDEX_LOCK:
        stale = (now - _INDEX_CACHE["built_at"]) > _INDEX_TTL_SECONDS
        if force or stale or _INDEX_CACHE["keyword_retriever"] is None:
            bm25, faiss = _build_index(top_k)
            _INDEX_CACHE.update({
                "keyword_retriever": bm25,
                "vector_store": faiss,
                "built_at": now,
            })
        return _INDEX_CACHE["keyword_retriever"], _INDEX_CACHE["vector_store"]


# ------------------------------------------------------------------
# PUBLIC API
# ------------------------------------------------------------------
#@spaces.GPU  #hugging face a deployment time
def retrieve_context(query: str, top_k: int = 4) -> str:
    """
    Academic-only RAG context.
    """
    if not query or len(query.strip()) < 3:
        return ""

    try:
        bm25, faiss = _get_cached_index(top_k)
        if not bm25 or not faiss:
            return ""

        kw_docs = bm25.invoke(query)
        sem_docs = faiss.as_retriever(search_kwargs={"k": top_k}).invoke(query)

        seen = set()
        final_docs = []

        for d in kw_docs + sem_docs:
            if d.page_content not in seen:
                seen.add(d.page_content)
                final_docs.append(d)

        final_docs = final_docs[:top_k]

        return "\n".join(d.page_content for d in final_docs)

    except Exception:
        logger.exception("RAG retrieval failed for query: %s", query)
        return ""


def refresh_index():
    with _INDEX_LOCK:
        _INDEX_CACHE["built_at"] = 0.0