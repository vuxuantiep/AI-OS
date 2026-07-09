"""JSON-basierter Vector Store mit Kosinus-Ähnlichkeit.

Bewusst dependency-frei (kein numpy/Qdrant) — die Schnittstelle ist so
geschnitten, dass später ein QdrantVectorStore mit identischer API
danebengestellt werden kann (Phase 3 der Roadmap).
"""

import json
import math
import threading
from pathlib import Path

from app.models.documents import ChunkRecord, DocumentMeta


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class JsonVectorStore:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._lock = threading.Lock()
        self._documents: dict[str, DocumentMeta] = {}
        self._chunks: list[ChunkRecord] = []
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        self._documents = {
            doc["id"]: DocumentMeta.model_validate(doc) for doc in raw.get("documents", [])
        }
        self._chunks = [ChunkRecord.model_validate(c) for c in raw.get("chunks", [])]

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "documents": [doc.model_dump(mode="json") for doc in self._documents.values()],
            "chunks": [chunk.model_dump(mode="json") for chunk in self._chunks],
        }
        self._path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def add_document(self, meta: DocumentMeta, chunks: list[ChunkRecord]) -> None:
        with self._lock:
            self._documents[meta.id] = meta
            self._chunks.extend(chunks)
            self._save()

    def list_documents(self) -> list[DocumentMeta]:
        return list(self._documents.values())

    def get_document(self, document_id: str) -> DocumentMeta | None:
        return self._documents.get(document_id)

    def search(
        self, query_embedding: list[float], top_k: int = 4
    ) -> list[tuple[ChunkRecord, float]]:
        scored = [
            (chunk, cosine_similarity(query_embedding, chunk.embedding)) for chunk in self._chunks
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_k]
