from __future__ import annotations

from app.graph.state import ChatState

_HISTORY_WINDOW = 12


async def record_turn_node(state: ChatState) -> ChatState:
    """Último nodo del grafo: cierra el par user/assistant del turno.

    Agrega la respuesta del asistente (si existe) a la ventana de historial
    conversacional, podada a las últimas ``_HISTORY_WINDOW`` entradas. No
    reintroduce campos sensibles en el estado del historial.
    """
    if state.response:
        history = list(state.history or [])
        history.append({"role": "assistant", "content": state.response})
        state.history = history[-_HISTORY_WINDOW:]
    return state
