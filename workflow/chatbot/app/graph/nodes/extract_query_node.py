from __future__ import annotations

import re

from app.graph.state import ChatState

_QUOTED = re.compile(r"“(?P<q1>.+?)”|«(?P<q2>.+?)»|\"(?P<q3>.+?)\"", re.UNICODE)

_PREFIXES = [
    "estoy buscando el libro",
    "estoy buscando un libro",
    "estoy buscando",
    "necesito conseguir",
    "necesito el libro",
    "necesito un libro",
    "necesito",
    "me gustaría",
    "busco el libro",
    "busco un libro",
    "busco",
    "quiero el libro",
    "quiero un libro",
    "quiero",
    "dónde está",
    "donde esta",
    "tienen el libro",
    "tienen un libro",
    "tienen",
    "tienes",
    "hay algún libro",
    "hay alguna obra",
    "hay algún",
    "hay alguna",
    "existe el libro",
    "existe",
    "un libro de",
    "el libro de",
    "de la",
    "de los",
    "de las",
    "del",
    "de",
]

_STRIP_CHARS = " \t¿?¡!“”«»…,\"'"


def _extract_query(message: str) -> str:
    """Extrae el término de búsqueda (título/autor) de un mensaje natural."""
    match = _QUOTED.search(message)
    if match:
        quoted = next((g for g in match.groups() if g), None)
        if quoted:
            return quoted.strip().strip(_STRIP_CHARS)

    text = message.strip().strip(_STRIP_CHARS)
    changed = True
    while changed:
        changed = False
        lower = text.lower()
        for prefix in _PREFIXES:
            if lower.startswith(prefix):
                text = text[len(prefix):].strip(_STRIP_CHARS)
                changed = True
                break
    return text or message.strip()


async def extract_query_node(state: ChatState) -> ChatState:
    """Extrae el título o autor buscado del mensaje sin LLM (heurística ligera)."""
    state.query = _extract_query(state.message)
    return state
