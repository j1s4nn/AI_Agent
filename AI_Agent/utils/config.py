"""
utils/config.py
Central configuration – reads .env and exposes typed settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME:     str = os.getenv("MODEL_NAME", "gpt-4o-mini")
API_PORT:       int = int(os.getenv("API_PORT", "8000"))
TOP_K_DOCS:     int = int(os.getenv("TOP_K_DOCS", "4"))

# Local FAISS index storage path
VECTOR_STORE_DIR: str = os.path.join(os.path.dirname(__file__), "..", "data", "vectorstore")

if not OPENAI_API_KEY or OPENAI_API_KEY.startswith("sk-your"):
    raise EnvironmentError(
        "\n[ERROR] OPENAI_API_KEY is not set.\n"
        "1. Open the .env file in the project root.\n"
        "2. Replace 'sk-your-openai-api-key-here' with your real key.\n"
        "3. Get a key at https://platform.openai.com/api-keys\n"
    )
