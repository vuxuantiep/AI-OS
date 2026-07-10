from pathlib import Path

import pytest

from app.models.documents import ChunkRecord, DocumentMeta
from app.rag.qdrant_store import QdrantVectorStore
from app.rag.vector_store import JsonVectorStore, VectorStore, cosine_similarity


def test_cosine_similarity_basics() -> None:
    assert cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert cosine_similarity([], [1.0]) == 0.0
    assert cosine_similarity([1.0, 2.0], [1.0]) == 0.0


@pytest.fixture(params=["json", "qdrant"])
def store(request: pytest.FixtureRequest, tmp_path: Path) -> VectorStore:
    """Beide Implementierungen müssen denselben Vertrag erfüllen."""
    if request.param == "json":
        return JsonVectorStore(tmp_path / "store.json")
    return QdrantVectorStore(":memory:")


def _sample_document(store: VectorStore) -> DocumentMeta:
    doc = DocumentMeta(filename="test.txt", num_chunks=2)
    store.add_document(
        doc,
        [
            ChunkRecord(document_id=doc.id, index=0, text="Katze", embedding=[1.0, 0.0]),
            ChunkRecord(document_id=doc.id, index=1, text="Hund", embedding=[0.0, 1.0]),
        ],
    )
    return doc


def test_add_and_search(store: VectorStore) -> None:
    doc = _sample_document(store)

    results = store.search([1.0, 0.1], top_k=1)
    assert len(results) == 1
    assert results[0][0].text == "Katze"
    assert results[0][0].document_id == doc.id

    assert store.search([0.1, 1.0], top_k=1)[0][0].text == "Hund"


def test_document_metadata(store: VectorStore) -> None:
    doc = _sample_document(store)

    documents = store.list_documents()
    assert len(documents) == 1
    assert documents[0].filename == "test.txt"

    found = store.get_document(doc.id)
    assert found is not None
    assert found.id == doc.id
    assert store.get_document("0" * 32) is None


def test_search_on_empty_store(store: VectorStore) -> None:
    assert store.search([1.0, 0.0], top_k=3) == []


def test_json_persistence(tmp_path: Path) -> None:
    path = tmp_path / "store.json"
    doc = _sample_document(JsonVectorStore(path))

    # Persistenz: neuer Store aus derselben Datei
    reloaded = JsonVectorStore(path)
    assert len(reloaded.list_documents()) == 1
    assert reloaded.get_document(doc.id) is not None
    assert reloaded.search([0.1, 1.0], top_k=1)[0][0].text == "Hund"
