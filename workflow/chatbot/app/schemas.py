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


class ChatResponse(BaseModel):
    message: str
    action_offer: BookRequestMetadata | None = None
    correlation_id: str | None = None
