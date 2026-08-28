from __future__ import annotations

from app.graph.state import ChatState

_HISTORY_WINDOW = 12

# Campos compactos que se incrustan en el historial junto con la respuesta del
# asistente (US-019 AC#4): permiten resolver turnos siguientes del tipo
# «cuéntame más sobre la primera» sin reintroducir campos sensibles.
_METADATA_FIELDS = (
    "title",
    "author",
    "genre",
    "isbn",
    "source",
    "open_library_key",
    "open_library_verified",
    "available_copies",
    "reason",
    "description",
)


def _light(rec: dict) -> dict:
    """Compacta una recomendación al subconjunto seguro para el historial."""
    return {key: rec.get(key) for key in _METADATA_FIELDS if rec.get(key) is not None}


async def record_turn_node(state: ChatState) -> ChatState:
    """Último nodo del grafo: cierra el par user/assistant del turno.

    Agrega la respuesta del asistente (si existe) a la ventana de historial
    conversacional, podada a las últimas ``_HISTORY_WINDOW`` entradas. Cuando
    el turno produjo recomendaciones, incrusta una copia compacta de las mismas
    en la entrada del asistente para que el siguiente turno pueda resolver
    preguntas de seguimiento. No reintroduce campos sensibles en el estado del
    historial.
    """
    if state.response:
        history = list(state.history or [])
        entry: dict = {"role": "assistant", "content": state.response}
        metadata = [_light(rec) for rec in state.recommendations or []]
        if metadata:
            entry["recommendations"] = metadata
        history.append(entry)
        state.history = history[-_HISTORY_WINDOW:]
    return state
