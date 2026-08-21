"""Tests del reintento transitorio de ``_get_json`` en el servidor Open Library MCP.

Los fallos de transporte (``httpx.TransportError``, p. ej. ``ConnectError``
justo tras el build del stack) se reintentan con backoff fijo; los errores
HTTP (4xx/5xx vía ``raise_for_status``) fallan sin reintento. Usa
``httpx.MockTransport`` para no depender de red.
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


def _flaky_handler(calls: list[int], fail_times: int) -> Callable[[httpx.Request], httpx.Response]:
    """Handler que lanza ``ConnectError`` las primeras ``fail_times`` llamadas."""

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        if len(calls) <= fail_times:
            raise httpx.ConnectError("connection refused", request=request)
        return httpx.Response(200, json={"docs": []})

    return handler


def _always_error_handler(calls: list[int], response_factory: Callable[[], httpx.Response]):
    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return response_factory()

    return handler


def _client(handler: Callable[[httpx.Request], httpx.Response]) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler), timeout=5)


@pytest.fixture(autouse=True)
def _fast_retry(monkeypatch: pytest.MonkeyPatch):
    """Reintentos deterministas y sin espera real durante los tests."""
    monkeypatch.setattr(server, "OPEN_LIBRARY_RETRIES", 1)
    monkeypatch.setattr(server, "OPEN_LIBRARY_RETRY_BACKOFF_SECONDS", 0.0)


@pytest.mark.asyncio
async def test_transport_error_is_retried_and_succeeds():
    calls: list[int] = []
    async with _client(_flaky_handler(calls, fail_times=1)) as client:
        data = await server._get_json("/search.json?q=tolkien", client)

    assert data == {"docs": []}
    assert len(calls) == 2


@pytest.mark.asyncio
async def test_transport_error_raises_after_exhausting_retries():
    calls: list[int] = []
    async with _client(_flaky_handler(calls, fail_times=99)) as client:
        with pytest.raises(httpx.ConnectError):
            await server._get_json("/search.json?q=tolkien", client)

    assert len(calls) == 2


@pytest.mark.asyncio
async def test_http_status_error_is_not_retried():
    calls: list[int] = []
    handler = _always_error_handler(calls, lambda: httpx.Response(500, text="boom"))
    async with _client(handler) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await server._get_json("/search.json?q=tolkien", client)

    assert len(calls) == 1


@pytest.mark.asyncio
async def test_retries_disabled_performs_single_attempt(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(server, "OPEN_LIBRARY_RETRIES", 0)
    calls: list[int] = []
    async with _client(_flaky_handler(calls, fail_times=99)) as client:
        with pytest.raises(httpx.ConnectError):
            await server._get_json("/search.json?q=tolkien", client)

    assert len(calls) == 1


def _tool_payload(result: Any) -> dict[str, Any]:
    structured = result.structured_content
    if isinstance(structured, dict) and "result" in structured:
        return structured["result"]
    return structured


@pytest.mark.asyncio
async def test_tool_end_to_end_recovers_from_transient_connect_error(
    monkeypatch: pytest.MonkeyPatch,
):
    """La tool ``ol_search_books`` sobrevive a un ConnectError transitorio."""
    calls: list[int] = []
    handler = _flaky_handler(calls, fail_times=1)
    real_async_client = httpx.AsyncClient

    def factory(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        return real_async_client(transport=httpx.MockTransport(handler), **kwargs)

    monkeypatch.setattr(server.httpx, "AsyncClient", factory)
    monkeypatch.setattr(server, "OPEN_LIBRARY_RETRY_BACKOFF_SECONDS", 0.0)

    result = await server.mcp.call_tool("ol_search_books", {"query": "tolkien"})

    assert result.is_error is False
    assert _tool_payload(result) == []
    assert len(calls) == 2
