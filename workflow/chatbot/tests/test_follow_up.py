"""Tests del seguimiento de recomendaciones (US-019 AC#4).

Cubre:
- Clasificación de la intención ``follow_up`` (y que un título citado siga
  siendo una búsqueda de catálogo).
- Resolución del selector («la primera», «la segunda», …, «la última»).
- Continuidad turno a turno: una pregunta sobre una recomendación previa
  responde con los detalles del libro recomendado.
- Metadatos de recomendaciones incrustados en el historial y su limpieza de
  campos sensibles.
- Fallbacks: sin recomendaciones previas, sesión aislada y LLM disponible.
"""

from __future__ import annotations

import asyncio
import re
import tempfile
import unicodedata
from pathlib import Path

import pytest

from app.graph.nodes.classify_intent_node import classify_intent_node
from app.graph.nodes.follow_up_node import (
    _last_recommendations,
    _resolve_index,
    follow_up_node,
)
from app.graph.nodes.record_turn_node import record_turn_node
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


def _catalog():
    return [
        {
            "id": 21,
            "title": "El nombre del viento",
            "author": "Patrick Rothfuss",
            "genre": "Fantasía",
            "isbn": "9788401337208",
            "available_copies": 3,
            "reason": "Por tu historial de lectura en Fantasía.",
        },
        {
            "id": 22,
            "title": "El aprendiz de asesino",
            "author": "Robin Hobb",
            "genre": "Fantasía",
            "isbn": "9788466607335",
            "available_copies": 1,
            "reason": "Novela de Fantasía altamente valorada.",
        },
    ]


async def _preferences(user_id, *args, **kwargs):
    return [{"genre": "Fantasía"}]


async def _recommend(user_id, limit=5, *args, **kwargs):
    return _catalog()


@pytest.fixture()
def follow_graph(monkeypatch):
    """Grafo compilado con checkpointer de memoria y catálogo simulado."""
    from app.graph.build_graph import build_graph

    import app.mcp_clients.biblioteca_client as bib
    import app.mcp_clients.security_audit_client as sec
    import app.llm.client as llmc

    monkeypatch.setattr(sec, "audit_input", _safe)
    monkeypatch.setattr(sec, "audit_output", _safe)
    monkeypatch.setattr(bib, "get_estado_lectura", _sin)
    monkeypatch.setattr(bib, "obtener_preferencias", _preferences)
    monkeypatch.setattr(bib, "listar_recomendaciones_por_genero", _recommend)
    monkeypatch.setattr(llmc, "generate_recommendation", _none)

    tmp_dir = tempfile.mkdtemp(prefix="chat-follow-")
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


@pytest.mark.parametrize(
    "message, expected",
    [
        ("cuéntame más sobre la primera", "follow_up"),
        ("cuéntame más de la segunda", "follow_up"),
        ("dime más sobre ese libro", "follow_up"),
        ("háblame de tu recomendación", "follow_up"),
        ("dame más detalles de la segunda", "follow_up"),
        ("¿puedes ampliar la información?", "follow_up"),
        ("cuéntame más sobre «El nombre del viento»", "book_query"),
        ("quiero el libro «Dune»", "book_query"),
        ("ese libro que me recomendaste me encantó", "feedback"),
        ("recomiéndame un libro de fantasía", "recommendation"),
        ("¿mis alquileres?", "status"),
        ("hola", "other"),
        ("¿tienen Cien años de soledad?", "book_query"),
    ],
)
def test_follow_up_classified(message, expected):
    state = ChatState(message=message)
    asyncio.run(classify_intent_node(state))
    assert state.intent == expected


def test_resolve_selector_ordinal():
    items = [{"title": "A"}, {"title": "B"}, {"title": "C"}]
    assert _resolve_index("cuéntame más sobre la primera", items) == 0
    assert _resolve_index("cuéntame más sobre la segunda", items) == 1
    assert _resolve_index("cuéntame más sobre la tercera", items) == 2
    assert _resolve_index("cuéntame más sobre la última", items) == 2
    assert _resolve_index("dime más sobre la quinta", items) == 2  # piso al máximo
    assert _resolve_index("háblame de ese libro", items) == 0        # sin selector
    assert _resolve_index("cuéntame algo más", items) == 0           # sin selector


def test_last_recommendations_from_assistant_entries():
    state = ChatState(
        message="x",
        history=[
            {"role": "user", "content": "hola"},
            {"role": "assistant", "content": "saludo"},
            {"role": "user", "content": "rec"},
            {
                "role": "assistant",
                "content": "te recomiendo",
                "recommendations": [{"title": "A"}],
            },
        ],
    )
    assert _last_recommendations(state) == [{"title": "A"}]


