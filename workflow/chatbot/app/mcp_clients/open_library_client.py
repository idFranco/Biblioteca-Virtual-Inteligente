"""Cliente aislado de Open Library MCP.

El comando stdio se configura con ``OPEN_LIBRARY_MCP_COMMAND`` (por defecto
lanza el servidor local de este monorepo). Cualquier error se propaga como
excepción para que el grafo aplique el fallback Bug 2.
"""

from __future__ import annotations

import os

from app.mcp_clients.stdio import run_mcp_tool

_DEFAULT_COMMAND = (
    "python workflow/mcp/open-library-mcp/server.py"
)


def _command() -> str:
    return os.getenv("OPEN_LIBRARY_MCP_COMMAND", _DEFAULT_COMMAND)


async def search_books(query: str, limit: int = 5) -> list[dict]:
    """Busca libros en Open Library vía MCP.

    Raises:
        RuntimeError: si el servidor no responde o falla, para activar el fallback.
    """
    results = await run_mcp_tool(
        _command(),
        "ol_search_books",
        {"query": query, "limit": limit},
        name="open-library",
    )
    if isinstance(results, dict) and "error" in results:
        raise RuntimeError(f"Open Library MCP: {results['error']}")
    return results if isinstance(results, list) else []


async def get_book_details(key: str) -> dict:
    """Obtiene el detalle de una obra vía MCP.

    Raises:
        RuntimeError: si el servidor no responde o falla.
    """
    details = await run_mcp_tool(
        _command(),
        "ol_get_book_details",
        {"key": key},
        name="open-library",
    )
    if not isinstance(details, dict):
        raise RuntimeError("Open Library MCP devolvió un detalle inválido.")
    return details
