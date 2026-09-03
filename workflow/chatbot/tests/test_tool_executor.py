"""Tests del nodo determinista de ejecución de herramientas (US-027).

Cubre ``tool_executor_node``:
- Ejecuta las tools sugeridas por el LLM y almacena resultados en tool_results.
- Desduplica tools repetidas.
- Fallo individual de una tool no rompe el turno (ok=False).
- Tool desconocida no rompe el turno.
"""

from __future__ import annotations

import pytest

from app.graph.nodes.tool_executor_node import tool_executor_node, execute_tool
from app.graph.state import ChatState


@pytest.mark.asyncio
async def test_tool_executor_runs_suggested_tools(monkeypatch):
    """Cuando el LLM sugiere tools, se ejecutan y guardan sus resultados."""
    import app.graph.nodes.tool_executor_node as node_module

    calls = {}

    async def fake_buscar(search, limit=10):
        calls["search"] = search
        return [{"title": "Cien años de soledad"}]

    async def fake_obtener_preferencias(user_id):
        calls["user_id"] = user_id
        return [{"genre": "realismo mágico"}]

    monkeypatch.setitem(node_module._TOOL_REGISTRY, "buscar_libros", fake_buscar)
    monkeypatch.setitem(
        node_module._TOOL_REGISTRY, "obtener_preferencias", fake_obtener_preferencias
    )

    state = ChatState(
        message="tienen Cien años del soledad",
        query="Cien años de soledad",
        user_id="user-1",
        suggested_tools=["buscar_libros", "obtener_preferencias"],
    )
    result = await tool_executor_node(state)

    assert calls["search"] == "Cien años de soledad"
    assert calls["user_id"] == "user-1"
    assert len(result.tool_results) == 2
    assert all(r["ok"] is True for r in result.tool_results)


@pytest.mark.asyncio
async def test_tool_executor_deduplicates_tools(monkeypatch):
    """Tools duplicadas se ejecutan una sola vez."""
    import app.graph.nodes.tool_executor_node as node_module

    calls = {"n": 0}

    async def fake_buscar(search, limit=10):
        calls["n"] += 1
        return []

    monkeypatch.setitem(node_module._TOOL_REGISTRY, "buscar_libros", fake_buscar)

    state = ChatState(
        message="libro",
        user_id="user-1",
        suggested_tools=["buscar_libros", "buscar_libros", "buscar_libros"],
    )
    result = await tool_executor_node(state)

    assert calls["n"] == 1
    assert len(result.tool_results) == 1


@pytest.mark.asyncio
async def test_tool_executor_no_suggested_tools(monkeypatch):
    """Sin sugerencias, tool_results queda vacío (factoría por defecto)."""
    state = ChatState(message="hola", user_id="user-1", suggested_tools=[])
    result = await tool_executor_node(state)
    assert result.tool_results == []


@pytest.mark.asyncio
async def test_execute_tool_unknown_tool():
    """Tool desconocida -> resultado ok=False sin lanzar."""
    state = ChatState(message="x", user_id="user-1")
    result = await execute_tool("no_existe", state)
    assert result["ok"] is False
    assert "desconocida" in result["error"]


@pytest.mark.asyncio
async def test_execute_tool_failure_does_not_crash(monkeypatch):
    """Fallo de una tool -> ok=False, no lanza."""
    import app.graph.nodes.tool_executor_node as node_module

    async def boom_search(search, limit=10):
        raise RuntimeError("MCP caído")

    monkeypatch.setitem(node_module._TOOL_REGISTRY, "buscar_libros", boom_search)

    state = ChatState(message="libro", query="libro", user_id="user-1")
    result = await execute_tool("buscar_libros", state)

    assert result["ok"] is False
    assert result["tool"] == "buscar_libros"


@pytest.mark.asyncio
async def test_execute_user_scoped_tool_without_user_id(monkeypatch):
    """Tool de ámbito usuario sin user_id -> ok=False sin llamar al MCP."""
    import app.graph.nodes.tool_executor_node as node_module

    called = []

    async def fake_prefs(user_id):
        called.append(user_id)
        return []

    monkeypatch.setitem(node_module._TOOL_REGISTRY, "obtener_preferencias", fake_prefs)

    state = ChatState(message="preferencias", user_id=None)
    result = await execute_tool("obtener_preferencias", state)
    assert result["ok"] is False
    assert "Usuario no identificado" in result["error"]
    assert called == []
