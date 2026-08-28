from __future__ import annotations

import os
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.graph.state import ChatState
from app.graph.nodes.audit_input_node import audit_input_node
from app.graph.nodes.audit_output_node import audit_output_node
from app.graph.nodes.availability_node import availability_node
from app.graph.nodes.block_response_node import block_response_node
from app.graph.nodes.classify_intent_node import classify_intent_node
from app.graph.nodes.external_enrichment_node import external_enrichment_node
from app.graph.nodes.extract_query_node import extract_query_node
from app.graph.nodes.feedback_node import feedback_node
from app.graph.nodes.follow_up_node import follow_up_node
from app.graph.nodes.internal_catalog_node import internal_catalog_node
from app.graph.nodes.llm_response_node import llm_response_node
from app.graph.nodes.load_user_state_node import load_user_state_node
from app.graph.nodes.due_reminder_node import due_reminder_node
from app.graph.nodes.overdue_node import overdue_node
from app.graph.nodes.preferences_node import preferences_node
from app.graph.nodes.record_turn_node import record_turn_node
from app.graph.nodes.reset_turn_node import reset_turn_node
from app.graph.nodes.response_node import response_node
from app.graph.nodes.route_by_state import route_by_state
from app.graph.nodes.save_feedback_node import save_feedback_node
from app.graph.nodes.sanitize_response_node import sanitize_response_node


def _build_checkpointer() -> Any:
    """Construye el checkpointer del grafo (memoria conversacional).

    Prioridad:
    1. ``InMemorySaver`` cuando ``CHAT_MEMORY_DB_PATH`` está definida: habilita
       la memoria por sesión (``thread_id``) conservando el historial a lo largo
       de la conversación. Se usa un saver en-memoria en lugar de
       ``AsyncSqliteSaver`` porque su construcción es sincrónica y no exige un
       bucle de eventos en tiempo de import.
    2. ``False`` (sin checkpointer) en dev/tests sin la variable, para conservar
       los arranques que no exigen ``thread_id`` (comportamiento previo).

    Returns:
        Checkpointer de LangGraph (InMemorySaver) o ``False``.
    """
    if not os.getenv("CHAT_MEMORY_DB_PATH", "").strip():
        return False
    from langgraph.checkpoint.memory import InMemorySaver
    return InMemorySaver()


def _route_intent(state: ChatState) -> str:
    return "blocked" if state.blocked else "process"


def _route_output(state: ChatState) -> str:
    return "sanitize" if state.sanitized else "record"


def build_graph():
    """Construye el grafo LangGraph del chatbot (flujo US-012 + US-019).

    Auditoría obligatoria: Security-Audit-MCP antes (audit_input) y después
    (audit_output) de procesar. Memoria conversacional: el turno nuevo comienza
    en ``reset_turn`` (limpia transitorios + registra el mensaje user) y
    termina en ``record_turn`` (registra la respuesta assistant). Recomendación
    personalizada por historial/preferencias con validación cruzada Open
    Library.
    """
    workflow = StateGraph(ChatState)

    workflow.add_node("reset_turn", reset_turn_node)
    workflow.add_node("audit_input", audit_input_node)
    workflow.add_node("block_response", block_response_node)
    workflow.add_node("load_user_state", load_user_state_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("preferences", preferences_node)
    workflow.add_node("extract_query", extract_query_node)
    workflow.add_node("internal_catalog", internal_catalog_node)
    workflow.add_node("external_enrichment", external_enrichment_node)
    workflow.add_node("availability", availability_node)
    workflow.add_node("response", response_node)
    workflow.add_node("llm_response", llm_response_node)
    workflow.add_node("due_reminder", due_reminder_node)
    workflow.add_node("overdue", overdue_node)
    workflow.add_node("feedback", feedback_node)
    workflow.add_node("follow_up", follow_up_node)
    workflow.add_node("save_feedback", save_feedback_node)
    workflow.add_node("audit_output", audit_output_node)
    workflow.add_node("sanitize_response", sanitize_response_node)
    workflow.add_node("record_turn", record_turn_node)

    workflow.add_edge(START, "reset_turn")
    workflow.add_edge("reset_turn", "audit_input")
    workflow.add_conditional_edges(
        "audit_input",
        _route_intent,
        {"blocked": "block_response", "process": "load_user_state"},
    )
    workflow.add_edge("block_response", "audit_output")
    workflow.add_edge("load_user_state", "classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        route_by_state,
        {
            "recommendation": "preferences",
            "due_reminder": "due_reminder",
            "overdue": "overdue",
            "status_plain": "response",
            "feedback": "feedback",
            "follow_up": "follow_up",
            "book_query": "extract_query",
            "other": "response",
        },
    )

    workflow.add_edge("preferences", "internal_catalog")
    workflow.add_edge("due_reminder", "audit_output")
    workflow.add_edge("overdue", "audit_output")
    workflow.add_edge("feedback", "save_feedback")
    workflow.add_edge("save_feedback", "response")
    workflow.add_edge("follow_up", "llm_response")

    workflow.add_edge("extract_query", "internal_catalog")
    workflow.add_edge("internal_catalog", "external_enrichment")
    workflow.add_edge("external_enrichment", "availability")
    workflow.add_edge("availability", "response")
    workflow.add_edge("response", "llm_response")
    workflow.add_edge("llm_response", "audit_output")

    workflow.add_conditional_edges(
        "audit_output",
        _route_output,
        {"sanitize": "sanitize_response", "record": "record_turn"},
    )
    workflow.add_edge("sanitize_response", "record_turn")
    workflow.add_edge("record_turn", END)

    workflow = workflow.compile(checkpointer=_build_checkpointer())
    return workflow


graph = build_graph()
