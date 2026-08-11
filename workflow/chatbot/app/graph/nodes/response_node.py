from __future__ import annotations

from app.graph.state import ChatState


async def response_node(state: ChatState) -> ChatState:
    """Genera la respuesta final para el usuario."""
    if state.response:
        return state

    if state.intent == "status":
        reading_state = state.reading_state or "sin_actividad"
        state.response = (
            f"Tu estado de lectura actual es «{reading_state}». "
            "Puedes consultar tus alquileres en la sección 'Mis alquileres'."
        )
        return state

    if state.intent == "recommendation":
        state.response = (
            "Puedo recomendarte libros según tu historial. "
            "Escribe el título o autor que te interesa y lo busco para ti."
        )
        return state

    if state.catalog_matches:
        top = state.catalog_matches[0]
        state.response = (
            f"Encontramos «{top.get('title')}» de {top.get('author')} en nuestro catálogo. "
            "Está disponible para alquilar desde el catálogo."
        )
        return state

    title = (state.enrichment or {}).get("title") or "este libro"
    if state.enrichment_error and not state.enrichment:
        state.response = _friendly_not_available(title)
        return state

    state.response = (
        f"El libro «{title}» no está en nuestro catálogo en este momento. "
        "Puedes solicitar una copia y estará disponible pronto. ¿Quieres que la registre?"
    )
    return state


def _friendly_not_available(title: str) -> str:
    return (
        f"No hemos encontrado «{title}» en nuestro catálogo por el momento. "
        "Puedes solicitarlo más adelante o consultar el catálogo para libros similares."
    )
