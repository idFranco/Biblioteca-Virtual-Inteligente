"""Tests de la guía conversacional del smalltalk (US-026).

Causa raíz: ``smalltalk_prompt.txt`` solo tenía una regla de cierre
(despedida/agradecimiento) y ninguna de saludo, por lo que el LLM cerraba
la conversación ante un simple "hola". Este módulo fija un guard DETERMINISTA
sobre el contenido del prompt (saludo = mantener el hilo abierto vs
despedida/agradecimiento = cierre cortés) y verifica el enrutado del grafo sin
regresión sobre los tests existentes de smalltalk (US-019/US-020).
"""

from __future__ import annotations

import pytest

from app.prompts import load_smalltalk_prompt

# Frases que indican CIERRE/despedida y no deben aparecer en una respuesta abierta
# de un saludo. (Heurística lenient en minúsculas, sin matches exactos.)
FAREWELL_MARKERS = (
    "vuelve cuando quieras",
    "que tengas un excelente día",
    "hasta pronto",
    "adiós",
    "chao",
    "nos vemos",
)


def _normalize(raw: dict):
    from app.graph.state import ChatState

    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


# --- Guard determinista: contenido del prompt (causa raíz) -------------------


def test_smalltalk_prompt_has_open_greeting_rule():
    """Regla explícita que mantiene el hilo ABIERTO ante un saludo."""
    prompt = load_smalltalk_prompt().lower()
    assert "saludo" in prompt
    assert "abierto" in prompt or "abrir" in prompt
    assert "no te despidas" in prompt or "no cierres" in prompt


def test_smalltalk_prompt_distinguishes_farewell_close():
    """La despedida/agradecimiento conserva su regla de CIERRE (Regla 4)."""
    prompt = load_smalltalk_prompt().lower()
    assert "se despide o agradece" in prompt
    assert "despídete amablemente" in prompt
    assert "invítale a volver" in prompt


def test_smalltalk_prompt_has_keep_open_phrasing():
    """El prompt pide terminar el saludo con una pregunta/invitación a continuar."""
    prompt = load_smalltalk_prompt().lower()
    assert "hilo conversacional" in prompt
    assert "terminando con una pregunta" in prompt or "invitación a continuar" in prompt


# --- Enrutado por el grafo: saludo -> smalltalk (other), sin catálogo --------


@pytest.mark.asyncio
async def test_greeting_open_response_via_graph(monkeypatch):
    """Un saludo se enruta como smalltalk y el LLM recibe el mensaje para abrir."""
    import app.mcp_clients.security_audit_client as security_client
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client
    from app.graph.build_graph import graph

    async def fake_audit(text, correlation_id=None):
        return {"safe": True}

    async def fake_estado(user_id):
        return "sin_actividad"

    async def no_search(message, limit=10):
        raise AssertionError("Un saludo no debe buscar en el catálogo")

    received: list[str] = []

    async def fake_smalltalk(message):
        received.append(message)
        # Simula el comportamiento del nuevo prompt: saludo abierto, sin despedida.
        return "¡Hola! ¿En qué puedo ayudarte hoy? ¿Buscas un libro o prefieres una recomendación?"

    def forbid_recommendation(context):
        raise AssertionError("Smalltalk no debe llamar generate_recommendation")

    monkeypatch.setattr(security_client, "audit_input", fake_audit)
    monkeypatch.setattr(security_client, "audit_output", fake_audit)
    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_estado)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", no_search)
    monkeypatch.setattr(llm_client, "generate_smalltalk", fake_smalltalk)
    monkeypatch.setattr(llm_client, "generate_recommendation", forbid_recommendation)

    state = {"message": "hola", "user_id": "user-1"}
    result = _normalize(await graph.ainvoke(state))

    assert result.intent == "other"
    assert received == ["hola"]
    assert result.response
    assert result.llm_used is True
    # La respuesta simulada del saludo es abierta (no despedida).
    assert not any(marker in result.response.lower() for marker in FAREWELL_MARKERS)


@pytest.mark.asyncio
async def test_greeting_response_is_conversational_not_farewell():
    """Un saludo NO debe producir una despedida (frases de cierre ausentes).

    No se usa LLM real: se valida la semántica esperada por el prompt aplicando
    la heurística de clases de frases al patrón de respuesta abierta definido.
    """
    prompt = load_smalltalk_prompt().lower()
    # La regla de cierre solo se aplica a despedida/agradecimiento; para un
    # saludo el prompt exige abrir el hilo (regla 5). Este aserto es el contrato.
    assert "para distinguir saludo de despedida" in prompt
    assert "un saludo abre la conversación" in prompt
    assert "un despedida o agradecimiento cierra la conversación" in prompt


@pytest.mark.asyncio
async def test_farewell_still_close_regression(monkeypatch):
    """Regresión: despedida/agradecimiento siguen cerrando cortésmente."""
    import app.mcp_clients.security_audit_client as security_client
    import app.mcp_clients.biblioteca_client as biblioteca_client
    import app.llm.client as llm_client
    from app.graph.build_graph import graph

    async def fake_audit(text, correlation_id=None):
        return {"safe": True}

    async def fake_estado(user_id):
        return "sin_actividad"

    async def no_search(message, limit=10):
        raise AssertionError("Una despedida no debe buscar en el catálogo")

    farewell = "¡Hasta luego! Gracias por visitar la biblioteca, vuelve cuando quieras."

    async def fake_smalltalk(message):
        return farewell

    def forbid_recommendation(context):
        raise AssertionError("Smalltalk no debe llamar generate_recommendation")

    monkeypatch.setattr(security_client, "audit_input", fake_audit)
    monkeypatch.setattr(security_client, "audit_output", fake_audit)
    monkeypatch.setattr(biblioteca_client, "get_estado_lectura", fake_estado)
    monkeypatch.setattr(biblioteca_client, "buscar_libros", no_search)
    monkeypatch.setattr(llm_client, "generate_smalltalk", fake_smalltalk)
    monkeypatch.setattr(llm_client, "generate_recommendation", forbid_recommendation)

    state = {"message": "gracias, hasta pronto", "user_id": "user-1"}
    result = _normalize(await graph.ainvoke(state))

    assert result.intent == "other"
    assert result.response == farewell
