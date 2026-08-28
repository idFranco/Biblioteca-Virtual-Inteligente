from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import security_audit_client
from app.utils.pii_masker import mask_pii


async def sanitize_response_node(state: ChatState) -> ChatState:
    """Sanitiza la respuesta cuando la auditoría de salida la marcó insegura.

    Cuando Security-Audit-MCP (Groq) está disponible, se usa su sanitizado.
    Cuando falla (sin clave, error de red, modelo no encontrado), se aplica
    enmascaramiento PII local segmentado via mask_pii() en lugar de devolver
    [REDACTED] global, para preservar el contenido no sensible de la respuesta.
    """
    if not state.response:
        return state
    try:
        state.response = await security_audit_client.sanitize_text(state.response)
        state.sanitized = False
    except Exception:
        state.response = mask_pii(state.response) if state.response else ""
        state.sanitized = False
    return state
