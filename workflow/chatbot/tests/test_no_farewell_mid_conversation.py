"""Tests de US-028: sin saludos duplicados ni despedidas prematuras.

Causa raíz: ``generate_smalltalk()`` no recibía el historial conversacional
(por lo que el LLM saludaba de nuevo en medio de una conversación) y los prompts
no prohibían explícitamente las frases de despedida cuando el usuario NO se
despedía. Este módulo fija guards deterministas sobre el contenido de los
prompts (saludo NO duplicado, despedida NO prematura) y verifica que el historial
se inyecta en el prompt de smalltalk.
"""

from __future__ import annotations

from app.prompts import load_guide_prompt, load_recommendation_prompt, load_smalltalk_prompt

# Frases de CIERRE/despedida que no deben aparecer en medio de una conversación
# (un usuario que no se despide). Heurística lenient en minúsculas.
FAREWELL_MARKERS = (
    "espero verte pronto",
    "vuelve cuando quieras",
    "que tengas un excelente día",
    "que tengas un excelente dia",
    "hasta pronto",
    "nos vemos",
)


def _normalize(raw: dict):
    from app.graph.state import ChatState

    defaults = ChatState(message=raw.get("message") or "")
    for field in defaults.__dataclass_fields__:
        if field in raw:
            setattr(defaults, field, raw[field])
    return defaults


# --- Guard determinista del prompt: no saludo duplicado -----------------------


def test_smalltalk_prompt_forbids_duplicate_greeting():
    """El prompt prohíbe saludar de nuevo si ya hubo interacción previa."""
    prompt = load_smalltalk_prompt().lower()
    assert "no saludes de nuevo" in prompt
    assert "historial" in prompt
    assert any(marker in prompt for marker in ("hola de nuevo", "hola otra vez"))


def test_smalltalk_prompt_forbids_premature_farewell():
    """El prompt prohíbe usar frases de despedida cuando el usuario no se despide."""
    prompt = load_smalltalk_prompt().lower()
    assert "no uses frases de despedida" in prompt
    assert "a menos que el usuario se despida" in prompt
    assert "hilo conversacional abierto" in prompt


def test_guide_prompt_forbids_farewell():
    """El prompt de guía prohíbe cerrar con frases de despedida."""
    prompt = load_guide_prompt().lower()
    assert "no cierres la respuesta con frases de despedida" in prompt
    assert "hilo conversacional abierto" in prompt


def test_recommendation_prompt_forbids_duplicate_and_farewell():
    """El prompt de recomendación prohíbe saludo duplicado y despedida prematura."""
    prompt = load_recommendation_prompt().lower()
    assert "no saludes de nuevo" in prompt
    assert "no cierres la respuesta con frases de despedida" in prompt


# --- El historial se inyecta en el prompt de smalltalk ------------------------


def test_generate_smalltalk_formats_history_in_prompt(monkeypatch):
    """``generate_smalltalk`` pasa el historial al prompt (US-028).

    Verifica que la plantilla de smalltalk expone un placeholder ``{history}``
    que recibe el historial enmascarado del nodo.
    """
    import app.graph.nodes.llm_response_node as node_module

    # La plantilla debe contener el placeholder {history}.
    raw = load_smalltalk_prompt()
    assert "{history}" in raw

    # El nodo pasa el historial (ventana enmascarada) a generate_smalltalk.
    history = [
        {"role": "user", "content": "hola"},
        {"role": "assistant", "content": "¡Hola! ¿En qué puedo ayudarte?"},
    ]

    received: dict = {}

    async def fake_smalltalk(message, history_text=""):
        received["message"] = message
        received["history_text"] = history_text
        return "Perfecto, sigamos con tu consulta."

    monkeypatch.setattr(node_module.llm_client, "generate_smalltalk", fake_smalltalk)
    monkeypatch.setattr(node_module, "mask_message", lambda text, uid: text)

    state = _normalize(
        {
            "message": "hoy te quiero pedir un favor",
            "intent": "other",
            "history": history,
            "user_id": "user-1",
        }
    )
    import asyncio

    result = asyncio.run(node_module.llm_response_node(state))
    assert received["message"] == "hoy te quiero pedir un favor"
    # El historial se pasa (enmascarado) para evitar saludo duplicado.
    assert "hola" in received["history_text"]
    assert "¿En qué puedo ayudarte?" in received["history_text"]
    assert result.response == "Perfecto, sigamos con tu consulta."
