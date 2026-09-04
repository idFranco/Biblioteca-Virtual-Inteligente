"""Cliente aislado de Security-Audit-MCP.

Audita la entrada del usuario (antes de procesar) y la salida del modelo
(antes de enviar al frontend). No almacena secretos ni PII en los logs.
"""

from __future__ import annotations

from app.mcp_clients.stdio import require_env, run_mcp_tool


def _command() -> str:
    return require_env("SECURITY_AUDIT_MCP_COMMAND")


def _as_dict(value) -> dict:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        from json import JSONDecodeError, loads

        try:
            return loads(value)
        except JSONDecodeError as exc:
            raise ValueError("Security-Audit-MCP devolvió una respuesta no JSON") from exc
    raise ValueError("Security-Audit-MCP devolvió una respuesta inesperada")


async def audit_input(text: str, correlation_id: str | None = None) -> dict:
    """Audita la entrada del usuario. Devuelve {"safe": bool, "reason": str}."""
    result = await run_mcp_tool(
        _command(),
        "audit_user_input",
        {"text": text, "correlation_id": correlation_id},
        name="security-audit-mcp",
    )
    return _as_dict(result)


async def audit_output(text: str, correlation_id: str | None = None) -> dict:
    """Audita la respuesta antes de enviarla al frontend."""
    result = await run_mcp_tool(
        _command(),
        "audit_model_output",
        {"text": text, "correlation_id": correlation_id},
        name="security-audit-mcp",
    )
    return _as_dict(result)


async def sanitize_text(text: str) -> str:
    """Sanitiza un texto eliminando contenido potencialmente peligroso."""
    result = await run_mcp_tool(
        _command(),
        "sanitize_text",
        {"text": text},
        name="security-audit-mcp",
    )
    if isinstance(result, dict):
        return result.get("safe_text") or result.get("text") or text
    return str(result) if result else text
