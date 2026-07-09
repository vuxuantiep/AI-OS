"""Absatz-bewusstes Chunking mit Überlappung."""


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Teilt Text in Chunks von ~chunk_size Zeichen mit overlap Zeichen Überlappung.

    Absätze werden möglichst zusammengehalten; erst wenn ein Absatz selbst
    zu groß ist, wird hart per Sliding Window geschnitten.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size muss > 0 sein")
    if overlap >= chunk_size:
        raise ValueError("overlap muss kleiner als chunk_size sein")

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    def flush() -> None:
        nonlocal current
        if current.strip():
            chunks.append(current.strip())
        current = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            flush()
            step = chunk_size - overlap
            for start in range(0, len(paragraph), step):
                piece = paragraph[start : start + chunk_size].strip()
                if piece:
                    chunks.append(piece)
                if start + chunk_size >= len(paragraph):
                    break
        elif len(current) + len(paragraph) + 2 > chunk_size:
            flush()
            current = paragraph
        else:
            current = f"{current}\n\n{paragraph}" if current else paragraph

    flush()
    return chunks
