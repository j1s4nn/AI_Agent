"""
streamlit_app.py
Streamlit frontend for the Autonomous AI Research Agent.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import requests
import json
import time

# ── Config ────────────────────────────────────────────────────────────────────
API_BASE = "http://localhost:8000"

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1923; color: #e0eaf0; }
    .main-title {
        font-size: 2rem; font-weight: 800;
        background: linear-gradient(90deg, #2ab09a, #1a6b5c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .chat-user {
        background: #1a2a38; border-radius: 10px;
        padding: 10px 14px; margin: 6px 0;
        border-left: 3px solid #2ab09a;
    }
    .chat-agent {
        background: #162030; border-radius: 10px;
        padding: 10px 14px; margin: 6px 0;
        border-left: 3px solid #1a6b5c;
    }
    .step-box {
        background: #0d1820; border-radius: 6px;
        padding: 8px 12px; font-size: 0.78rem;
        color: #7ecfc0; font-family: monospace;
        margin: 4px 0;
    }
    .status-ok  { color: #2ab09a; font-weight: 600; }
    .status-err { color: #e05a5a; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # {"role": "user"|"agent", "content": str, "steps": []}
if "docs_uploaded" not in st.session_state:
    st.session_state.docs_uploaded = []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🤖 AI Research Agent")
    st.markdown("*Built by **Jisan** · LangChain + FAISS + FastAPI*")
    st.divider()

    # Health check
    st.markdown("### ⚙️ Backend Status")
    try:
        r = requests.get(f"{API_BASE}/health", timeout=3)
        if r.status_code == 200:
            st.markdown('<span class="status-ok">● Connected</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-err">● Error</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="status-err">● Offline – start the backend first</span>', unsafe_allow_html=True)
        st.code("uvicorn app.main:app --reload", language="bash")

    st.divider()

    # Document upload
    st.markdown("### 📂 Upload Knowledge Base")
    st.caption("Supports PDF, DOCX, TXT")
    uploaded_files = st.file_uploader(
        "Choose files", type=["pdf", "docx", "txt"],
        accept_multiple_files=True, label_visibility="collapsed"
    )

    if st.button("📤 Ingest Documents", use_container_width=True):
        if not uploaded_files:
            st.warning("Please select at least one file.")
        else:
            with st.spinner("Building knowledge base..."):
                file_tuples = [
                    ("files", (f.name, f.getvalue(), f.type))
                    for f in uploaded_files
                ]
                try:
                    resp = requests.post(f"{API_BASE}/upload", files=file_tuples, timeout=120)
                    data = resp.json()
                    if resp.status_code == 200:
                        st.success(data["message"])
                        st.session_state.docs_uploaded.extend(data["files_ingested"])
                    else:
                        st.error(data.get("detail", "Upload failed."))
                except Exception as e:
                    st.error(f"Upload error: {e}")

    if st.session_state.docs_uploaded:
        st.markdown("**Ingested files:**")
        for f in set(st.session_state.docs_uploaded):
            st.markdown(f"- 📄 `{f}`")

    st.divider()

    # Reset
    if st.button("🗑️ Clear Chat Memory", use_container_width=True):
        try:
            requests.post(f"{API_BASE}/reset", timeout=10)
            st.session_state.messages = []
            st.success("Memory cleared!")
            st.rerun()
        except:
            st.error("Could not reach backend.")

    st.divider()
    st.caption("Model: gpt-4o-mini · Embeddings: MiniLM-L6-v2 (local)")


# ── Main chat area ────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">Autonomous AI Research Agent</div>', unsafe_allow_html=True)
st.caption("Ask anything — I can search the web or query your uploaded documents.")
st.divider()

# Render chat history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-user">👤 <strong>You:</strong> {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-agent">🤖 <strong>Agent:</strong></div>', unsafe_allow_html=True)
        st.markdown(msg["content"])
        if msg.get("steps"):
            with st.expander("🔍 View reasoning steps"):
                for step in msg["steps"]:
                    st.markdown(f'<div class="step-box">{step}</div>', unsafe_allow_html=True)

# Input
st.divider()
col1, col2 = st.columns([5, 1])
with col1:
    user_input = st.text_input(
        "Your question",
        placeholder="e.g. Summarize my uploaded document / What is RAG? / Latest AI news...",
        label_visibility="collapsed",
        key="chat_input"
    )
with col2:
    send = st.button("Send ➤", use_container_width=True)

if send and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Agent is thinking..."):
        try:
            resp = requests.post(
                f"{API_BASE}/chat",
                json={"message": user_input},
                timeout=120
            )
            data = resp.json()
            if resp.status_code == 200:
                st.session_state.messages.append({
                    "role": "agent",
                    "content": data["answer"],
                    "steps":   data.get("steps", []),
                })
            else:
                st.session_state.messages.append({
                    "role": "agent",
                    "content": f"⚠️ Error: {data.get('detail', 'Unknown error')}",
                    "steps": [],
                })
        except Exception as e:
            st.session_state.messages.append({
                "role": "agent",
                "content": f"⚠️ Could not reach backend: {e}",
                "steps": [],
            })
    st.rerun()
