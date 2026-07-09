from pydantic import BaseModel, Field


class RagQuery(BaseModel):
    question: str = Field(min_length=1, max_length=8_000)
    top_k: int = Field(default=4, ge=1, le=20)


class RetrievedChunk(BaseModel):
    document_id: str
    filename: str
    chunk_index: int
    text: str
    score: float


class RagAnswer(BaseModel):
    answer: str
    model: str
    sources: list[RetrievedChunk]
