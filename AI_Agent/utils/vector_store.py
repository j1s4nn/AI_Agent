"""
utils/vector_store.py
Build and query a FAISS vector store from uploaded documents.
Uses HuggingFace sentence-transformers (runs locally – no API cost).
"""

import os
import pickle
from typing import List

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

from utils.config import VECTOR_STORE_DIR, TOP_K_DOCS

# Free, local embedding model (downloaded once, ~90 MB)
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_embeddings = None


def _get_embeddings() -> HuggingFaceEmbeddings:
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    return _embeddings


def _load_document(file_path: str):
    """Load a PDF, DOCX, or TXT file and return LangChain documents."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in (".docx", ".doc"):
        loader = Docx2txtLoader(file_path)
    else:
        loader = TextLoader(file_path, encoding="utf-8")
    return loader.load()


def build_vector_store(file_paths: List[str]) -> FAISS:
    """
    Ingest documents → chunk → embed → save FAISS index to disk.
    Returns the FAISS vector store.
    """
    all_docs = []
    for fp in file_paths:
        docs = _load_document(fp)
        all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=80)
    chunks = splitter.split_documents(all_docs)

    embeddings = _get_embeddings()
    vs = FAISS.from_documents(chunks, embeddings)

    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    vs.save_local(VECTOR_STORE_DIR)
    return vs


def load_vector_store() -> FAISS | None:
    """Load existing FAISS index from disk. Returns None if not built yet."""
    index_path = os.path.join(VECTOR_STORE_DIR, "index.faiss")
    if not os.path.exists(index_path):
        return None
    embeddings = _get_embeddings()
    return FAISS.load_local(VECTOR_STORE_DIR, embeddings, allow_dangerous_deserialization=True)


def similarity_search(query: str, vs: FAISS = None) -> List[str]:
    """Return top-K relevant text chunks for a query."""
    if vs is None:
        vs = load_vector_store()
    if vs is None:
        return []
    results = vs.similarity_search(query, k=TOP_K_DOCS)
    return [doc.page_content for doc in results]
