from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas import DocumentChunk, EvidenceItem, KnowledgeIngestResponse
from app.utils.text import chunk_text, load_text_files

try:
    import chromadb
except Exception:  # pragma: no cover - fallback when chromadb is unavailable
    chromadb = None


class SimpleVectorBackend:
    """Fallback semantic-ish retriever when Chroma is not available.
    It uses cosine similarity over token frequency vectors. This is intentionally
    lightweight so the project remains demo-friendly even before all dependencies
    are installed.
    """

    def __init__(self) -> None:
        self.docs: list[DocumentChunk] = []
        self.term_vectors: list[Counter[str]] = []

    def upsert(self, chunks: list[DocumentChunk]) -> None:
        for chunk in chunks:
            self.docs.append(chunk)
            self.term_vectors.append(self._vectorize(chunk.text))

    def query(self, text: str, n_results: int = 4) -> list[EvidenceItem]:
        query_vec = self._vectorize(text)
        scored: list[tuple[float, DocumentChunk]] = []
        for vec, doc in zip(self.term_vectors, self.docs):
            score = self._cosine(query_vec, vec)
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            EvidenceItem(
                source_name=item.source_name,
                title=item.title,
                excerpt=item.text[:280],
                similarity=round(score, 4),
                metadata=item.metadata,
            )
            for score, item in scored[:n_results]
        ]

    @staticmethod
    def _vectorize(text: str) -> Counter[str]:
        tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text.lower())
        return Counter(tokens)

    @staticmethod
    def _cosine(a: Counter[str], b: Counter[str]) -> float:
        common = set(a) & set(b)
        numerator = sum(a[t] * b[t] for t in common)
        denom_a = math.sqrt(sum(v * v for v in a.values()))
        denom_b = math.sqrt(sum(v * v for v in b.values()))
        if denom_a == 0 or denom_b == 0:
            return 0.0
        return numerator / (denom_a * denom_b)


class KnowledgeBaseService:
    def __init__(self) -> None:
        self.backend_name = settings.vector_backend
        self.collection_name = settings.collection_name
        self.simple_backend = SimpleVectorBackend()
        self.collection = None

        if self.backend_name == "chroma" and chromadb is not None:
            client = chromadb.PersistentClient(path=str(settings.chroma_dir))
            self.collection = client.get_or_create_collection(name=self.collection_name)

    def ingest_folder(self, folder_path: str) -> KnowledgeIngestResponse:
        loaded = load_text_files(folder_path)
        chunks: list[DocumentChunk] = []
        files_count = 0

        for name, raw_text in loaded:
            files_count += 1
            title = Path(name).stem.replace("_", " ").title()
            for idx, piece in enumerate(chunk_text(raw_text)):
                chunks.append(
                    DocumentChunk(
                        source_name=name,
                        title=title,
                        text=piece,
                        metadata={"chunk_index": idx, "folder": folder_path},
                    )
                )

        if self.collection is not None:
            self.collection.upsert(
                ids=[c.chunk_id for c in chunks],
                documents=[c.text for c in chunks],
                metadatas=[
                    {
                        "source_name": c.source_name,
                        "title": c.title,
                        **c.metadata,
                    }
                    for c in chunks
                ],
            )
        else:
            self.simple_backend.upsert(chunks)

        return KnowledgeIngestResponse(
            ingested_files=files_count,
            ingested_chunks=len(chunks),
            collection_name=self.collection_name,
            backend="chroma" if self.collection is not None else "simple_fallback",
        )

    def query(self, text: str, n_results: int = 4) -> list[EvidenceItem]:
        if self.collection is not None:
            result = self.collection.query(
                query_texts=[text],
                n_results=n_results,
            )
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0] if "distances" in result else [None] * len(docs)
            evidence: list[EvidenceItem] = []
            for doc, meta, dist in zip(docs, metas, distances):
                evidence.append(
                    EvidenceItem(
                        source_name=meta.get("source_name", "unknown"),
                        title=meta.get("title", "Untitled"),
                        excerpt=doc[:280],
                        similarity=None if dist is None else round(1 - float(dist), 4),
                        metadata=meta,
                    )
                )
            return evidence

        return self.simple_backend.query(text=text, n_results=n_results)
