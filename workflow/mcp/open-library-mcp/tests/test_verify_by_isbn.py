"""Tests de la tool ``ol_verify_by_isbn`` del servidor Open Library MCP.

Usa ``httpx.MockTransport`` para no depender de red. El módulo del servidor
acepta un cliente inyectado en ``_get_json``/``_verify_by_isbn`` (y la tool se
prueba de extremo a extremo parcheando ``httpx.AsyncClient``), de modo que los
tests controlan la respuesta exacta de Open Library.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable

import httpx
import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
SERVER_DIR = REPO_ROOT / "workflow" / "mcp" / "open-library-mcp"
if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

import server  # noqa: E402

# Referencia al cliente real antes de cualquier monkeypatch de httpx.AsyncClient.
REAL_ASYNC_CLIENT = httpx.AsyncClient


# --- Handlers de respuesta (httpx.MockTransport) ---------------------------------


def _found_handler(request: httpx.Request) -> httpx.Response:
    """Respuesta de /api/books para un ISBN indexado (jscmd=data)."""
    assert request.url.path == "/api/books", f"ruta inesperada: {request.url}"
    assert "bibkeys=ISBN:9780140328721" in str(request.url), f"bibkey inesperado: {request.url}"
    assert "format=json" in str(request.url)
    assert "jscmd=data" in str(request.url)
    payload = {
        "ISBN:9780140328721": {
            "url": "http://openlibrary.org/books/OL7353617M/Fantastic_Mr._Fox",
            "key": "/books/OL7353617M",
            "title": "Fantastic Mr. Fox",
            "identifiers": {
                "isbn_13": ["9780140328721"],
                "openlibrary": ["OL7353617M"],
            },
        }
    }
    return httpx.Response(200, json=payload)


def _normalized_bibkey_handler(request: httpx.Request) -> httpx.Response:
    """Open Library normaliza el bibkey (sin guiones) aunque la entrada los tenga."""
    payload = {
        "ISBN:9780140328721": {
            "key": "/books/OL7353617M",
            "title": "Fantastic Mr. Fox",
            "identifiers": {"openlibrary": ["OL7353617M"]},
        }
    }
    return httpx.Response(200, json=payload)


def _key_only_handler(request: httpx.Request) -> httpx.Response:
    """Entrada sin ``identifiers``: la clave debe extraerse del campo ``key``."""
    payload = {"ISBN:9780140328721": {"key": "/books/OL7353617M", "title": "Fantastic Mr. Fox"}}
    return httpx.Response(200, json=payload)


def _server_error_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(500, text="Internal Server Error")


def _no_network_handler(request: httpx.Request) -> httpx.Response:
    raise httpx.ConnectError("connection refused", request=request)


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.AsyncClient:
    """Cliente httpx con MockTransport para los tests sin red."""
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5)


def _mocked_client_factory(
    handler: Callable[[httpx.Request], httpx.Response],
) -> Callable[..., httpx.AsyncClient]:
    """Fábrica que reemplaza ``httpx.AsyncClient`` para pruebas de la tool."""

    def factory(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        return REAL_ASYNC_CLIENT(transport=httpx.MockTransport(handler), **kwargs)

    return factory


# --- Casos de la implementación interna (cliente inyectado) ------------------------


@pytest.mark.asyncio
async def test_found_isbn_returns_edition_key_and_title():
    async with _client(_found_handler) as client:
        result = await server._verify_by_isbn("9780140328721", client)

    assert result == {
        "isbn": "9780140328721",
        "found": True,
        "open_library_key": "/books/OL7353617M",
        "title": "Fantastic Mr. Fox",
    }


@pytest.mark.asyncio
async def test_found_isbn_with_normalized_bibkey():
    """El ISBN con guiones se resuelve aunque OL devuelva el bibkey normalizado."""
    async with _client(_normalized_bibkey_handler) as client:
        result = await server._verify_by_isbn("978-0-140328721", client)

    assert result["found"] is True
    assert result["open_library_key"] == "/books/OL7353617M"
    assert result["title"] == "Fantastic Mr. Fox"


@pytest.mark.asyncio
async def test_found_isbn_extracts_key_without_identifiers():
    async with _client(_key_only_handler) as client:
        result = await server._verify_by_isbn("9780140328721", client)

    assert result["found"] is True
    assert result["open_library_key"] == "/books/OL7353617M"
    assert result["title"] == "Fantastic Mr. Fox"


@pytest.mark.asyncio
async def test_not_found_isbn_returns_false_with_nulls():
    async with _client(lambda request: httpx.Response(200, json={})) as client:
        result = await server._verify_by_isbn("9780000000000", client)

    assert result == {
        "isbn": "9780000000000",
        "found": False,
        "open_library_key": None,
        "title": None,
    }


@pytest.mark.asyncio
async def test_http_error_raises_structured_runtime_error():
    async with _client(_server_error_handler) as client:
        with pytest.raises(RuntimeError) as exc_info:
            await server._verify_by_isbn("9780140328721", client)

    message = str(exc_info.value)
    assert "Open Library no respondió" in message
    assert "9780140328721" in message


@pytest.mark.asyncio
async def test_connection_error_raises_structured_runtime_error():
    async with _client(_no_network_handler) as client:
        with pytest.raises(RuntimeError) as exc_info:
            await server._verify_by_isbn("9780140328721", client)

    message = str(exc_info.value)
    assert "Open Library no respondió" in message
    assert "9780140328721" in message


@pytest.mark.parametrize("isbn", ["", "   ", None])
@pytest.mark.asyncio
async def test_empty_or_whitespace_isbn_raises_value_error(isbn):
    with pytest.raises(ValueError, match="El ISBN no puede estar vacío"):
        await server._verify_by_isbn(isbn)


def _tool_payload(result: Any) -> dict[str, Any]:
    """Extrae el valor devuelto por la tool de un ``ToolResult`` de FastMCP."""
    structured = result.structured_content
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured


# --- Casos de la tool expuesta vía FastMCP (extremo a extremo) ---------------------


@pytest.mark.asyncio
async def test_tool_is_registered():
    tools = await server.mcp.list_tools()
    names = {tool.name for tool in tools}
    assert "ol_verify_by_isbn" in names


@pytest.mark.asyncio
async def test_tool_end_to_end_found(monkeypatch):
    monkeypatch.setattr(server.httpx, "AsyncClient", _mocked_client_factory(_found_handler))

    result = await server.mcp.call_tool("ol_verify_by_isbn", {"isbn": "9780140328721"})

    assert result.is_error is False
    payload = _tool_payload(result)
    assert payload["found"] is True
    assert payload["open_library_key"] == "/books/OL7353617M"
    assert payload["title"] == "Fantastic Mr. Fox"


@pytest.mark.asyncio
async def test_tool_end_to_end_not_found(monkeypatch):
    monkeypatch.setattr(
        server.httpx,
        "AsyncClient",
        _mocked_client_factory(lambda request: httpx.Response(200, json={})),
    )

    result = await server.mcp.call_tool("ol_verify_by_isbn", {"isbn": "9780000000000"})

    assert result.is_error is False
    payload = _tool_payload(result)
    assert payload["found"] is False
    assert payload["open_library_key"] is None
    assert payload["title"] is None


@pytest.mark.asyncio
async def test_tool_end_to_end_rejects_empty_isbn(monkeypatch):
    monkeypatch.setattr(server.httpx, "AsyncClient", _mocked_client_factory(_found_handler))

    with pytest.raises(Exception) as exc_info:
        await server.mcp.call_tool("ol_verify_by_isbn", {"isbn": "   "})

    assert exc_info.type.__name__ in {"ToolError", "ValueError"}
    assert "El ISBN no puede estar vacío" in str(exc_info.value)
