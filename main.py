"""
main.py — FastAPI application exposing /upload, /ask, and / routes.
"""

import os
import shutil
import tempfile

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

from ingest import ingest_file
from query import answer_question

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(title="RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")

# Track uploaded filenames for the /uploaded-files endpoint
uploaded_files: list[str] = []


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    sources: list[str]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def serve_frontend():
    """Serve the single-page frontend."""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index_path)


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Accept a PDF or TXT file, ingest it, and store it in ChromaDB."""
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".txt"):
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    # Save to a temp file
    tmp_dir = tempfile.mkdtemp()
    tmp_path = os.path.join(tmp_dir, file.filename)
    try:
        with open(tmp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        num_chunks = ingest_file(tmp_path, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Track the filename
    if file.filename not in uploaded_files:
        uploaded_files.append(file.filename)

    return {
        "message": f"Successfully ingested '{file.filename}' ({num_chunks} chunks).",
        "filename": file.filename,
        "chunks": num_chunks,
    }


@app.post("/ask", response_model=AskResponse)
async def ask_question(req: AskRequest):
    """Retrieve relevant chunks and return a Gemini-powered answer."""
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = answer_question(req.question)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


@app.get("/uploaded-files")
async def list_uploaded_files():
    """Return the list of files that have been uploaded in this session."""
    return {"files": uploaded_files}
