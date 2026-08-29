"""Cliente aislado de Open Library MCP.

El comando stdio se configura con ``OPEN_LIBRARY_MCP_COMMAND`` (por defecto
lanza el servidor local de este monorepo). Cualquier error se propaga como
excepción para que el grafo aplique el fallback Bug 2.
"""

from __future__ import annotations

from app.mcp_clients.stdio import require_env, run_mcp_tool


def _command() -> str:
    return require_env("OPEN_LIBRARY_MCP_COMMAND")


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


async def verify_by_isbn(isbn: str) -> dict:
    """Verifica un ISBN en Open Library vía MCP.

    Devuelve un dict con la obra si se encuentra (p. ej. ``{"key", "title"}``)
    o un dict vacío/``{"found": false}`` si no, según el contrato del servidor.

    Raises:
        RuntimeError: si el servidor no responde o falla.
    """
    result = await run_mcp_tool(
        _command(),
        "ol_verify_by_isbn",
        {"isbn": isbn},
        name="open-library",
    )
    if isinstance(result, dict) and "error" in result:
        raise RuntimeError(f"Open Library MCP: {result['error']}")
    return result if isinstance(result, dict) else {}
