from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=32_000)
    model: str | None = None
    system: str | None = None


class ChatResponse(BaseModel):
    answer: str
    model: str
