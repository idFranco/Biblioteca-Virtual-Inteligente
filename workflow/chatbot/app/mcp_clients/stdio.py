"""Cliente MCP stdio aislado.

Lanza un servidor MCP por stdio, ejecuta una tool y cierra el proceso.
Cada invocación abre/cierra sesión para aislar fallos y evitar procesos vivos.
"""

from __future__ import annotations

import asyncio
import shlex
from contextlib import AsyncExitStack
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpStdioClient:
    """Cliente para un servidor MCP lanzado como subproceso por stdio."""

    def __init__(self, command: str, name: str = "mcp") -> None:
        self.name = name
        if not command or not command.strip():
            raise ValueError(f"El comando MCP '{self.name}' está vacío.")
        args = shlex.split(command)
        self._parameters = StdioServerParameters(command=args[0], args=args[1:])

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
    """Extrae el contenido de un resultado MCP a tipos JSON serializables."""
    try:
        if result.isError:
            text = _text_content(result)
            raise RuntimeError(f"MCP tool returned error: {text}")
        text = _text_content(result)
        import json

        try:
            return json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return text
    except AttributeError:
        return result


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
