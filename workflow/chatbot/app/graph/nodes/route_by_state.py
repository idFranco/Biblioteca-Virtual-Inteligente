from __future__ import annotations

from app.graph.state import ChatState


def route_by_state(state: ChatState) -> str:
    """Enruta el flujo según la intención clasificada y el estado de lectura.

    Devuelve la clave de rama que el grafo mapea a los nodos siguientes:
    recommendation, due_reminder, overdue, status_plain, feedback,
    book_query u other.
    """
    if state.intent == "recommendation":
        return "recommendation"

    if state.intent == "status":
        reading_state = state.reading_state or "sin_actividad"
        if reading_state == "por_vencer":
            return "due_reminder"
        if reading_state == "vencido":
            return "overdue"
        return "status_plain"

    if state.intent == "feedback":
        return "feedback"

    if state.intent == "book_query":
        return "book_query"

    return "other"
