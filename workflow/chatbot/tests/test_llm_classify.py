"""Tests del nodo híbrido de clasificación LLM (US-027).

Cubre ``llm_classify_node``:
- Clasificación vía LLM (intent + suggested_tools + confidence).
- Fallback al clasificador heurístico cuando el LLM no está disponible.
- El "bug de recomiendes": el subjuntivo «recomiendes» que el regex no capturaba
  ahora lo resuelve el LLM (AC 1 de la historia).
"""

from __future__ import annotations

import pytest

from app.graph.nodes.llm_classify_node import llm_classify_node
from app.graph.state import ChatState


@pytest.mark.asyncio
async def test_llm_classify_uses_llm_when_available(monkeypatch):
    """Cuando el LLM responde, se usan intent/tools/confidence del LLM."""
    import app.graph.nodes.llm_classify_node as node_module

    async def fake_classify(message, user_id=None, conversation_id=None, history=None):
        return ("recommendation", ["listar_recomendaciones_por_genero"], 0.93)

    monkeypatch.setattr(node_module, "classify_intent", fake_classify)

    state = ChatState(message="¿qué me recomiendas?", user_id="user-1")
    result = await llm_classify_node(state)

    assert result.intent == "recommendation"
    assert result.suggested_tools == ["listar_recomendaciones_por_genero"]
    assert result.classification_confidence == 0.93
    assert result.llm_used is True


@pytest.mark.asyncio
async def test_other_with_high_confidence_trusted_from_llm(monkeypatch):
    """Un intent 'other' con confianza>0 del LLM se respeta (no cae al regex)."""
    import app.graph.nodes.llm_classify_node as node_module

    async def fake_classify(message, user_id=None, conversation_id=None, history=None):
        return ("other", [], 0.8)

    monkeypatch.setattr(node_module, "classify_intent", fake_classify)

    state = ChatState(message="hola, ¿cómo estás?", user_id="user-1")
    result = await llm_classify_node(state)

    assert result.intent == "other"
    assert result.llm_used is True
    assert result.classification_confidence == 0.8


@pytest.mark.asyncio
async def test_fallback_to_regex_when_llm_other_with_zero_confidence(monkeypatch):
    """LLM devuelve (other, [], 0.0) -> cae al clasificador heurístico."""
    import app.graph.nodes.llm_classify_node as node_module

    async def fake_classify(message, user_id=None, conversation_id=None, history=None):
        return ("other", [], 0.0)

    monkeypatch.setattr(node_module, "classify_intent", fake_classify)

    state = ChatState(message="recomiéndame una novela", user_id="user-1")
    result = await llm_classify_node(state)

    # El regex captura «recomiéndame» -> recommendation
    assert result.intent == "recommendation"
    assert result.llm_used is False
    assert result.classification_confidence == 0.0


@pytest.mark.asyncio
async def test_recomiendes_subjunctive_resolved_by_llm(monkeypatch):
    """`recomiendes` (subjuntivo, no capturado por el regex) se resuelve por LLM.

    Sin el LLM, «¿qué libro me recomiendes?» caía a book_query (bug original).
    Con el LLM activo y respondiendo recommendation, el intent es el correcto.
    """
    import app.graph.nodes.llm_classify_node as node_module

    async def fake_classify(message, user_id=None, conversation_id=None, history=None):
        return ("recommendation", ["listar_recomendaciones_por_genero"], 0.9)

    monkeypatch.setattr(node_module, "classify_intent", fake_classify)

    state = ChatState(message="¿qué libro me recomiendes?", user_id="user-1")
    result = await llm_classify_node(state)

    assert result.intent == "recommendation"
    assert result.llm_used is True


@pytest.mark.asyncio
async def test_llm_classify_throws_does_not_crash(monkeypatch):
    """Si classify_intent lanza (no debería), el nodo no debe colapsar."""
    import app.graph.nodes.llm_classify_node as node_module

    async def fake_classify(message, user_id=None, conversation_id=None, history=None):
        raise RuntimeError("LLM caído")

    monkeypatch.setattr(node_module, "classify_intent", fake_classify)

    state = ChatState(message="hola", user_id="user-1")
    result = await llm_classify_node(state)
    assert result.intent == "other"
