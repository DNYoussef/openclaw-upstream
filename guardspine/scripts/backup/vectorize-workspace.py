"""Vectorize OpenClaw workspace files into Memory MCP ChromaDB.
Chunks each file by section (## headers) and stores with metadata.
"""
import chromadb
import hashlib
import os
import re
from datetime import datetime

CHROMA_PATH = os.path.expanduser("~/.claude/memory-mcp-data/chroma")
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")
COLLECTION_NAME = "agent_memories"

# Files to vectorize
FILES = [
    "IDENTITY.md",
    "BUSINESS.md",
    "TOOLS.md",
    "USER.md",
    "MEMORY.md",
    "SOUL.md",
    "AGENTS.md",
    "HEARTBEAT.md",
    "PATTERNS.md",
    "LEARNINGS.md",
    "ERRORS.md",
    "FEATURE-REQUESTS.md",
]


def chunk_by_sections(text, filename):
    """Split markdown into chunks by ## headers."""
    chunks = []
    current_section = filename
    current_lines = []

    for line in text.split("\n"):
        if line.startswith("## "):
            if current_lines:
                content = "\n".join(current_lines).strip()
                if len(content) > 50:
                    chunks.append((current_section, content))
            current_section = f"{filename} > {line.lstrip('#').strip()}"
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_lines:
        content = "\n".join(current_lines).strip()
        if len(content) > 50:
            chunks.append((current_section, content))

    return chunks


def main():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    now = datetime.utcnow().isoformat()
    added = 0

    for fname in FILES:
        fpath = os.path.join(WORKSPACE_DIR, fname)
        if not os.path.exists(fpath):
            print(f"[skip] {fname} not found")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_by_sections(text, fname)
        print(f"[{fname}] {len(chunks)} chunks")

        for section, content in chunks:
            # Deterministic ID based on file+section
            doc_id = f"workspace_{hashlib.md5(f'{fname}:{section}'.encode()).hexdigest()[:12]}"

            # Upsert (update if exists, insert if new)
            collection.upsert(
                ids=[doc_id],
                documents=[content],
                metadatas=[{
                    "source": f"workspace/{fname}",
                    "section": section,
                    "type": "workspace_doc",
                    "updated_at": now,
                    "confidence": "1.0",
                    "layer": "long_term",
                }],
            )
            added += 1

    print(f"\n[done] Upserted {added} chunks into {COLLECTION_NAME}")
    print(f"[total] Collection now has {collection.count()} items")


if __name__ == "__main__":
    main()