@pytest.mark.asyncio
async def test_record_turn_embeds_recommendations_metadata():
    state = ChatState(
        message="rec",
        response="te recomiendo",
        recommendations=[
            {"title": "Un libro", "author": "Alguien", "secret_field": "no debe persistir"}
        ],
    )
    await record_turn_node(state)
    entry = state.history[-1]
    assert entry["role"] == "assistant"
    assert entry["recommendations"] == [{"title": "Un libro", "author": "Alguien"}]
    assert "secret_field" not in entry["recommendations"][0]


@pytest.mark.asyncio
async def test_record_turn_without_recommendations_has_no_metadata():
    state = ChatState(message="hola", response="Hola, ¿en qué te ayudo?")
    await record_turn_node(state)
    assert state.history[-1] == {"role": "assistant", "content": "Hola, ¿en qué te ayudo?"}


@pytest.mark.asyncio
async def test_follow_up_node_clarifies_without_history():
    state = ChatState(message="cuéntame más sobre la primera")
    await follow_up_node(state)
    assert state.intent is None
    assert "recomiéndame" in (state.response or "")
    assert state.recommendations == []


@pytest.mark.asyncio
async def test_follow_up_resolves_first_recommendation(follow_graph):
    t1 = await _run(
        follow_graph, "recomiéndame un libro de fantasía", "thread-f1", "user-f1"
    )
    assert t1.intent == "recommendation"
    assert len(t1.recommendations) == 2
    assert "El nombre del viento" in t1.recommendations[0]["title"]

    t2 = await _run(follow_graph, "cuéntame más sobre la primera", "thread-f1", "user-f1")
    assert t2.intent == "follow_up"
    assert "El nombre del viento" in (t2.response or "")
    assert (t2.recommendations or [])[0]["title"] == "El nombre del viento"
    assert t2.response != t1.response  # el transitorio del turno 1 quedó limpio


@pytest.mark.asyncio
async def test_follow_up_resolves_second_recommendation(follow_graph):
    await _run(follow_graph, "recomiéndame un libro de fantasía", "thread-f2", "user-f2")
    t2 = await _run(follow_graph, "y ¿qué me cuentas de la segunda?", "thread-f2", "user-f2")
    assert t2.intent == "follow_up"
    assert "El aprendiz de asesino" in (t2.response or "")


@pytest.mark.asyncio
async def test_follow_up_uses_llm_when_available(follow_graph, monkeypatch):
    import app.llm.client as llmc

    async def fake_llm(context, *args, **kwargs):
        return "Sobre el libro que te recomendé: es el inicio de la Crónica del Asesino."

    monkeypatch.setattr(llmc, "generate_recommendation", fake_llm)

    await _run(follow_graph, "recomiéndame un libro de fantasía", "thread-f3", "user-f3")
    t2 = await _run(follow_graph, "cuéntame más sobre la primera", "thread-f3", "user-f3")
    assert t2.intent == "follow_up"
    assert t2.llm_used is True
    assert "Crónica del Asesino" in (t2.response or "")


@pytest.mark.asyncio
async def test_follow_up_fresh_thread_clarifies_without_catalog(follow_graph, monkeypatch):
    import app.mcp_clients.biblioteca_client as bib

    called: dict[str, bool] = {}

    async def fake_search(message, limit=10):
        called["search"] = True
        return []

    monkeypatch.setattr(bib, "buscar_libros", fake_search)

    t = await _run(follow_graph, "cuéntame más sobre la primera", "thread-fresh")
    assert t.intent == "follow_up"
    assert "recomiéndame" in (t.response or "")
    assert called.get("search") is None  # no buscó en catálogo


@pytest.mark.asyncio
async def test_follow_up_sessions_are_isolated(follow_graph):
    await _run(follow_graph, "recomiéndame un libro de fantasía", "thread-iso", "user-iso")
    t = await _run(follow_graph, "cuéntame más sobre la primera", "thread-iso-2", "user-iso")
    assert t.intent == "follow_up"
    assert "recomiéndame" in (t.response or "")  # sin recomendación previa en esta sesión


@pytest.mark.asyncio
async def test_follow_up_attaches_open_library_description(follow_graph, monkeypatch):
    import app.mcp_clients.open_library_client as ol

    async def fake_verify(isbn, *args, **kwargs):
        return {"found": True, "open_library_key": "/works/OL123W"}

    async def fake_details(key, *args, **kwargs):
        return {"description": "Primer libro de una saga inspirada en la música."}

    monkeypatch.setattr(ol, "verify_by_isbn", fake_verify)
    monkeypatch.setattr(ol, "get_book_details", fake_details)

    await _run(follow_graph, "recomiéndame un libro de fantasía", "thread-desc", "user-desc")
    t2 = await _run(follow_graph, "cuéntame más sobre la primera", "thread-desc", "user-desc")
    assert "saga" in (t2.response or "")
