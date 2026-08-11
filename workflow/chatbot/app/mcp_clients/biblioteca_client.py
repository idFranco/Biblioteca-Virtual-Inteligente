"""Cliente aislado de Biblioteca-MCP (solo lectura).

El chatbot usa este cliente para consultar el catálogo interno y el estado de
lectura. Nunca escribe en la base de datos (ADR-011): las escrituras van por la
API del backend con el JWT del usuario.
"""

from __future__ import annotations

import os

from app.mcp_clients.stdio import run_mcp_tool

_DEFAULT_COMMAND = "python workflow/mcp/biblioteca-mcp/server.py"


def _command() -> str:
    return os.getenv("BIBLIOTECA_MCP_COMMAND", _DEFAULT_COMMAND)


def _as_list(value) -> list[dict]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict) and "items" in value:
        return value["items"]
    return []


async def buscar_libros(search: str | None = None, limit: int = 10) -> list[dict]:
    """Busca libros en el catálogo interno de la biblioteca.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    try:
        result = await run_mcp_tool(
            _command(),
            "buscar_libros",
            {"search": search, "limit": limit},
            name="biblioteca-mcp",
        )
        return _as_list(result)
    except Exception as exc:
        raise RuntimeError(f"Biblioteca-MCP no disponible: {exc}") from exc


async def get_estado_lectura(user_id: str) -> str | None:
    """Devuelve el estado de lectura del usuario (sin_actividad, en_curso, ...).

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    if not user_id:
        return None
    try:
        result = await run_mcp_tool(
            _command(),
            "get_estado_lectura",
            {"user_id": user_id},
            name="biblioteca-mcp",
        )
        if isinstance(result, dict):
            return result.get("estado")
        return str(result) if result else None
    except Exception:
        return None
