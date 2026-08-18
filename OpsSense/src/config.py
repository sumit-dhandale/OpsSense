import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "incidents"

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION = os.getenv("QDRANT_COLLECTION", "incident_memory")
# MiniLM-L6-v2 (Step 4) emits 384-d vectors. Collection size is fixed at create time.
VECTOR_SIZE = 384
