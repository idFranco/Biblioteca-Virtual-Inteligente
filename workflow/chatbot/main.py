from __future__ import annotations

import os
import uuid

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.graph.build_graph import graph
from app.graph.state import ChatState
from app.schemas import BookRecommendation, ChatRequest, ChatResponse


def _cors_origins() -> list[str]:
    """Origen(es) CORS permitidos desde la variable CORS_ORIGINS (fail-fast).

    Se espera una lista separada por comas; cada origen se recorta y se
    descartan entradas vacías. Sin orígenes, el arranque falla con un error
    claro (ADR-025).
    """
    raw = os.getenv("CORS_ORIGINS", "")
    origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
    if not origins:
        raise RuntimeError(
            "Falta la variable de entorno 'CORS_ORIGINS' (origen(es) permitidos "
            "separados por coma, p. ej. http://localhost:5173)."
        )
    return origins


app = FastAPI(title="Biblioteca Virtual Chatbot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "X-Correlation-ID"],
    allow_credentials=False,
)


def normalize_state(raw: dict) -> ChatState:
    """Convierte el dict devuelto por LangGraph en un ChatState tipado."""
    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


def _recommendations(result: ChatState) -> list[BookRecommendation]:
    """Convierte las recomendaciones del estado en el schema de respuesta."""
    recommendations = []
    for item in result.recommendations or []:
        available_copies = int(item.get("available_copies") or 0)
        recommendations.append(
            BookRecommendation(
                id=item.get("id"),
                title=item.get("title") or "Sin título",
                author=item.get("author"),
                genre=item.get("genre"),
                isbn=item.get("isbn"),
                openLibraryKey=item.get("open_library_key") or item.get("key"),
                availableCopies=available_copies,
                available=available_copies > 0,
                reason=item.get("reason"),
                source=item.get("source"),
                openLibraryVerified=item.get("open_library_verified"),
            )
        )
    return recommendations


def _correlation_id(header: str | None) -> str:
    return header or f"chat-{uuid.uuid4()}"


def _conversation_id(requested: str | None) -> str:
    """Devuelve un conversationId válido (<=64) o genera uno nuevo.

    Si el cliente envió uno (persistido en sessionStorage), se reutiliza para
    conservar la memoria conversacional entre turnos. Si es inválido o está
    vacío, se genera uno nuevo.
    """
    if requested and len(requested) <= 64 and requested.strip():
        return requested.strip()
    return f"conv-{uuid.uuid4()}"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/chat")
async def chat(
    request: ChatRequest,
    x_correlation_id: str | None = Header(default=None, alias="X-Correlation-ID"),
) -> ChatResponse:
    """Procesa un mensaje a través del grafo LangGraph auditado."""
    correlation_id = _correlation_id(x_correlation_id)
    conversation_id = _conversation_id(request.conversationId)
    # Se pasa un dict SIN la clave "history": así LangGraph conserva el historial
    # almacenado en el checkpointer (mismo thread_id) y no lo reinicia a [] en
    # cada turno. El primer turno arranca con el historial vacío del esquema.
    initial_state = {
        "message": request.message,
        "user_id": request.userId,
        "correlation_id": correlation_id,
        "conversation_id": conversation_id,
    }

    try:
        raw = await graph.ainvoke(
            initial_state, config={"configurable": {"thread_id": conversation_id}}
        )
        result = normalize_state(raw)
    except Exception:
        raise HTTPException(status_code=503, detail="El asistente no está disponible en este momento.")

    return ChatResponse(
        message=result.response or "Lo siento, no pude generar una respuesta.",
        action_offer=result.action_offer,
        recommendations=_recommendations(result),
        correlation_id=correlation_id,
        conversation_id=conversation_id,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
