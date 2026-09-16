# Autonomous AI Research Agent

**Md Jisan Hossen** — B.Sc. Artificial Intelligence, NUIST

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-ReAct-1C3C3A?logo=langchain&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

> A ReAct agent that decides **on its own** whether to answer from your documents (RAG over FAISS) or from the live web — with multi-turn memory and a fully exposed reasoning trace.

---

## Motivation

Most "chat with your PDF" demos do exactly one thing: retrieval. Real research questions mix private context ("what did this paper claim?") with live information ("what changed in LangChain this month?"). This project builds an agent that *routes* between the two sources autonomously using LangChain's ReAct (Reason + Act) loop, and — importantly for trust and debugging — surfaces every intermediate thought/action step in the UI rather than hiding the chain of reasoning.

---

## What It Does

An end-to-end autonomous AI agent that can:

- **Search the web** in real time (DuckDuckGo, no API key needed)
- **Answer questions from your documents** (PDF, DOCX, TXT) using RAG
- **Remember the conversation** with multi-turn memory
- **Reason step-by-step** using LangChain's ReAct agent framework
- **Interactive UI** via Streamlit + REST API via FastAPI

---

## Architecture

```
User (Streamlit UI)
       │
       ▼
FastAPI Backend  (/chat, /upload, /reset)
       │
       ▼
LangChain ReAct Agent  (gpt-4o-mini)
  ├── Tool 1: DocumentRetriever  →  FAISS Vector Store (local embeddings)
  └── Tool 2: WebSearch          →  DuckDuckGo
       │
       ▼
ConversationBufferMemory  (multi-turn context)
```

---

## Setup Instructions

### Step 1 – Clone the repository

```bash
git clone https://github.com/j1s4nn/AI_Agent.git
cd AI_Agent
```

### Step 2 – Activate your conda environment

```bash
conda activate ml
```

### Step 3 – Install dependencies

```bash
pip install -r requirements.txt
```

> First run downloads the MiniLM embedding model (~90 MB). This is a one-time download.

### Step 4 – Set your OpenAI API key

Copy the example environment file and add your key:

```bash
cp .env.example .env
```

Edit `.env` and replace the placeholder:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

Get a key at → https://platform.openai.com/api-keys  
(`gpt-4o-mini` costs ~$0.0002 per query – very cheap)

### Step 5 – Run the project

```bash
python run.py
```

This starts both servers simultaneously:

| Service | URL |
|---------|-----|
| Streamlit UI | http://localhost:8501 |
| FastAPI Docs | http://localhost:8000/docs |

---

## How to Use

1. **Open** http://localhost:8501 in your browser
2. **Upload documents** (PDF/DOCX/TXT) using the sidebar → click **Ingest Documents**
3. **Ask questions** – the agent will decide whether to search your docs or the web
4. **View reasoning** – click "View reasoning steps" under any response to see the agent's thought process
5. **Reset memory** – click "Clear Chat Memory" to start fresh

---

## File Structure

```
AI_Agent/
│
├── app/
│   └── main.py            ← FastAPI backend (API endpoints)
│
├── utils/
│   ├── agent.py           ← LangChain ReAct agent + memory
│   ├── tools.py           ← WebSearch + DocumentRetriever tools
│   ├── vector_store.py    ← FAISS ingestion & retrieval
│   └── config.py          ← Environment config loader
│
├── data/
│   └── vectorstore/       ← Auto-created; stores FAISS index
│
├── docs/
│   └── sample_query.txt   ← Sample document to test with
│
├── streamlit_app.py        ← Streamlit frontend UI
├── run.py                  ← One-command launcher
├── requirements.txt        ← All dependencies
├── .env.example            ← Template for environment variables
├── .env                    ← Your actual API keys (DO NOT commit)
├── .gitignore
└── README.md
```

---

## Example Queries to Try

After uploading `docs/sample_query.txt`:

> *"What is RAG and how does it work?"*  
> *"What are the benefits of retrieval-augmented generation?"*  
> *"Search the web for the latest LangChain updates"*  
> *"Compare RAG with fine-tuning an LLM"*

---

## System Requirements

| Component | Minimum | This Project Tested On |
|-----------|---------|----------------------|
| RAM | 8 GB | 16 GB |
| GPU | Not required | RTX 3060 |
| Python | 3.10+ | 3.10+ |
| OS | Windows/Linux/Mac | Windows 11 |

---

## Technology Stack

`Python` · `LangChain` (ReAct agent) · `OpenAI API` (gpt-4o-mini) · `FAISS` (vector store) · `sentence-transformers` (all-MiniLM-L6-v2 embeddings) · `DuckDuckGo Search` · `FastAPI` · `Uvicorn` · `Streamlit` · `pypdf` / `python-docx` (document loaders)

## Evaluation & Limitations

This is a service rather than a benchmarked model, so there is no accuracy
table. It was validated functionally: the agent correctly routes document
questions to the RAG tool and live questions to web search, preserves
multi-turn context, and exposes a complete reasoning trace. Known limitations:
retrieval quality depends on the MiniLM embedding and chunking strategy; the
agent inherits gpt-4o-mini's reasoning limits; and there is no automated
end-to-end evaluation harness yet.

## Future Improvements

- Add an evaluation harness (e.g., a RAG QA benchmark) to report retrieval and answer quality instead of relying on manual checks
- Cross-encoder re-ranking of retrieved chunks for borderline queries
- Configurable chunk size / overlap and a persistence layer for the vector store
- Swap the OpenAI dependency for a local LLM (llama.cpp) to run fully offline
- Tool-use guardrails and rate limiting for the web-search tool

## License

MIT License – free to use, modify, and distribute.
