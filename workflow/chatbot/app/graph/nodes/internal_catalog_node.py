from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def internal_catalog_node(state: ChatState) -> ChatState:
    """Busca el libro en el catálogo interno de la biblioteca via Biblioteca-MCP."""
    if state.intent != "book_query":
        return state

    try:
        matches = await biblioteca_client.buscar_libros(state.message, limit=10)
        state.catalog_matches = matches[:10]
    except Exception:
        state.catalog_matches = []
    return state
