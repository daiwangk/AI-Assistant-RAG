"""
db.py — Shared ChromaDB client, collection, and embedding model.

Both ingest.py and query.py import from here so they use the exact same
PersistentClient instance, avoiding data-visibility issues.
"""

import os
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
COLLECTION_NAME = "documents"

client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
