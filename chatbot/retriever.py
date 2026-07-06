import logging
import threading
import time

import config
from database import get_collection
from chatbot.preprocess import clean_text

from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

logger = logging.getLogger(__name__)

# Initialize a lightweight embedding model locally (runs fully offline)
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# ---------------------------------------------------------------------------
# In-process cache for the built index. Rebuilding FAISS + BM25 on every
# query re-embeds the entire dataset, which is slow and hits MongoDB on
# every request. We build once and refresh on a TTL / manual trigger.
# ---------------------------------------------------------------------------
_INDEX_CACHE = {
    "keyword_retriever": None,
    "vector_store": None,
    "built_at": 0.0,
}
_INDEX_LOCK = threading.Lock()
_INDEX_TTL_SECONDS = 300  # rebuild at most every 5 minutes; tune to your write frequency


def _clean(value: str) -> str:
    """Run text through the project's clean_text step, tolerating non-str input."""
    if not value:
        return ""
    try:
        return clean_text(str(value))
    except Exception:
        # Never let a bad clean_text call take down document construction
        return str(value).strip()


def _safe_get_collection(attr_name: str):
    """Fetch a Mongo collection by config attribute name without crashing on typos."""
    collection_ref = getattr(config, attr_name, None)
    if collection_ref is None:
        logger.warning("Config attribute '%s' not found; skipping that collection.", attr_name)
        return None
    return get_collection(collection_ref)


def gather_all_library_knowledge() -> list:
    """
    Scans all MongoDB collections and transforms them into LangChain Document
    objects with cleaned text and rich, traceable metadata.
    """
    langchain_docs = []

    # 1. Books
    books_col = _safe_get_collection("BooksCollection")
    if books_col is not None:
        for b in books_col.find({}, {"_id": 0}):
            title = _clean(b.get("title", b.get("book_title", "")))
            desc = _clean(b.get("longDescription", b.get("description", "")))
            authors_raw = b.get("authors", b.get("author_name", ""))
            authors = _clean(", ".join(authors_raw) if isinstance(authors_raw, list) else authors_raw)

            if not title and not desc:
                continue  # skip near-empty records; they only add noise

            text_content = (
                f"Book Title: {title}. Author: {authors}. Course Code: {b.get('course_code', 'N/A')}. "
                f"Department: {_clean(b.get('department', ''))}. Semester: {b.get('semester', 'N/A')}. "
                f"Genre: {_clean(b.get('genre', ''))}. Description: {desc}. "
                f"Available Copies: {b.get('available_copies', 0)}."
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "books", "title": title},
            ))

    # 2. Users / Librarian Profiles
    users_col = _safe_get_collection("UsersCollection")
    if users_col is not None:
        for u in users_col.find({}, {"_id": 0, "password": 0, "token": 0, "resetToken": 0}):
            name = _clean(u.get("name", ""))
            if not name:
                continue
            text_content = (
                f"User Profile Name: {name}. Email: {u.get('email', '')}. "
                f"System Role: {u.get('role', '')}. Identity ID: {u.get('studentId', u.get('facultyId', 'N/A'))}"
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "users", "title": name},
            ))

    # 3. System Notifications
    notif_col = _safe_get_collection("NotificationsCollection")
    if notif_col is not None:
        for n in notif_col.find({}, {"_id": 0}):
            created_at = n.get("createdAt", "")
            date_str = created_at.get("$date", "") if isinstance(created_at, dict) else created_at
            message = _clean(n.get("message", ""))
            if not message:
                continue

            text_content = (
                f"Notification Alert Type: {n.get('type', 'pending')}. Alert Log Message: {message}. "
                f"Sender From Email: {n.get('from_email', '')}. Target To Email: {n.get('toEmail', '')}. "
                f"Student Identity: {n.get('student_name', '')}. Read Status: {n.get('isRead', False)}. Date: {date_str}"
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "notifications"},
            ))

    # 4. Book Loan Submissions
    sub_col = _safe_get_collection("SubmissionsCollection")
    if sub_col is not None:
        for s in sub_col.find({}, {"_id": 0}):
            due_date = s.get("dueDate", "")
            due_str = due_date.get("$date", "") if isinstance(due_date, dict) else due_date
            author_raw = s.get("author", "")
            author = _clean(", ".join(author_raw) if isinstance(author_raw, list) else author_raw)
            book_title = _clean(s.get("book_title", ""))
            if not book_title:
                continue

            text_content = (
                f"Submission Event Borrowing Student Name: {s.get('student_name', '')}. "
                f"Student Account Email: {s.get('student_email', '')}. "
                f"Requested Book Title: {book_title} by Author: {author}. Department: {s.get('department', '')}. "
                f"Processing Application Status: {s.get('status', 'pending')}. Return Submission Due Date: {due_str}"
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "submissions", "title": book_title},
            ))

    # 5. Faculty Lecture Notes
    notes_col = _safe_get_collection("FacultyNotesCollection")
    if notes_col is not None:
        for fn in notes_col.find({}, {"_id": 0}):
            title = _clean(fn.get("title", ""))
            if not title:
                continue
            text_content = (
                f"Academic Faculty Lecture Notes. Subject Title: {title}. Department: {fn.get('department', '')}. "
                f"Semester Course: {fn.get('semester', '')}. Resource Material Type: {fn.get('resourceType', '')}. "
                f"Shared By Professor Teacher Name: {fn.get('teacherName', '')}. Access Link URL: {fn.get('pdfUrl', '')}"
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "faculty_notes", "title": title},
            ))

    # 6. Book Reviews
    reviews_col = _safe_get_collection("ReviewsCollection")
    if reviews_col is not None:
        for r in reviews_col.find({}, {"_id": 0}):
            comment = _clean(r.get("comment", ""))
            if not comment:
                continue
            text_content = (
                f"User Evaluation Feedback Comment: {comment}. Submitted By Student User Name: {r.get('name', '')}. "
                f"Numeric Score Evaluation Rating: {r.get('rating', 5)} Stars"
            )
            langchain_docs.append(Document(
                page_content=text_content,
                metadata={"category": "reviews"},
            ))

    logger.info("Gathered %d documents across all collections.", len(langchain_docs))
    return langchain_docs


