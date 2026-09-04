"""Cliente MCP stdio aislado.

Lanza un servidor MCP por stdio, ejecuta una tool y cierra el proceso.
Cada invocación abre/cierra sesión para aislar fallos y evitar procesos vivos.
"""

from __future__ import annotations

import asyncio
import os
import shlex
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _inherit_environment() -> dict[str, str]:
    """Entorno propio del proceso para propagar variables (p. ej. DATABASE_PATH).

    La lista segura por defecto de ``get_default_environment()`` no incluye
    variables del proyecto (``DATABASE_PATH``, ``AUDIT_DATABASE_PATH``), por lo
    que se hereda el entorno completo proceso.
    """
    return {key: value for key, value in os.environ.items() if not value.startswith("()")}


def require_env(name: str) -> str:
    """Devuelve el valor de una variable de entorno requerida (fail-fast).

    Raises:
        RuntimeError: si la variable no está definida o está vacía.
    """
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno requerida '{name}' "
            f"para configurar el servidor MCP del chatbot."
        )
    return value


class McpStdioClient:
    """Cliente para un servidor MCP lanzado como subproceso por stdio."""

    def __init__(self, command: str, name: str = "mcp") -> None:
        self.name = name
        if not command or not command.strip():
            raise ValueError(f"El comando MCP '{self.name}' está vacío.")
        args = shlex.split(command)
        self._parameters = StdioServerParameters(
            command=args[0],
            args=args[1:],
            env=_inherit_environment(),
        )

    async def call_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
        async with AsyncExitStack() as stack:
            read, write = await stack.enter_async_context(stdio_client(self._parameters))
            session = await stack.enter_async_context(ClientSession(read, write))
            await session.initialize()

            tools = await session.list_tools()
            available = {t.name for t in tools.tools}
            if tool_name not in available:
                raise RuntimeError(
                    f"El servidor MCP '{self.name}' no expone la tool '{tool_name}'."
                )

            result = await session.call_tool(tool_name, arguments)
            return _parse_result(result)

    async def aclose(self) -> None:
        return None


def _parse_result(result: Any) -> Any:
    """Extrae el contenido de un resultado MCP a tipos JSON serializables.

    El SDK de MCP devuelve objetos ``CallToolResult`` que pueden exponer la
    respuesta ya parseada en ``structured_content`` (dict) o como texto en
    ``content``. Se prioriza ``structured_content`` para evitar depender de
    ``json.loads`` sobre el repr y para no filtrar la serialización interna.
    Nunca se devuelve el objeto ``CallToolResult`` crudo: si no se puede
    extraer un tipo JSON, se lanza para que el llamador aplique su fallback.
    """
    if result.isError:
        raise RuntimeError(f"MCP tool returned error: {_text_content(result)}")

    structured = getattr(result, "structured_content", None)
    if structured:
        return structured

    text = _text_content(result)
    import json

    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return text


def _text_content(result: Any) -> str:
    parts = []
    for content in result.content or []:
        if hasattr(content, "text"):
            parts.append(str(content.text))
        else:
            parts.append(str(content))
    return "\n".join(parts)


async def run_mcp_tool(command: str, tool_name: str, arguments: dict[str, Any], name: str = "mcp") -> Any:
    client = McpStdioClient(command, name)
    try:
        return await asyncio.wait_for(client.call_tool(tool_name, arguments), timeout=30)
    finally:
        await client.aclose()
