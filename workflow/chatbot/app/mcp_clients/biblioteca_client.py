"""Cliente aislado de Biblioteca-MCP (solo lectura).

El chatbot usa este cliente para consultar el catálogo interno y el estado de
lectura. Nunca escribe en la base de datos (ADR-011): las escrituras van por la
API del backend con el JWT del usuario.
"""

from __future__ import annotations

import ast
import json
import re

from app.mcp_clients.stdio import require_env, run_mcp_tool


def _command() -> str:
    return require_env("BIBLIOTECA_MCP_COMMAND")


_EMBEDDED_JSON = re.compile(r"\{.*?\}", re.DOTALL)


def _try_dict(candidate: str) -> dict | None:
    """Intenta interpretar ``candidate`` como dict JSON o literal de Python."""
    try:
        parsed = json.loads(candidate)
        return parsed if isinstance(parsed, dict) else None
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        parsed = ast.literal_eval(candidate)
        return parsed if isinstance(parsed, dict) else None
    except (ValueError, SyntaxError):
        return None


def _extract_estado(result) -> str | None:
    """Extrae el valor 'estado' de una respuesta de Biblioteca-MCP de forma robusta.

    El resultado puede llegar como ``dict``, como ``str`` con JSON/literal válido,
    o como la representación de un objeto ``CallToolResult`` con un JSON embebido
    en su ``repr``. Nunca se devuelve la serialización cruda (evita fugas de
    user_id).
    """
    if isinstance(result, dict):
        estado = result.get("estado")
        return str(estado) if isinstance(estado, str) and estado else None

    if isinstance(result, str):
        candidates = [result] + [m.group(0) for m in _EMBEDDED_JSON.finditer(result)]
        for candidate in candidates:
            parsed = _try_dict(candidate)
            if parsed is not None:
                estado = parsed.get("estado")
                if isinstance(estado, str) and estado:
                    return estado
        return None

    return None


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

    Extrae únicamente el valor ``estado`` de la respuesta de Biblioteca-MCP,
    sin exponer el ``user_id`` ni la serialización interna del cliente MCP.

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
        return _extract_estado(result)
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
