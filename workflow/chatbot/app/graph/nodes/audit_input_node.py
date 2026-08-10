from __future__ import annotations

from app.graph.state import ChatState
from app.mcp_clients import security_audit_client


async def audit_input_node(state: ChatState) -> ChatState:
    """Audita la entrada del usuario antes de ser procesada por el grafo."""
    try:
        result = await security_audit_client.audit_input(
            state.message, state.correlation_id
        )
        state.blocked = not bool(result.get("safe", True))
    except Exception:
        state.blocked = False
    return state
