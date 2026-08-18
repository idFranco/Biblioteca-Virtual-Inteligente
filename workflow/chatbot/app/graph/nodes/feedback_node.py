from __future__ import annotations

import re

from app.graph.state import ChatState
from app.graph.nodes.extract_query_node import _extract_query

_LIKE_PATTERN = re.compile(
    r"me gust[oó]|me encant[oó]|recomendad[oa]|excelente|muy buen|gracias.*recomend",
    re.IGNORECASE,
)
_DISLIKE_PATTERN = re.compile(
    r"no me gust[oó]|no me encant[oó]|mal[oa] recomendaci[oó]n|no era lo que esperaba",
    re.IGNORECASE,
)


async def feedback_node(state: ChatState) -> ChatState:
    """Detecta la valoración del usuario sobre una recomendación.

    Extrae el libro referenciado y una valoración binaria (me gustó / no me
    gustó) en ``feedback_payload`` para que save_feedback_node la persista.
    """
    message = state.message

    if _DISLIKE_PATTERN.search(message):
        rating = 1
    elif _LIKE_PATTERN.search(message):
        rating = 5
    else:
        rating = 4

    book_query = _extract_query(message)
    state.feedback_payload = {
        "book_query": book_query or None,
        "rating": rating,
        "comment": message,
    }
    return state
