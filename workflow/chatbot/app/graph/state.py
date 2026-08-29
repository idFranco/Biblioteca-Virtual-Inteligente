"""Estado tipado del grafo LangGraph del chatbot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.schemas import BookRequestMetadata


@dataclass
class ChatState:
    message: str
    user_id: str | None = None
    correlation_id: str | None = None
    intent: str | None = None
    query: str | None = None
    reading_state: str | None = None
    catalog_matches: list[dict[str, Any]] = field(default_factory=list)
    preferences: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[dict[str, Any]] = field(default_factory=list)
    enrichment: dict[str, Any] | None = None
    enrichment_error: bool = False
    action_offer: BookRequestMetadata | None = None
    due_reminder_flag: bool = False
    feedback_payload: dict[str, Any] | None = None
    blocked: bool = False
    sanitized: bool = False
    llm_used: bool = False
    response: str | None = None
    llm_messages: list[dict[str, str]] = field(default_factory=list)
    conversation_id: str | None = None
    history: list[dict[str, Any]] = field(default_factory=list)
