from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def save_feedback_node(state: ChatState) -> ChatState:
    """Persiste el feedback vía Biblioteca-MCP (registrar_feedback).

    Resuelve el book_id consultando el catálogo por título si el payload no lo
    incluye. Un fallo del MCP no colapsa el grafo: se responde con un mensaje
    amable sin exponer errores internos.
    """
    payload = state.feedback_payload
    if not payload or not state.user_id:
        state.response = "Gracias por tu comentario. No pude asociarlo a tu cuenta."
        return state

    rating = int(payload.get("rating") or 4)
    comment = payload.get("comment")
    book_query = payload.get("book_query")

    try:
        book_id = payload.get("book_id")
        if not book_id and book_query:
            matches = await biblioteca_client.buscar_libros(book_query, limit=1)
            if matches:
                book_id = matches[0].get("id")
        if not book_id:
            state.response = "Gracias por tu comentario. No encontré el libro para guardar tu valoración."
            return state

        result = await biblioteca_client.registrar_feedback(
            state.user_id, book_id, rating, comment
        )
        if result.get("success"):
            state.response = "¡Gracias por tu valoración! La tendré en cuenta para futuras recomendaciones."
        else:
            state.response = "Gracias por tu comentario. No pude guardar tu valoración ahora mismo."
    except Exception:
        state.response = "Gracias por tu comentario. No pude guardar tu valoración ahora mismo."
    return state
