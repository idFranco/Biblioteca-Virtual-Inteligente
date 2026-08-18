from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def due_reminder_node(state: ChatState) -> ChatState:
    """Informa al usuario de su alquiler por vencer.

    Consulta el libro en curso vía Biblioteca-MCP para incluir el título y la
    fecha límite. Un fallo del MCP no bloquea la respuesta amable.
    """
    title: str | None = None
    due_date: str | None = None
    if state.user_id:
        try:
            current = await biblioteca_client.consultar_libro_en_curso(state.user_id)
            if current:
                title = current.get("title")
                due_date = current.get("due_date")
        except Exception:
            title = None

    if title and due_date:
        state.response = (
            f"Tu alquiler «{title}» está por vencer el {due_date}. "
            "Recuerda devolverlo a tiempo para liberar el stock."
        )
    else:
        state.response = (
            "Tienes un alquiler por vencer pronto. "
            "Consulta 'Mis alquileres' para ver la fecha límite y devolverlo a tiempo."
        )
    return state
