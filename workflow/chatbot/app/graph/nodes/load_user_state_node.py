from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def load_user_state_node(state: ChatState) -> ChatState:
    """Carga el estado de lectura del usuario desde Biblioteca-MCP (solo lectura).

    Un fallo del MCP no colapsa el grafo: se deja el estado sin cargar.
    """
    if not state.user_id:
        return state
    try:
        state.reading_state = await biblioteca_client.get_estado_lectura(state.user_id)
    except Exception:
        state.reading_state = None
    return state
