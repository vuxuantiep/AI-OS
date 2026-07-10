"""Qdrant-Implementierung des VectorStore-Vertrags (Roadmap Phase 3b).

Gleiche Schnittstelle wie JsonVectorStore — der RagService merkt keinen
Unterschied. Auswahl über AIOS_VECTOR_BACKEND=qdrant.

Zwei Collections:
- <prefix>_chunks:    ein Punkt pro Chunk, Vektor = Embedding, Payload = Text
- <prefix>_documents: ein Punkt pro Dokument (Dummy-Vektor), Payload = Metadaten
"""

from typing import Any
from uuid import UUID

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from app.models.documents import ChunkRecord, DocumentMeta


def _point_id(hex_id: str) -> str:
    """Unsere IDs sind uuid4().hex — Qdrant erwartet kanonische UUID-Strings."""
    return str(UUID(hex=hex_id))


class QdrantVectorStore:
    def __init__(self, url: str, collection_prefix: str = "aios") -> None:
        # ":memory:" startet eine In-Process-Instanz — ideal für Tests ohne Server
        if url == ":memory:":
            self._client = QdrantClient(location=":memory:")
        else:
            self._client = QdrantClient(url=url)
        self._chunks_collection = f"{collection_prefix}_chunks"
        self._documents_collection = f"{collection_prefix}_documents"

    def _ensure_collections(self, vector_size: int) -> None:
        if not self._client.collection_exists(self._chunks_collection):
            self._client.create_collection(
                self._chunks_collection,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
        if not self._client.collection_exists(self._documents_collection):
            self._client.create_collection(
                self._documents_collection,
                vectors_config=VectorParams(size=1, distance=Distance.COSINE),
            )

    def add_document(self, meta: DocumentMeta, chunks: list[ChunkRecord]) -> None:
        if not chunks:
            return
        self._ensure_collections(vector_size=len(chunks[0].embedding))
        self._client.upsert(
            self._documents_collection,
            points=[
                PointStruct(
                    id=_point_id(meta.id),
                    vector=[0.0],
                    payload=meta.model_dump(mode="json"),
                )
            ],
        )
        self._client.upsert(
            self._chunks_collection,
            points=[
                PointStruct(
                    id=_point_id(chunk.id),
                    vector=chunk.embedding,
                    payload={
                        "document_id": chunk.document_id,
                        "index": chunk.index,
                        "text": chunk.text,
                    },
                )
                for chunk in chunks
            ],
        )

    def list_documents(self) -> list[DocumentMeta]:
        if not self._client.collection_exists(self._documents_collection):
            return []
        points, _ = self._client.scroll(
            self._documents_collection, limit=1_000, with_payload=True
        )
        return [DocumentMeta.model_validate(point.payload) for point in points]

    def get_document(self, document_id: str) -> DocumentMeta | None:
        if not self._client.collection_exists(self._documents_collection):
            return None
        points = self._client.retrieve(
            self._documents_collection, ids=[_point_id(document_id)], with_payload=True
        )
        if not points:
            return None
        return DocumentMeta.model_validate(points[0].payload)

    def search(
        self, query_embedding: list[float], top_k: int = 4
    ) -> list[tuple[ChunkRecord, float]]:
        if not self._client.collection_exists(self._chunks_collection):
            return []
        hits = self._client.query_points(
            self._chunks_collection,
            query=query_embedding,
            limit=top_k,
            with_payload=True,
        ).points
        results: list[tuple[ChunkRecord, float]] = []
        for hit in hits:
            payload: dict[str, Any] = hit.payload or {}
            chunk = ChunkRecord(
                id=UUID(str(hit.id)).hex,
                document_id=str(payload.get("document_id", "")),
                index=int(payload.get("index", 0)),
                text=str(payload.get("text", "")),
                embedding=[],
            )
            results.append((chunk, float(hit.score)))
        return results
