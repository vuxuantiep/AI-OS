import pytest

from app.rag.chunker import chunk_text


def test_short_text_single_chunk() -> None:
    assert chunk_text("Hallo Welt", chunk_size=100, overlap=20) == ["Hallo Welt"]


def test_paragraphs_are_grouped() -> None:
    text = "Absatz eins.\n\nAbsatz zwei.\n\nAbsatz drei."
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) == 1
    assert "Absatz eins." in chunks[0]
    assert "Absatz drei." in chunks[0]


def test_long_paragraph_is_split_with_overlap() -> None:
    text = "x" * 1000
    chunks = chunk_text(text, chunk_size=400, overlap=100)
    assert all(len(c) <= 400 for c in chunks)
    assert len(chunks) >= 3
    # Überlappung: Ende von Chunk 1 == Anfang von Chunk 2
    assert chunks[0][-100:] == chunks[1][:100]


def test_empty_text_returns_no_chunks() -> None:
    assert chunk_text("   \n\n  ") == []


def test_invalid_params_raise() -> None:
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=0)
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=100, overlap=100)
