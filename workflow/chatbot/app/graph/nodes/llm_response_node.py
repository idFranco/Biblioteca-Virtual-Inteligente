from __future__ import annotations

from app.graph.state import ChatState
from app.llm import client as llm_client
from app.utils.pii_masker import mask_message


def _history_window(state: ChatState) -> str:
    """Construye la ventana de historial conversacional enmascarada (sin PII)."""
    history = list(getattr(state, "history", None) or [])
    if not history:
        return ""
    lines = []
    for entry in history:
        role = entry.get("role") or "user"
        content = mask_message(str(entry.get("content") or ""), state.user_id)
        lines.append(f"{role}: {content}")
    return "\n".join(lines)


def _context_text(state: ChatState) -> str:
    """Construye el contexto enmascarado con los libros candidatos."""
    if state.recommendations:
        books = "\n".join(
            f"- «{item.get('title')}» de {item.get('author')} "
            f"[{item.get('genre')}] disponible={item.get('available_copies', 0) > 0}"
            for item in state.recommendations
        )
        return f"Preferencias del usuario: {state.preferences}\nLibros candidatos:\n{books}"
    if state.catalog_matches:
        books = "\n".join(
            f"- «{item.get('title')}» de {item.get('author')}"
            for item in state.catalog_matches
        )
        return f"Resultados del catálogo:\n{books}"
    return "Sin resultados."


def _greeting_fallback() -> str:
    return (
        "¡Hola! Soy el asistente de la biblioteca virtual. Puedo recomendarte "
        "libros según tu historial, buscar títulos en el catálogo y resolver "
        "dudas sobre tus alquileres. ¿En qué puedo ayudarte?"
    )


async def llm_response_node(state: ChatState) -> ChatState:
    """Genera una respuesta en lenguaje natural con el LLM externo.

    Actúa en ``recommendation`` (recomendación validada), ``follow_up``
    (pregunta sobre una recomendación previa, US-019 AC#4) y en ``smalltalk``
    (saludo/smalltalk conversacional, ``intent == "other"``), inyectando la
    ventana de historial enmascarada al prompt. Si el LLM no está disponible o
    falla, usa el fallback heurístico (recomendación, seguimiento o saludo) sin
    colapsar.
    """
    if state.intent not in ("recommendation", "other", "follow_up"):
        return state

    history_text = _history_window(state)
    if state.intent == "other":
        generated = await llm_client.generate_smalltalk(state.message)
        if generated:
            state.response = generated
            state.llm_used = True
        elif not state.response:
            state.response = _greeting_fallback()
        return state

    base_context = _context_text(state)

    context = base_context
    if history_text:
        context = f"Historial reciente de la conversación:\n{history_text}\n\n{context}"

    generated = await llm_client.generate_recommendation(context)
    if generated:
        state.response = generated
        state.llm_used = True
    return state
