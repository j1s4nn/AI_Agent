"""
utils/tools.py
Custom LangChain tools used by the agent:
  1. DuckDuckGoSearchTool  – live web search (no API key needed)
  2. DocumentRetrieverTool – searches the uploaded knowledge base (FAISS)
"""

from langchain.tools import Tool
from duckduckgo_search import DDGS

from utils.vector_store import similarity_search


# ── Tool 1: Web Search ────────────────────────────────────────────────────────

def web_search(query: str) -> str:
    """Search the web using DuckDuckGo and return a summary of top results."""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results found on the web."
        formatted = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "No title")
            body  = r.get("body",  "No snippet")
            href  = r.get("href",  "")
            formatted.append(f"[{i}] {title}\n{body}\nSource: {href}")
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Web search failed: {str(e)}"


web_search_tool = Tool(
    name="WebSearch",
    func=web_search,
    description=(
        "Use this tool to search the internet for recent or general information. "
        "Input should be a clear search query string."
    ),
)


# ── Tool 2: Document Retriever (RAG) ─────────────────────────────────────────

def retrieve_documents(query: str) -> str:
    """Search the uploaded knowledge base and return relevant excerpts."""
    chunks = similarity_search(query)
    if not chunks:
        return (
            "No documents have been uploaded yet, or no relevant content found. "
            "Please upload a document first using the sidebar."
        )
    result = "\n\n---\n\n".join(
        [f"[Excerpt {i+1}]:\n{chunk}" for i, chunk in enumerate(chunks)]
    )
    return result


document_retriever_tool = Tool(
    name="DocumentRetriever",
    func=retrieve_documents,
    description=(
        "Use this tool to search the uploaded knowledge base (PDF, DOCX, or TXT files). "
        "Input should be a question or keywords related to the documents. "
        "Always try this before WebSearch if the question might relate to uploaded files."
    ),
)


# ── Export all tools ──────────────────────────────────────────────────────────
ALL_TOOLS = [document_retriever_tool, web_search_tool]
