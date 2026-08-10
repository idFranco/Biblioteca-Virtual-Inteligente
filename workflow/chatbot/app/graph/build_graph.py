from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.state import ChatState
from app.graph.nodes.audit_input_node import audit_input_node
from app.graph.nodes.audit_output_node import audit_output_node
from app.graph.nodes.availability_node import availability_node
from app.graph.nodes.block_response_node import block_response_node
from app.graph.nodes.classify_intent_node import classify_intent_node
from app.graph.nodes.external_enrichment_node import external_enrichment_node
from app.graph.nodes.internal_catalog_node import internal_catalog_node
from app.graph.nodes.load_user_state_node import load_user_state_node
from app.graph.nodes.response_node import response_node
from app.graph.nodes.sanitize_response_node import sanitize_response_node


def _route_intent(state: ChatState) -> str:
    return "blocked" if state.blocked else "process"


def _route_output(state: ChatState) -> str:
    return "sanitize" if state.sanitized else END


def build_graph():
    """Construye el grafo LangGraph del chatbot (flujo mínimo de US-009)."""
    workflow = StateGraph(ChatState)

    workflow.add_node("audit_input", audit_input_node)
    workflow.add_node("block_response", block_response_node)
    workflow.add_node("load_user_state", load_user_state_node)
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("internal_catalog", internal_catalog_node)
    workflow.add_node("external_enrichment", external_enrichment_node)
    workflow.add_node("availability", availability_node)
    workflow.add_node("response", response_node)
    workflow.add_node("audit_output", audit_output_node)
    workflow.add_node("sanitize_response", sanitize_response_node)

    workflow.add_edge(START, "audit_input")
    workflow.add_conditional_edges(
        "audit_input",
        _route_intent,
        {"blocked": "block_response", "process": "load_user_state"},
    )
    workflow.add_edge("block_response", "audit_output")
    workflow.add_edge("load_user_state", "classify_intent")
    workflow.add_edge("classify_intent", "internal_catalog")
    workflow.add_edge("internal_catalog", "external_enrichment")
    workflow.add_edge("external_enrichment", "availability")
    workflow.add_edge("availability", "response")
    workflow.add_edge("response", "audit_output")
    workflow.add_conditional_edges(
        "audit_output",
        _route_output,
        {"sanitize": "sanitize_response", END: END},
    )
    workflow.add_edge("sanitize_response", END)

    return workflow.compile()


graph = build_graph()
