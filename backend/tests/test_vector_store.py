from pathlib import Path

from app.models.documents import ChunkRecord, DocumentMeta
from app.rag.vector_store import JsonVectorStore, cosine_similarity


def test_cosine_similarity_basics() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine_similarity([], [1.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [1.0]) == 0.0


def test_add_search_and_persistence(tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    store = JsonVectorStore(path)

    doc = DocumentMeta(filename="test.txt", num_chunks=2)
    store.add_document(
        doc,
        [
            ChunkRecord(document_id=doc.id, index=0, text="Katze", embedding=[1.0, 0.0]),
            ChunkRecord(document_id=doc.id, index=1, text="Hund", embedding=[0.0, 1.0]),
        ],
    )

    results = store.search([1.0, 0.1], top_k=1)
    assert len(results) == 1
    assert results[0][0].text == "Katze"

    # Persistenz: neuer Store aus derselben Datei
    reloaded = JsonVectorStore(path)
    assert len(reloaded.list_documents()) == 1
    assert reloaded.get_document(doc.id) is not None
    assert reloaded.search([0.1, 1.0], top_k=1)[0][0].text == "Hund"
