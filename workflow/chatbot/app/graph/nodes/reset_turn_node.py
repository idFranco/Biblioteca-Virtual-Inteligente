from __future__ import annotations

from app.graph.state import ChatState

_HISTORY_WINDOW = 12

# Campos transitorios del turno anterior que nunca deben contaminar el turno
# actual (el checkpointer de LangGraph fusiona el estado entre invocaciones).
_TRANSIENT_FIELDS = (
    "intent",
    "query",
    "catalog_matches",
    "recommendations",
    "enrichment",
    "enrichment_error",
    "action_offer",
    "due_reminder_flag",
    "feedback_payload",
    "blocked",
    "sanitized",
    "llm_used",
    "response",
    "llm_messages",
)


def _reset_transient(state: ChatState) -> None:
    for field in _TRANSIENT_FIELDS:
        if field in state.__dataclass_fields__:
            if field in ("catalog_matches", "recommendations", "llm_messages"):
                setattr(state, field, [])
            else:
                setattr(state, field, None if field != "enrichment_error" else False)


def _append_user_message(state: ChatState) -> None:
    history = list(state.history or [])
    history.append({"role": "user", "content": state.message})
    state.history = history[-_HISTORY_WINDOW:]


async def reset_turn_node(state: ChatState) -> ChatState:
    """Primer nodo del grafo: prepara el estado para un turno nuevo.

    Limpia todos los campos transitorios del turno anterior (heredados por el
    checkpointer) y registra el mensaje del usuario en la ventana de historial
    conversacional, podada a las últimas ``_HISTORY_WINDOW`` entradas.
    """
    _reset_transient(state)
    _append_user_message(state)
    return state
