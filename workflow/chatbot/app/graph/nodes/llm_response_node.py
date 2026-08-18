from __future__ import annotations

from app.graph.state import ChatState
from app.llm import client as llm_client


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


async def llm_response_node(state: ChatState) -> ChatState:
    """Genera una recomendación en lenguaje natural con el LLM externo.

    Solo actúa en la intención ``recommendation``. Si el LLM no está disponible
    o falla, no modifica la respuesta heurística (fallback silencioso).
    """
    if state.intent != "recommendation":
        return state

    generated = await llm_client.generate_recommendation(_context_text(state))
    if generated:
        state.response = generated
        state.llm_used = True
    return state