def _build_index_structures(top_k: int):
    """Builds raw BM25 and FAISS objects separately to avoid EnsembleRetriever import issues."""
    docs = gather_all_library_knowledge()
    if not docs:
        logger.warning("No documents returned from MongoDB; index structures not built.")
        return None, None

    keyword_retriever = BM25Retriever.from_documents(docs)
    keyword_retriever.k = top_k

    vector_store = FAISS.from_documents(docs, embeddings_model)
    
    return keyword_retriever, vector_store


def _get_or_build_cached_structures(top_k: int, force_refresh: bool = False):
    """Returns cached retrievers, rebuilding them if stale or forced."""
    now = time.time()
    with _INDEX_LOCK:
        is_stale = (now - _INDEX_CACHE["built_at"]) > _INDEX_TTL_SECONDS
        if force_refresh or is_stale or _INDEX_CACHE["keyword_retriever"] is None:
            kw_ret, v_store = _build_index_structures(top_k)
            _INDEX_CACHE["keyword_retriever"] = kw_ret
            _INDEX_CACHE["vector_store"] = v_store
            _INDEX_CACHE["built_at"] = now
        return _INDEX_CACHE["keyword_retriever"], _INDEX_CACHE["vector_store"]


def retrieve_context(query: str, top_k: int = 4, force_refresh: bool = False) -> str:
    """
    Hybrid ensemble retrieval combining BM25 keyword matching and FAISS
    semantic search. Uses custom result interleaving to replicate EnsembleRetriever 
    without import version errors.
    """
    if not query or not query.strip():
        return ""

    try:
        kw_retriever, vector_store = _get_or_build_cached_structures(top_k, force_refresh=force_refresh)
        if kw_retriever is None or vector_store is None:
            return ""

        # 1. Execute Keyword Match (BM25)
        bm25_docs = kw_retriever.invoke(query)

        # 2. Execute Semantic Match (FAISS)
        semantic_retriever = vector_store.as_retriever(search_kwargs={"k": top_k})
        faiss_docs = semantic_retriever.invoke(query)

        # 3. Interleave and deduplicate results manually (Native Ensemble logic)
        seen_contents = set()
        combined_docs = []

        for d1, d2 in zip(bm25_docs, faiss_docs):
            if d1.page_content not in seen_contents:
                seen_contents.add(d1.page_content)
                combined_docs.append(d1)
            if d2.page_content not in seen_contents:
                seen_contents.add(d2.page_content)
                combined_docs.append(d2)

        # Handle remaining items if one list is longer than the other
        for d in bm25_docs + faiss_docs:
            if d.page_content not in seen_contents:
                seen_contents.add(d.page_content)
                combined_docs.append(d)

        final_docs = combined_docs[:top_k]
        return "\n".join(d.page_content for d in final_docs)

    except Exception:
        logger.exception("Retriever error while handling query: %s", query)
        return ""


def refresh_index():
    """Call this after writes to MongoDB (new book, review, etc.) to force a rebuild
    on the next query, instead of waiting for the TTL to expire."""
    with _INDEX_LOCK:
        _INDEX_CACHE["built_at"] = 0.0