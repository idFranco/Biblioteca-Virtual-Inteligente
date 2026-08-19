"""Cliente aislado de Biblioteca-MCP (solo lectura).

El chatbot usa este cliente para consultar el catálogo interno y el estado de
lectura. Nunca escribe en la base de datos (ADR-011): las escrituras van por la
API del backend con el JWT del usuario.
"""

from __future__ import annotations

from app.mcp_clients.stdio import require_env, run_mcp_tool


def _command() -> str:
    return require_env("BIBLIOTECA_MCP_COMMAND")


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


async def consultar_alquileres_usuario(user_id: str) -> list[dict]:
    """Devuelve el historial de alquileres del usuario.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    if not user_id:
        return []
    try:
        result = await run_mcp_tool(
            _command(),
            "consultar_alquileres_usuario",
            {"user_id": user_id},
            name="biblioteca-mcp",
        )
        return _as_list(result)
    except Exception as exc:
        raise RuntimeError(f"Biblioteca-MCP no disponible: {exc}") from exc


async def consultar_libro_en_curso(user_id: str) -> dict | None:
    """Devuelve el libro que el usuario tiene en curso, o None.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    if not user_id:
        return None
    try:
        result = await run_mcp_tool(
            _command(),
            "consultar_libro_en_curso",
            {"user_id": user_id},
            name="biblioteca-mcp",
        )
        if isinstance(result, dict):
            return result
        return None
    except Exception:
        return None


async def obtener_preferencias(user_id: str) -> list[dict]:
    """Devuelve las preferencias de género del usuario.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    if not user_id:
        return []
    try:
        result = await run_mcp_tool(
            _command(),
            "obtener_preferencias",
            {"user_id": user_id},
            name="biblioteca-mcp",
        )
        return _as_list(result)
    except Exception as exc:
        raise RuntimeError(f"Biblioteca-MCP no disponible: {exc}") from exc


async def listar_recomendaciones_por_genero(user_id: str, limit: int = 5) -> list[dict]:
    """Recomienda libros disponibles según el historial y preferencias del usuario.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    if not user_id:
        return []
    try:
        result = await run_mcp_tool(
            _command(),
            "listar_recomendaciones_por_genero",
            {"user_id": user_id, "limit": limit},
            name="biblioteca-mcp",
        )
        return _as_list(result)
    except Exception as exc:
        raise RuntimeError(f"Biblioteca-MCP no disponible: {exc}") from exc


async def registrar_feedback(
    user_id: str, book_id: str, rating: int, comment: str | None = None
) -> dict:
    """Registra el feedback del usuario sobre un libro.

    Raises:
        RuntimeError: si el servidor MCP no está disponible.
    """
    result = await run_mcp_tool(
        _command(),
        "registrar_feedback",
        {
            "user_id": user_id,
            "book_id": book_id,
            "rating": rating,
            "comment": comment,
        },
        name="biblioteca-mcp",
    )
    if isinstance(result, dict):
        return result
    return {"success": False, "reason": "Biblioteca-MCP devolvió un resultado inválido."}
