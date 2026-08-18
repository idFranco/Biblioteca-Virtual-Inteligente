from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import biblioteca_client


async def overdue_node(state: ChatState) -> ChatState:
    """Informa al usuario de un alquiler vencido pendiente de devolución."""
    title: str | None = None
    if state.user_id:
        try:
            current = await biblioteca_client.consultar_libro_en_curso(state.user_id)
            if current:
                title = current.get("title")
        except Exception:
            title = None

    if title:
        state.response = (
            f"Tu alquiler «{title}» está vencido. "
            "Devuélvelo lo antes posible para liberar el stock."
        )
    else:
        state.response = (
            "Tienes un alquiler vencido. "
            "Devuélvelo lo antes posible desde la sección 'Mis alquileres'."
        )
    return state
