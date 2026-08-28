from __future__ import annotations

import re

from app.graph.state import ChatState

_STATUS_PATTERNS = re.compile(
    r"mis alquileres|cu[aá]nto.*debo|mi pr[eé]stamo|estado de lectura|alquiler",
    re.IGNORECASE,
)
_RECOMMENDATION_PATTERNS = re.compile(
    r"recomi[eé]ndame|qu[eé] me recomiendas|qu[eé] leer|sugiere|recomendaci[oó]n",
    re.IGNORECASE,
)
_FEEDBACK_PATTERNS = re.compile(
    r"me gust[oó]|me encant[oó]|no me gust[oó]|no me encant[oó]|recomendad[oa]|excelente|muy buen|mal[oa] recomendaci[oó]n",
    re.IGNORECASE,
)
_SMALLTALK_PATTERNS = re.compile(
    r"^\s*[¿¡]?(hola|buenas|buen[oa]s? d[ií]as|buen[oa]s? tardes|buen[oa]s? noches|qu[eé] tal|"
    r"c[oó]mo est[aaá]s|qu[eé] haces|gracias|muchas gracias|adi[oó]s|chao|bye|"
    r"quien eres|qui[eén] eres|qu[eé] puedes hacer|ay[uú]dame)",
    re.IGNORECASE,
)


def _looks_like_book_query(message: str) -> bool:
    return bool(
        re.search(r"¿?tienen|tienen |busc[oa] |hay alg[úu]n |t[eé]n[eé]s |existe ", message, re.IGNORECASE)
        or re.search(r"[¿?]*(?:\"|«).+?(?:\"|»)", message)
    )


async def classify_intent_node(state: ChatState) -> ChatState:
    """Clasifica la intención del mensaje con heurísticas ligeras.

    Orden de evaluación: status, recommendation, feedback, smalltalk y
    book_query. Los patrones de smalltalk se evalúan ANTES del catch-all, de
    modo que un saludo («hola», «buenas tardes») no se convierte en una
    búsqueda en catálogo.
    """
    message = state.message
    if _STATUS_PATTERNS.search(message):
        state.intent = "status"
    elif _RECOMMENDATION_PATTERNS.search(message):
        state.intent = "recommendation"
    elif _FEEDBACK_PATTERNS.search(message):
        state.intent = "feedback"
    elif _SMALLTALK_PATTERNS.search(message):
        state.intent = "other"
    elif _looks_like_book_query(message) or len(message.strip()) > 0:
        state.intent = "book_query"
    else:
        state.intent = "other"
    return state
