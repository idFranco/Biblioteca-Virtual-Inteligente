from __future__ import annotations

import re

from app.graph.state import ChatState

_STATUS_PATTERNS = re.compile(
    r"mis alquileres|cu[aá]nto.*debo|mi pr[eé]stamo|estado de lectura|alquiler",
    re.IGNORECASE,
)
_RECOMMENDATION_PATTERNS = re.compile(
    r"recomi[eé]ndame|qu[eé] me recomiendas|qu[eé] leer|sugiere",
    re.IGNORECASE,
)


def _looks_like_book_query(message: str) -> bool:
    return bool(
        re.search(r"¿?tienen|tienen |busc[oa] |hay alg[úu]n |t[eé]n[eé]s |existe ", message, re.IGNORECASE)
        or re.search(r"[¿?]*(?:\"|«).+?(?:\"|»)", message)
    )


async def classify_intent_node(state: ChatState) -> ChatState:
    """Clasifica la intención del mensaje con heurísticas ligeras.

    Sin dependencia del LLM para el flujo mínimo: si la heurística no decide,
    se trata como book_query para habilitar la búsqueda en catálogo.
    """
    message = state.message
    if _STATUS_PATTERNS.search(message):
        state.intent = "status"
    elif _RECOMMENDATION_PATTERNS.search(message):
        state.intent = "recommendation"
    elif _looks_like_book_query(message) or len(message.strip()) > 0:
        state.intent = "book_query"
    else:
        state.intent = "other"
    return state
