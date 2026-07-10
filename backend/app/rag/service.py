"""RAG-Service: Ingestion (Parse → Chunk → Embed → Store) und Query (Retrieve → Generate)."""

from app.models.documents import ChunkRecord, DocumentMeta
from app.models.rag import RagAnswer, RetrievedChunk
from app.rag.chunker import chunk_text
from app.rag.parser import parse_bytes
from app.rag.vector_store import VectorStore
from app.services.llm_service import LLMClient

RAG_SYSTEM_PROMPT = (
    "Du bist der Wissens-Assistent des AI-OS. Beantworte die Frage ausschließlich "
    "auf Basis des bereitgestellten Kontexts. Wenn der Kontext die Antwort nicht "
    "enthält, sage das ehrlich. Antworte auf Deutsch."
)


class RagService:
    def __init__(
        self,
        llm: LLMClient,
        store: VectorStore,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> None:
        self._llm = llm
        self._store = store
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap

    async def ingest(self, filename: str, data: bytes, media_type: str) -> DocumentMeta:
        text = parse_bytes(filename, data)
        pieces = chunk_text(text, self._chunk_size, self._chunk_overlap)
        if not pieces:
            raise ValueError(f"Kein Text extrahierbar aus {filename}")

        embeddings = await self._llm.embed(pieces)
        meta = DocumentMeta(filename=filename, media_type=media_type, num_chunks=len(pieces))
        chunks = [
            ChunkRecord(document_id=meta.id, index=i, text=piece, embedding=vector)
            for i, (piece, vector) in enumerate(zip(pieces, embeddings, strict=True))
        ]
        self._store.add_document(meta, chunks)
        return meta

    async def query(self, question: str, top_k: int = 4) -> RagAnswer:
        query_embedding = (await self._llm.embed([question]))[0]
        results = self._store.search(query_embedding, top_k)

        sources = []
        for chunk, score in results:
            doc = self._store.get_document(chunk.document_id)
            sources.append(
                RetrievedChunk(
                    document_id=chunk.document_id,
                    filename=doc.filename if doc else "?",
                    chunk_index=chunk.index,
                    text=chunk.text,
                    score=round(score, 4),
                )
            )

        context = "\n\n---\n\n".join(
            f"[{source.filename} / Chunk {source.chunk_index}]\n{source.text}" for source in sources
        )
        prompt = f"Kontext:\n{context}\n\nFrage: {question}"
        answer = await self._llm.chat(prompt, system=RAG_SYSTEM_PROMPT)
        return RagAnswer(answer=answer, model=self._llm.chat_model, sources=sources)

    def list_documents(self) -> list[DocumentMeta]:
        return self._store.list_documents()
