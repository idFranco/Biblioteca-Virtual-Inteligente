"""Tests de memoria conversacional del chatbot (US-019).

Cubre:
- Continuidad entre turnos de la misma sesión (mismo thread/conversationId).
- Aislamiento entre sesiones distintas.
- Limpieza de campos transitorios del turno anterior (reset_turn).
- Enrutado smalltalk (saludo → conversacional, sin búsqueda en catálogo).
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path

import pytest

from app.graph.nodes.reset_turn_node import reset_turn_node, _TRANSIENT_FIELDS
from app.graph.nodes.record_turn_node import record_turn_node
from app.graph.nodes.classify_intent_node import classify_intent_node
from app.graph.state import ChatState


def normalize(raw: dict) -> ChatState:
    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


async def _safe(*args, **kwargs):
    return {"safe": True}


async def _sin(*args, **kwargs):
    return "sin_actividad"


async def _none(*args, **kwargs):
    return None


@pytest.fixture()
def mem_graph(monkeypatch):
    """Grafo compilado con un checkpointer persistente de memoria.

    Permite probar la continuidad entre turnos (mismo ``thread_id``) y el
    aislamiento de sesiones. Desactiva el proveedor Cloud real y los MCP.
    """
    from app.graph.build_graph import build_graph

    import app.mcp_clients.security_audit_client as sec
    import app.mcp_clients.biblioteca_client as bib
    import app.llm.client as llmc

    monkeypatch.setattr(sec, "audit_input", _safe)
    monkeypatch.setattr(sec, "audit_output", _safe)
    monkeypatch.setattr(bib, "get_estado_lectura", _sin)
    monkeypatch.setattr(llmc, "generate_recommendation", _none)

    tmp_dir = tempfile.mkdtemp(prefix="chat-memory-")
    monkeypatch.setenv("CHAT_MEMORY_DB_PATH", str(Path(tmp_dir) / "chat_memory.db"))
    return build_graph()


async def _run(graph, message: str, thread_id: str, user_id: str = "user-1") -> ChatState:
    initial_state = {
        "message": message,
        "user_id": user_id,
        "conversation_id": thread_id,
    }
    raw = await graph.ainvoke(
        initial_state, config={"configurable": {"thread_id": thread_id}}
    )
    return normalize(raw)


@pytest.mark.asyncio
async def test_same_session_accumulates_history(mem_graph):
    await _run(mem_graph, "hola", "thread-a")
    second = await _run(mem_graph, "¿me sigues? vuelve a saludarme", "thread-a")

    assert second.history is not None and len(second.history) >= 2
    assert second.history[0]["role"] == "user"
    assert second.history[0]["content"] == "hola"


@pytest.mark.asyncio
async def test_different_sessions_are_isolated(mem_graph):
    await _run(mem_graph, "hola", "thread-a")
    third = await _run(mem_graph, "hola", "thread-b")

    contents = [entry.get("content") for entry in (third.history or [])]
    assert contents.count("hola") == 1


@pytest.mark.asyncio
async def test_reset_turn_clears_transient_fields():
    state = ChatState(
        message="nuevo mensaje",
        response="respuesta anterior",
        recommendations=[{"title": "viejo"}],
        blocked=True,
        intent="recommendation",
        history=[{"role": "user", "content": "prev"}],
    )
    await reset_turn_node(state)

    for field in _TRANSIENT_FIELDS:
        value = getattr(state, field)
        assert value in ([], None, False), f"{field} no limpiado: {value!r}"
    assert state.history[-1]["content"] == "nuevo mensaje"


@pytest.mark.asyncio
async def test_record_turn_appends_assistant_response():
    state = ChatState(message="hola", response="Hola, ¿en qué te ayudo?")
    await record_turn_node(state)
    assert state.history[-1] == {"role": "assistant", "content": "Hola, ¿en qué te ayudo?"}


@pytest.mark.parametrize(
    "message, expected",
    [
        ("hola", "other"),
        ("buenas tardes", "other"),
        ("¿qué tal?", "other"),
        ("qué puedes hacer", "other"),
    ],
)
def test_smalltalk_classified(message, expected):
    state = ChatState(message=message)
    asyncio.run(classify_intent_node(state))
    assert state.intent == expected


@pytest.mark.asyncio
async def test_greeting_produces_conversational_response_without_catalog(mem_graph, monkeypatch):
    import app.mcp_clients.biblioteca_client as bib

    called: dict[str, bool] = {}

    async def fake_search(message, limit=10):
        called["search"] = True
        return []

    monkeypatch.setattr(bib, "buscar_libros", fake_search)

    raw = await mem_graph.ainvoke(
        {"message": "hola"}, config={"configurable": {"thread_id": "greet"}}
    )
    result = normalize(raw)

    assert called.get("search") is None  # no buscó en catálogo
    assert result.intent == "other"
    assert result.response  # respuesta conversacional generada
