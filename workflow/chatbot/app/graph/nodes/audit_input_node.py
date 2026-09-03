from __future__ import annotations

import re

from app.graph.state import ChatState
from app.mcp_clients import security_audit_client


_CREDENTIAL_OR_INJECTION = re.compile(
    r"ignor(?:a|e|ad)\s+(?:las\s+|tus\s+|mis\s+)?(?:instrucciones|indicaciones|prompt|reglas)"
    r"|ignore\s+(?:previous|all|prior)\s+instructions"
    r"|reveal\s+your\s+(?:system|instructions)|est[aá]s\s+desbloqueado"
    r"|(?:dame|d[aá]me|p[aá]same|pasa|suministr(?:a|ar|e|as)|proporcion(?:a|ar|e|as)|"
    r"facilit(?:a|ar|e|as)|env[ií](?:a|ar|e|as)|compart(?:e|ir|a|as)|cu[aá]l\s+es|"
    r"(?:give|send|show|provide|reveal|share)\s+(?:me\s+|us\s+|them\s+|your\s+|my\s+)?"
    r")\s*(?:la\s+|el\s+|tu\s+|su\s+|mi\s+)?(?:password|contrase[ñn]a|jwt|token|"
    r"session|sesi[oó]n|cookie|api[_-]?key|access[_-]?token|secret|secreto|"
    r"credentials?|credencial(?:es)?|otp|pin|c[oó]digo)"
    r"|(?:la\s+|el\s+|mi\s+|tu\s+|your\s+|my\s+|the\s+)?(?:contrase[ñn]a|password)\b"
    r"|<script|</script>|javascript:\s*|union\s+select"
    r"",
    re.IGNORECASE,
)


def _detect_local_credential_or_injection(message: str) -> bool:
    """Detector local determinista de credenciales/inyección (fallback fail-closed).

    Se usa cuando el MCP de auditoría de entrada no está disponible. Replica un
    subconjunto de los patrones de ``local_audit`` para que el sistema no degrade
    a fail-open; cubre peticiones de credenciales e inyección conocidas.
    """
    if not message:
        return False
    return bool(_CREDENTIAL_OR_INJECTION.search(message))


async def audit_input_node(state: ChatState) -> ChatState:
    """Audita la entrada del usuario antes de ser procesada por el grafo.

    Si el MCP de auditoría falla, se degrada a fail-closed: se aplica la
    detección local determinista y se bloquea si el input parece malicioso.
    """
    try:
        result = await security_audit_client.audit_input(
            state.message, state.correlation_id
        )
        state.blocked = not bool(result.get("safe", True))
    except Exception:
        state.blocked = _detect_local_credential_or_injection(state.message)
    return state
