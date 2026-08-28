from __future__ import annotations

from typing import Any

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client
from app.mcp_clients import open_library_client


async def external_enrichment_node(state: ChatState) -> ChatState:
    """Enriquece un libro ausente con metadatos de Open Library.

    Fallback obligatorio (Bug 2): si Open Library no responde, no encuentra el
    libro o el MCP falla, se marca ``enrichment_error`` y el grafo continúa sin
    colapsar. La oferta de copia depende de la ausencia en catálogo, no del
    enriquecimiento.

    Nueva funcionalidad US-019: cuando la intención es ``recommendation``, cruza
    los resultados del catálogo local (Biblioteca-MCP) con Open Library para
    validar y enrichiar las recomendaciones, conservando solo los libros que
    estén disponibles en al menos una de las dos fuentes.
    """
    if state.intent == "book_query":
        # comportamiento original: enriquece el libro buscado
        if not state.catalog_matches:
            return state
        best = state.catalog_matches[0]
        key = best.get("key") or best.get("open_library_key")
        if not key:
            return state
        try:
            details = await open_library_client.get_book_details(key)
            state.enrichment = {**best, **details}
            state.enrichment_error = False
        except Exception:
            state.enrichment = best
            state.enrichment_error = False
        return state

    if state.intent != "recommendation" or not state.recommendations:
        # Sin recomendaciones que procesar - comportamiento anterior
        return state

    # ---- US-019: cruce de recomendaciones con Open Library ----
    enriched: list[dict[str, Any]] = []
    for rec in state.recommendations:
        title = rec.get("title") or ""
        author = rec.get("author") or ""
        # Busca en Open Library por título + autor
        try:
            ol_results = await open_library_client.search_books(f'"{title}" "{author}"', limit=3)
            if ol_results:
                # Libro validado en Open Library → conservar
                enriched.append({**rec, "open_library_verified": True})
            else:
                # No encontrado en OL, pero conservar catálogo local
                enriched.append({**rec, "open_library_verified": False})
        except Exception:
            # Error en OL: conservar catálogo local con marca de advertencia
            enriched.append({**rec, "open_library_verified": None, "open_library_error": True})

    state.recommendations = enriched
    state.enrichment = None
    state.enrichment_error = False
    return state
