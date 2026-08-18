from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    userId: str | None = Field(default=None, max_length=64)


class BookRequestMetadata(BaseModel):
    type: Literal["book_request"] = "book_request"
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    genre: str | None = None
    description: str | None = None
    openLibraryKey: str | None = None


class BookRecommendation(BaseModel):
    id: str | None = None
    title: str
    author: str | None = None
    genre: str | None = None
    isbn: str | None = None
    openLibraryKey: str | None = None
    coverUrl: str | None = None
    availableCopies: int = 0
    available: bool = False
    reason: str | None = None


class ChatResponse(BaseModel):
    message: str
    action_offer: BookRequestMetadata | None = None
    recommendations: list[BookRecommendation] = Field(default_factory=list)
    correlation_id: str | None = None
