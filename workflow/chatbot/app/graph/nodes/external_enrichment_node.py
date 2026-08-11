from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import open_library_client


async def external_enrichment_node(state: ChatState) -> ChatState:
    """Enriquece un libro ausente con metadatos de Open Library.

    Fallback obligatorio (Bug 2): si Open Library no responde, no encuentra el
    libro o el MCP falla, se marca ``enrichment_error`` y el grafo continúa sin
    colapsar. La oferta de copia depende de la ausencia en catálogo, no del
    enriquecimiento.
    """
    if state.intent != "book_query" or state.catalog_matches:
        return state

    try:
        results = await open_library_client.search_books(state.query or state.message, limit=3)
    except Exception:
        state.enrichment = None
        state.enrichment_error = True
        return state

    if not results:
        state.enrichment = None
        state.enrichment_error = True
        return state

    best = results[0]
    key = best.get("key")
    try:
        if key:
            details = await open_library_client.get_book_details(key)
            best = {**best, **details}
        state.enrichment = best
        state.enrichment_error = False
    except Exception:
        state.enrichment = best
        state.enrichment_error = False
    return state
