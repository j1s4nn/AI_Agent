# Autonomous AI Research Agent

**Built by Jisan** | B.Sc. Artificial Intelligence, NUIST  
*Stack: Python · LangChain · FAISS · FastAPI · Streamlit · OpenAI API*

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

### Step 1 – Clone / unzip the project

```bash
cd C:\Users\jisan\OneDrive\Desktop\
# unzip AI_Agent.zip here, then:
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

Open `.env` and replace the placeholder:

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
├── .env                    ← API keys (DO NOT commit to GitHub)
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

## License

MIT License – free to use, modify, and distribute.
