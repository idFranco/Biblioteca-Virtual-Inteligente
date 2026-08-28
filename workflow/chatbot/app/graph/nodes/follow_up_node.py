from __future__ import annotations

import re
import unicodedata
from typing import Any

from app.graph.state import ChatState
from app.mcp_clients import open_library_client

_ORDINALS = {
    "primera": 0,
    "primero": 0,
    "segunda": 1,
    "segundo": 1,
    "tercera": 2,
    "tercero": 2,
    "cuarta": 3,
    "cuarto": 3,
    "quinta": 4,
    "quinto": 4,
}
_LAST_ORDINALS = ("última", "ultima", "último", "ultimo")
_ORDINAL_PATTERN = re.compile(
    r"\b(prim[eé]r[oa]|segund[oa]|tercer[oa]|cuart[oa]|quint[oa]|"
    r"[uú]ltim[oa]|siguiente)\b",
    re.IGNORECASE,
)
_QUOTED_TITLE_PATTERN = re.compile(r"[¿?]*(?:\"|«)(.+?)(?:\"|»)", re.IGNORECASE)


def _normalize(text: str) -> str:
    """Normaliza un texto para comparación (case/acento-insensible, ADR-020)."""
    value = unicodedata.normalize("NFKD", text or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value).strip().lower()


def _last_recommendations(state: ChatState) -> list[dict[str, Any]]:
    """Devuelve las recomendaciones de la respuesta previa del asistente.

    Los turnos ``record_turn`` incrustan la lista compacta de libros
    recomendados en la entrada de historial del asistente bajo ``recommendations``.
    """
    for entry in reversed(list(state.history or [])):
        recs = entry.get("recommendations")
        if isinstance(recs, list) and recs:
            return recs
    return []


def _find_by_title(message: str, items: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Localiza por título literal cuando el mensaje cita «algo» entre comillas."""
    quoted = _QUOTED_TITLE_PATTERN.search(message)
    if not quoted:
        return None
    target = _normalize(quoted.group(1))
    for item in items:
        normalized = _normalize(item.get("title") or "")
        if normalized and (target in normalized or normalized in target):
            return item
    return None


def _resolve_index(message: str, items: list[dict[str, Any]]) -> int:
    """Resuelve el selector ordinal («la primera», «la segunda»…) a un índice."""
    match = _ORDINAL_PATTERN.search(message)
    if not match:
        return 0
    key = match.group(1).lower()
    last = max(0, len(items) - 1)
    if key in _LAST_ORDINALS:
        return last
    if key == "siguiente":
        return 0
    return min(_ORDINALS.get(key, 0), last)


def _detail_text(item: dict[str, Any]) -> str:
    """Compone la respuesta heurística sobre un libro ya recomendado."""
    title = item.get("title") or "ese libro"
    author = item.get("author")
    genre = item.get("genre")
    reason = item.get("reason")
    source = item.get("source")
    description = item.get("description")
    available = int(item.get("available_copies") or 0) > 0

    detail = f"«{title}»" + (f" de {author}" if author else "") + "."
    if genre:
        detail += f" Es una obra de {genre}."
    if source == "open_library":
        detail += " No está en nuestro catálogo, pero puedes solicitar una copia."
    elif available:
        detail += " Está disponible en nuestro catálogo."
    else:
        detail += " Está en nuestro catálogo, aunque hoy no hay copias disponibles para alquilar."
    if reason:
        detail += f" {reason}"
    if isinstance(description, str) and description.strip():
        detail += f"\n{description.strip()}"
    return detail


def _no_recommendations() -> str:
    return (
        "Aún no tengo una recomendación previa para ampliarte. "
        "Pídeme recomendaciones con «recomiéndame un libro de…» y después "
        "podrás preguntarme por «la primera», «la segunda»… o por el título."
    )


async def _enrich_details(item: dict[str, Any]) -> dict[str, Any]:
    """Adjunta la descripción de Open Library si el libro tiene clave OLID.

    Un fallo del MCP no colapsa: devuelve el ítem original sin descripción.
    """
    key = (item.get("open_library_key") or item.get("key") or "").strip()
    if not key:
        return item
    try:
        details = await open_library_client.get_book_details(key)
        if isinstance(details, dict):
            merged = {**item}
            if isinstance(details.get("description"), str) and details.get("description").strip():
                merged["description"] = details.get("description").strip()
            return merged
    except Exception:
        pass
    return item


async def follow_up_node(state: ChatState) -> ChatState:
    """Responde a preguntas sobre una recomendación previa (US-019 AC#4).

    Busca la última respuesta del asistente que contenga una lista de libros
    recomendados (incrustada por ``record_turn_node``), resuelve el selector
    («la primera», «la segunda», … o el título citado) y compone una respuesta
    con los detalles del libro elegido. Enriquece con la descripción de Open
    Library cuando hay clave OLID. Sin recomendaciones previas, orienta al
    usuario sin colapsar.
    """
    state.recommendations = []
    candidates = _last_recommendations(state)
    message = state.message or ""

    item = _find_by_title(message, candidates)
    if item is None and candidates:
        item = candidates[_resolve_index(message, candidates)]

    if item is not None:
        item = await _enrich_details(item)
        state.recommendations = [item]
        state.response = _detail_text(item)
        return state

    state.response = _no_recommendations()
    return state
