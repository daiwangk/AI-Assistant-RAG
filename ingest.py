"""
ingest.py — PDF/TXT parsing, text chunking, embedding, and ChromaDB storage.
"""

import os
import fitz  # PyMuPDF
from db import collection, embed_model

# ---------------------------------------------------------------------------
# Text extraction helpers
# ---------------------------------------------------------------------------

def _extract_text_from_pdf(file_path: str) -> list[dict]:
    """Return a list of {'text': ..., 'page': ...} dicts, one per page."""
    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        text = doc[page_num].get_text()
        if text.strip():
            pages.append({"text": text, "page": page_num + 1})
    doc.close()
    return pages


def _extract_text_from_txt(file_path: str) -> list[dict]:
    """Return the full text of a .txt file wrapped in a single-element list."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return [{"text": text, "page": 1}]


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------

def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split *text* into overlapping chunks of roughly *chunk_size* characters."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def ingest_file(file_path: str, file_name: str) -> int:
    """
    Parse *file_path*, chunk, embed, and store in ChromaDB.

    If *file_name* was previously ingested its old chunks are deleted first.
    Returns the number of new chunks stored.
    """
    ext = os.path.splitext(file_name)[1].lower()

    # --- extract raw text ---------------------------------------------------
    if ext == ".pdf":
        pages = _extract_text_from_pdf(file_path)
    elif ext == ".txt":
        pages = _extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # --- delete old chunks for this filename --------------------------------
    try:
        existing = collection.get(where={"source": file_name})
        if existing and existing["ids"]:
            collection.delete(ids=existing["ids"])
    except Exception:
        pass  # collection might be empty / no match — that's fine

    # --- chunk and embed ----------------------------------------------------
    all_chunks: list[str] = []
    all_metas: list[dict] = []
    all_ids: list[str] = []

    chunk_index = 0
    for page_info in pages:
        chunks = _chunk_text(page_info["text"])
        for chunk in chunks:
            if not chunk.strip():
                continue
            all_chunks.append(chunk)
            all_metas.append({
                "source": file_name,
                "page": page_info["page"],
                "chunk_index": chunk_index,
            })
            all_ids.append(f"{file_name}__chunk_{chunk_index}")
            chunk_index += 1

    if not all_chunks:
        return 0

    # Generate embeddings
    embeddings = embed_model.encode(all_chunks).tolist()

    # Store in ChromaDB
    collection.add(
        ids=all_ids,
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metas,
    )

    return len(all_chunks)
