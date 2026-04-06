"""
app/main.py
FastAPI backend – exposes the agent and document ingestion via REST API.

Endpoints:
  POST /chat          – send a message, get agent response
  POST /upload        – upload PDF/DOCX/TXT to knowledge base
  POST /reset         – clear chat memory
  GET  /health        – health check
"""

import os
import shutil
import tempfile
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from utils.agent import get_agent, reset_agent
from utils.vector_store import build_vector_store

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Autonomous AI Research Agent",
    description="By Jisan – LangChain + FAISS + FastAPI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Streamlit frontend on localhost
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Schemas ───────────────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer:     str
    steps:      List[str] = []   # intermediate reasoning steps


class UploadResponse(BaseModel):
    message:       str
    files_ingested: List[str]


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "agent": "ready"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Send a message to the agent and receive a response."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        agent = get_agent()
        result = agent.invoke({"input": req.message})

        answer = result.get("output", "")
        steps  = []
        for action, observation in result.get("intermediate_steps", []):
            steps.append(f"🔧 Tool: {action.tool}\n   Input: {action.tool_input}\n   Output: {str(observation)[:300]}...")

        return ChatResponse(answer=answer, steps=steps)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload one or more documents to build the FAISS knowledge base."""
    allowed_ext = {".pdf", ".docx", ".doc", ".txt"}
    saved_paths = []
    tmp_dir = tempfile.mkdtemp()

    try:
        for file in files:
            ext = os.path.splitext(file.filename)[1].lower()
            if ext not in allowed_ext:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.filename}. Allowed: PDF, DOCX, TXT"
                )
            dest = os.path.join(tmp_dir, file.filename)
            with open(dest, "wb") as f:
                f.write(await file.read())
            saved_paths.append(dest)

        build_vector_store(saved_paths)
        names = [os.path.basename(p) for p in saved_paths]
        return UploadResponse(
            message=f"Successfully ingested {len(names)} document(s) into the knowledge base.",
            files_ingested=names,
        )
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


@app.post("/reset")
def reset():
    """Clear agent memory and start a fresh conversation."""
    reset_agent()
    return {"message": "Agent memory cleared. New conversation started."}
