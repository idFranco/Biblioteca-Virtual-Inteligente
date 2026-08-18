from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def internal_catalog_node(state: ChatState) -> ChatState:
    """Consulta el catálogo interno vía Biblioteca-MCP.

    - book_query: busca libros por título/autor (catalog_matches).
    - recommendation: obtiene recomendaciones por género/historial (recommendations).
    """
    if state.intent == "recommendation" and state.user_id:
        try:
            recommendations = await biblioteca_client.listar_recomendaciones_por_genero(
                state.user_id, limit=5
            )
            state.recommendations = recommendations[:5]
        except Exception:
            state.recommendations = []
        return state

    if state.intent != "book_query":
        return state

    try:
        matches = await biblioteca_client.buscar_libros(state.query or state.message, limit=10)
        state.catalog_matches = matches[:10]
    except Exception:
        state.catalog_matches = []
    return state
