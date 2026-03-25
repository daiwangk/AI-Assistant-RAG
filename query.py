"""
query.py — Question embedding, ChromaDB retrieval, and Gemini LLM answering.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from db import collection, embed_model

# ---------------------------------------------------------------------------
# Initialise Gemini
# ---------------------------------------------------------------------------
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
PROMPT_TEMPLATE = """You are a helpful assistant. Answer the question based ONLY on the context below.
If the answer is not in the context, say 'I could not find the answer in the uploaded documents.'

Context:
{context}

Question: {question}
Answer:"""

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def answer_question(question: str) -> dict:
    """
    Embed *question*, retrieve the top-4 most relevant chunks from ChromaDB,
    send a grounded prompt to Gemini, and return the answer + sources.
    """

    # --- embed the question -------------------------------------------------
    q_embedding = embed_model.encode([question]).tolist()

    # --- retrieve top 4 chunks ----------------------------------------------
    results = collection.query(query_embeddings=q_embedding, n_results=4)

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return {
            "answer": "I could not find the answer in the uploaded documents.",
            "sources": [],
        }

    # --- build prompt -------------------------------------------------------
    context = "\n\n---\n\n".join(documents)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    # --- call Gemini --------------------------------------------------------
    response = _gemini_model.generate_content(prompt)
    answer_text = response.text.strip()

    # --- collect unique source filenames ------------------------------------
    sources = list({m["source"] for m in metadatas if "source" in m})

    return {"answer": answer_text, "sources": sources}
