from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def preferences_node(state: ChatState) -> ChatState:
    """Carga las preferencias de género del usuario vía Biblioteca-MCP.

    Un fallo del MCP no colapsa el grafo: deja las preferencias vacías.
    """
    if not state.user_id:
        state.preferences = []
        return state
    try:
        state.preferences = await biblioteca_client.obtener_preferencias(state.user_id)
    except Exception:
        state.preferences = []
    return state
