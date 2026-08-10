from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def load_user_state_node(state: ChatState) -> ChatState:
    """Carga el estado de lectura del usuario desde Biblioteca-MCP (solo lectura)."""
    if not state.user_id:
        return state
    state.reading_state = await biblioteca_client.get_estado_lectura(state.user_id)
    return state
