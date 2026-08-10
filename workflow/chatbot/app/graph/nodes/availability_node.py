from __future__ import annotations

from app.graph.state import ChatState
from app.schemas import BookRequestMetadata


def _open_library_key(key: str | None) -> str | None:
    if not key:
        return None
    return key if key.startswith("/") else f"/{key}"


def _offer_from_enrichment(state: ChatState) -> BookRequestMetadata | None:
    enrichment = state.enrichment or {}
    title = enrichment.get("title")
    author = enrichment.get("author")
    if not title or not author:
        return None
    return BookRequestMetadata(
        title=title,
        author=author,
        isbn=enrichment.get("isbn"),
        genre=enrichment.get("genre"),
        description=enrichment.get("description"),
        openLibraryKey=_open_library_key(enrichment.get("key")),
    )


async def availability_node(state: ChatState) -> ChatState:
    """Compone la oferta de solicitud de copia para un libro ausente del catálogo.

    La oferta se genera cuando el libro no existe internamente. El enriquecimiento
    fallido (Bug 2) se mantiene como oferta con los datos mínimos disponibles o, si
    no hay datos, no se muestra la acción para no crear solicitudes incompletas.
    """
    if state.intent != "book_query" or state.catalog_matches:
        return state

    state.action_offer = _offer_from_enrichment(state)
    return state
