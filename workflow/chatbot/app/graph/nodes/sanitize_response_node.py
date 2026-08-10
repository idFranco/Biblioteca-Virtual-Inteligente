from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import security_audit_client


async def sanitize_response_node(state: ChatState) -> ChatState:
    """Sanitiza la respuesta cuando la auditoría de salida la marcó insegura."""
    if not state.response:
        return state
    try:
        state.response = await security_audit_client.sanitize_text(state.response)
        state.sanitized = False
    except Exception:
        state.response = "Lo siento, no puedo responder a esa petición en este momento."
        state.sanitized = False
    return state
