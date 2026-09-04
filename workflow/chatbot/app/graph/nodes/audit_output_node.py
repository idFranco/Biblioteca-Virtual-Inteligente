from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import security_audit_client


async def audit_output_node(state: ChatState) -> ChatState:
    """Audita la salida antes de enviarla al frontend.

    Si el output se considera inseguro, lo marca para sanitización.
    Si el MCP de auditoría falla (excepción), se degrada a fail-closed: se
    marca ``sanitized=True`` para que ``sanitize_response_node`` aplique si o si
    la sanitización local ``mask_pii`` (nunca se envía salida sin sanear).
    """
    if not state.response:
        return state
    try:
        result = await security_audit_client.audit_output(
            state.response, state.correlation_id
        )
        state.sanitized = not bool(result.get("safe", True))
    except Exception:
        state.sanitized = True
    return state
