from __future__ import annotations

from app.graph.state import ChatState

BLOCK_RESPONSE = (
    "Lo siento, no puedo atender esa petición. Si tienes dudas sobre el catálogo "
    "o sobre tus alquileres, estaré encantado de ayudarte."
)


async def block_response_node(state: ChatState) -> ChatState:
    """Devuelve una respuesta segura de bloqueo cuando la entrada es insegura."""
    state.response = BLOCK_RESPONSE
    return state
