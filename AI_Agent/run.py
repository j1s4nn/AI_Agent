"""
run.py
One-command launcher: starts FastAPI backend + Streamlit frontend simultaneously.

Usage:
    python run.py
"""

import subprocess
import sys
import time
import threading
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def run_backend():
    print("\n[Backend] Starting FastAPI on http://localhost:8000 ...\n")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--reload", "--port", "8000"],
        cwd=ROOT
    )


def run_frontend():
    time.sleep(3)   # give backend a moment to start
    print("\n[Frontend] Starting Streamlit on http://localhost:8501 ...\n")
    subprocess.run(
        [sys.executable, "-m", "streamlit", "run", "streamlit_app.py", "--server.port", "8501"],
        cwd=ROOT
    )


if __name__ == "__main__":
    print("=" * 55)
    print("   Autonomous AI Research Agent  –  by Jisan")
    print("=" * 55)
    print("Starting backend + frontend...\n")
    print("  API docs  →  http://localhost:8000/docs")
    print("  App UI    →  http://localhost:8501")
    print("=" * 55)

    t_backend  = threading.Thread(target=run_backend,  daemon=True)
    t_frontend = threading.Thread(target=run_frontend, daemon=False)

    t_backend.start()
    t_frontend.start()
    t_frontend.join()
