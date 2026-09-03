from __future__ import annotations

from app.graph.state import ChatState
from app.llm.client import classify_intent
from app.graph.nodes.classify_intent_node import classify_intent_node


async def llm_classify_node(state: ChatState) -> ChatState:
    """Clasifica la intención con el LLM (US-027).

    Intenta clasificar con el LLM vía ``classify_intent``. Se ejecuta en
    try/except porque: si el LLM no está disponible, devuelve fallback seguro
    (other, [], 0.0), pero si la cadena lanza por cualquier motivo, también
    caemos al clasificador heurístico ``classify_intent_node`` sin colapsar el
    grafo (ADR-023, "handle MCP/LLM failures gracefully").

    "recomiendes" subjunctive bug: el clasificador heurístico ``_RECOMMENDATION_PATTERNS``
    no captura "recomiendes" (subjuntivo) lo que causaba book_query errada. El LLM
    es ahora la primera línea de clasificación y resuelve esa casuística.
    """
    try:
        intent, tools, confidence = await classify_intent(
            message=state.message,
            user_id=state.user_id,
            conversation_id=state.conversation_id,
            history=state.history,
        )
    except Exception:  # noqa: BLE001 - fallback elegante (ADR-023)
        intent, tools, confidence = "other", [], 0.0

    if intent != "other" or confidence > 0.0:
        state.intent = intent
        state.classification_confidence = confidence
        state.suggested_tools = tools
        state.llm_used = True
        return state

    # Fallback heurístico.
    state = await classify_intent_node(state)
    state.classification_confidence = 0.0
    state.suggested_tools = []
    state.llm_used = False
    return state
