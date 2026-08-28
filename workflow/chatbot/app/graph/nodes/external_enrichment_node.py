from __future__ import annotations

import asyncio
import re
import unicodedata
from typing import Any

from app.graph.state import ChatState
from app.mcp_clients import open_library_client

_MAX_CANDIDATES = 5
_MAX_OL_SUGGESTIONS = 3


def _normalize(text: str) -> str:
    """Normaliza un texto para comparación (case/acento-insensible, ADR-020)."""
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value).strip().lower()


def _title_matches(candidate_title: str, ol_title: str) -> bool:
    candidate = _normalize(candidate_title)
    found = _normalize(ol_title)
    if not candidate or not found:
        return False
    return candidate in found or found in candidate


async def _verify_candidate(rec: dict[str, Any]) -> dict[str, Any]:
    """Verifica un candidato local contra Open Library (ISBN → título+autor).

    Flags por ítem (nunca rompen ante fallo individual):
    - ``open_library_verified``: True / False / None (no se pudo verificar).
    - ``open_library_key``: clave OLID cuando se encuentra en Open Library.
    - ``source``: ``"catalog"`` (origen local).
    """
    item = {**rec, "source": "catalog"}
    isbn = (rec.get("isbn") or "").strip()
    title = rec.get("title") or ""
    author = rec.get("author") or ""

    if isbn:
        try:
            result = await open_library_client.verify_by_isbn(isbn)
            if isinstance(result, dict) and result.get("found"):
                item["open_library_verified"] = True
                item["open_library_key"] = result.get("open_library_key")
                return item
            item["open_library_verified"] = False
            return item
        except Exception:
            item["open_library_verified"] = None
            return item

    # Sin ISBN: búsqueda por título + autor y comparación normalizada.
    try:
        query = f'"{title}" {author}'.strip()
        results = await open_library_client.search_books(query, limit=1)
        best = results[0] if isinstance(results, list) and results else None
        if best is None:
            item["open_library_verified"] = False
            return item
        ol_title = best.get("title") or ""
        if _title_matches(title, ol_title):
            item["open_library_verified"] = True
            item["open_library_key"] = best.get("key")
        else:
            item["open_library_verified"] = False
        return item
    except Exception:
        item["open_library_verified"] = None
        return item


async def _external_suggestions(state: ChatState) -> list[dict[str, Any]]:
    """Genera hasta 3 sugerencias de Open Library cuando no hay candidatos locales.

    Devuelve ítems con ``source="open_library"`` y ``availableCopies=0`` para
    que el frontend las marque como «Open Library · solicitable».
    """
    genre = ""
    for pref in state.preferences or []:
        candidate = (pref.get("genre") or "").strip()
        if candidate:
            genre = candidate
            break
    query = genre or (state.query or "").strip() or (state.message or "").strip()
    if not query:
        return []
    try:
        results = await open_library_client.search_books(query, limit=_MAX_OL_SUGGESTIONS)
        if not isinstance(results, list):
            return []
        suggestions = []
        for result in results[: _MAX_OL_SUGGESTIONS]:
            title = (result.get("title") or "").strip()
            if not title:
                continue
            suggestions.append(
                {
                    "title": title,
                    "author": result.get("author"),
                    "genre": genre,
                    "isbn": result.get("isbn"),
                    "open_library_key": result.get("key"),
                    "available_copies": 0,
                    "source": "open_library",
                    "open_library_verified": True,
                    "reason": "Verificado en Open Library · copia solicitable",
                }
            )
        return suggestions
    except Exception:
        return []


async def external_enrichment_node(state: ChatState) -> ChatState:
    """Enriquece un libro ausente o valida las recomendaciones con Open Library.

    - ``book_query``: comportamiento original — enriquece el libro buscado con
      metadatos de Open Library sin colapsar si el MCP falla (Bug 2).
    - ``recommendation`` (US-019): cruza los candidatos locales con Open Library
      (ISBN → título+autor, paralelizada con ``asyncio.gather``, tope 5) y marca
      cada ítem con ``open_library_verified``/``open_library_key``/``source``.
      Si no hay candidatos locales, propone hasta 3 títulos de Open Library
      marcados como ``source="open_library"`` (solicitables).
    """
    if state.intent == "book_query":
        # comportamiento original: si el libro no está en catálogo, enriquece
        # con Open Library por query para poder ofrecer una copia.
        if state.catalog_matches:
            return state
        try:
            results = await open_library_client.search_books(
                state.query or state.message, limit=3
            )
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

    if state.intent != "recommendation":
        return state

    # ---- US-019: validación cruzada de recomendaciones con Open Library ----
    state.enrichment = None
    state.enrichment_error = False

    if state.recommendations:
        candidates = state.recommendations[:_MAX_CANDIDATES]
        verified = await asyncio.gather(
            *(_verify_candidate(rec) for rec in candidates), return_exceptions=True
        )
        enriched: list[dict[str, Any]] = []
        for rec, outcome in zip(candidates, verified):
            if isinstance(outcome, Exception):
                enriched.append({**rec, "source": "catalog", "open_library_verified": None})
            else:
                enriched.append(outcome)
        state.recommendations = enriched
        return state

    # Sin candidatos locales → sugerencias de Open Library solicitables.
    suggestions = await _external_suggestions(state)
    if suggestions:
        state.recommendations = suggestions
    return state
