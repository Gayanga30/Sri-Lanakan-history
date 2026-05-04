"""
ingest.py
---------
Loads every file in ./sources/, splits the text into chunks, embeds each chunk
with a local sentence-transformers model, and writes the result to a Chroma
vector store at ./vectorstore/.

Run this once after you add or change source files:
    python ingest.py

Supported file types:
    .pdf  - parsed with pypdf
    .txt  - read as UTF-8
    .md   - read as UTF-8
    .html / .htm - text extracted with BeautifulSoup
"""

from __future__ import annotations

import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from bs4 import BeautifulSoup
from pypdf import PdfReader

SOURCES_DIR = Path("sources")
DB_DIR = Path("vectorstore")
COLLECTION_NAME = "sri_lankan_history"
EMBED_MODEL = "all-MiniLM-L6-v2"   # ~80MB, runs on CPU, no API key needed
CHUNK_SIZE = 800                    # characters per chunk
CHUNK_OVERLAP = 150                 # overlap so context isn't cut mid-sentence


def read_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def read_html(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    return soup.get_text(separator="\n")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


READERS = {
    ".pdf": read_pdf,
    ".html": read_html,
    ".htm": read_html,
    ".txt": read_text,
    ".md": read_text,
}


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Naive character chunker. Works fine for RAG; swap for a smarter splitter later if needed."""
    text = " ".join(text.split())  # collapse whitespace
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def main() -> None:
    if not SOURCES_DIR.exists():
        print(f"No {SOURCES_DIR}/ folder found. Create it and drop your source files in.")
        sys.exit(1)

    files = [p for p in SOURCES_DIR.rglob("*") if p.is_file() and p.suffix.lower() in READERS]
    if not files:
        print(f"No supported files in {SOURCES_DIR}/. Drop in PDFs, HTML, or text files.")
        sys.exit(1)

    print(f"Found {len(files)} source file(s).")

    # Local embeddings - downloads model on first run.
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)

    DB_DIR.mkdir(exist_ok=True)
    client = chromadb.PersistentClient(path=str(DB_DIR))

    # Wipe and rebuild for a clean ingest each run.
    if COLLECTION_NAME in [c.name for c in client.list_collections()]:
        client.delete_collection(COLLECTION_NAME)
    collection = client.create_collection(name=COLLECTION_NAME, embedding_function=embed_fn)

    total_chunks = 0
    for path in files:
        try:
            raw = READERS[path.suffix.lower()](path)
        except Exception as exc:
            print(f"  skipped {path.name}: {exc}")
            continue

        chunks = chunk_text(raw)
        if not chunks:
            print(f"  empty: {path.name}")
            continue

        ids = [f"{path.name}::{i}" for i in range(len(chunks))]
        metadatas = [{"source": path.name, "chunk": i} for i in range(len(chunks))]
        collection.add(documents=chunks, ids=ids, metadatas=metadatas)
        total_chunks += len(chunks)
        print(f"  ingested {path.name}: {len(chunks)} chunks")

    print(f"\nDone. {total_chunks} chunks in collection '{COLLECTION_NAME}' at {DB_DIR}/")


if __name__ == "__main__":
    main()
