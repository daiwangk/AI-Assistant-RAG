---
title: AI Assistant RAG
emoji: 🤖
colorFrom: indigo
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# 🤖 Gemini RAG Assistant

A complete, end-to-end Retrieval-Augmented Generation (RAG) web application. This assistant allows you to upload PDF and TXT documents and ask questions based strictly on their content, using Google Gemini for reasoning and ChromaDB for local vector storage.

## 🚀 Features

-   **Backend:** FastAPI & Uvicorn for high-performance async API routes.
-   **RAG Engine:**
    -   **ChromaDB:** Local persistent vector database.
    -   **Sentence-Transformers:** `all-MiniLM-L6-v2` runs locally for embeddings (no API key needed for this part).
    -   **Google Gemini:** 2.5 Flash / Pro models for high-quality grounded answers.
-   **Frontend:** Stunning dark-themed single-page UI built with Vanilla JS, CSS, and HTML.
-   **Ingestion:** Supports multi-page PDFs (PyMuPDF) and plain TXT files with smart chunking and overlap.

## 🛠️ Tech Stack

-   **Language:** Python 3.10+
-   **Web Framework:** FastAPI
-   **Vector Database:** ChromaDB
-   **Embeddings:** Sentence-Transformers (`all-MiniLM-L6-v2`)
-   **LLM:** Google Gemini 1.5/2.5 API
-   **Parsing:** PyMuPDF (Fitz)
-   **Frontend:** Vanilla JS / CSS

## 📋 Prerequisites

-   Python 3.10 or higher
-   A Google Gemini API Key (Get one free at [aistudio.google.com](https://aistudio.google.com))

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/daiwangk/AI-Assistant-RAG.git
    cd AI-Assistant-RAG
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate  # macOS/Linux
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment:**
    Create a `.env` file in the root directory:
    ```env
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

## 🏃 Running the Application

1.  **Start the Backend & Frontend:**
    ```bash
    uvicorn main:app --reload
    ```
2.  **Access the Web UI:**
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## 📖 How to Use

1.  **Upload:** Drag and drop a PDF or TXT file into the sidebar.
2.  **Ingest:** Click "Upload" to chunk and embed the document into the local vector DB.
3.  **Chat:** Ask questions in the chat bar. The assistant will search the document and answer using Gemini.

---
Built with ❤️ by [daiwangk](https://github.com/daiwangk)
