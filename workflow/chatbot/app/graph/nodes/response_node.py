from __future__ import annotations

from app.graph.state import ChatState


def _recommendation_text(state: ChatState) -> str:
    """Compone la respuesta heurística con las recomendaciones disponibles."""
    if not state.recommendations:
        return (
            "Aún no tengo suficientes datos para recomendarte. "
            "Alquila algún libro o cuéntame tus géneros favoritos y volveré a intentarlo."
        )

    lines = []
    for index, item in enumerate(state.recommendations, start=1):
        title = item.get("title", "un libro")
        author = item.get("author")
        genre = item.get("genre")
        reason = item.get("reason")
        detail = f"«{title}»" + (f" de {author}" if author else "")
        if genre:
            detail += f" ({genre})"
        if reason:
            detail += f" — {reason}"
        lines.append(f"{index}. {detail}")

    return "Basándome en tu historial, te recomiendo:\n" + "\n".join(lines)


async def response_node(state: ChatState) -> ChatState:
    """Genera la respuesta final para el usuario."""
    if state.response:
        return state

    if state.intent == "recommendation":
        state.response = _recommendation_text(state)
        return state

    if state.intent == "status":
        reading_state = state.reading_state or "sin_actividad"
        state.response = (
            f"Tu estado de lectura actual es «{reading_state}». "
            "Puedes consultar tus alquileres en la sección 'Mis alquileres'."
        )
        return state

    if state.intent == "feedback":
        state.response = "Gracias por tu valoración."
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
