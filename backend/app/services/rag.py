from pathlib import Path
import chromadb
from pypdf import PdfReader
from ..config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_DIR)
collection = _client.get_or_create_collection("careers")


def chunk_text(text, size=800, overlap=100):
    out, i = [], 0
    while i < len(text):
        out.append(text[i:i + size])
        i += size - overlap
    return out


def _pages(path: Path):
    if path.suffix.lower() == ".pdf":
        return [(n + 1, p.extract_text() or "") for n, p in enumerate(PdfReader(str(path)).pages)]
    return [(1, path.read_text(encoding="utf-8"))]


def ingest(folder=None) -> int:
    folder = Path(folder or settings.KNOWLEDGE_DIR)
    ids, docs, metas = [], [], []
    for f in sorted(folder.glob("*")):
        if f.suffix.lower() not in (".pdf", ".txt", ".md"):
            continue
        career = f.stem.replace("_", " ").title()
        for page, text in _pages(f):
            for n, c in enumerate(chunk_text(text)):
                ids.append(f"{f.name}-{page}-{n}")
                docs.append(c)
                metas.append({"document": f.name, "page": page, "career": career})
    if docs:
        collection.upsert(ids=ids, documents=docs, metadatas=metas)
    return len(docs)


def ensure_ingested():
    if collection.count() == 0:
        print("Chunks added:", ingest())


def search(query, k=4):
    r = collection.query(query_texts=[query], n_results=k)
    return [
        {"text": d, "source": m["document"], "page": m["page"], "career": m["career"]}
        for d, m in zip(r["documents"][0], r["metadatas"][0])
    ]


def careers():
    return sorted({m["career"] for m in collection.get()["metadatas"]})
