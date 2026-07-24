# Skill Langgraph ChatBot

## Purpose

Use this skill for implementing the chatbot with LangChain and LangGraph.

## Rules

- The assistant must use LangGraph.
- Do not implement a single prompt-only chatbot.
- Audit every user message with `Security-Audit-MCP` before processing it.
- Audit every generated response with `Security-Audit-MCP` before returning it.
- Block the response gracefully if input is flagged as unsafe.
- Sanitize the response if output is flagged as unsafe.
- Always load user state first.
- Always verify availability before recommending a rentable book.
- Use MCP tools for internal data.
- Use external MCP for bibliographic enrichment.
- Use persistent memory through Biblioteca-MCP.
- Handle MCP failures gracefully.

## Required Graph Nodes

audit_input_node
load_user_state
route_by_state
due_reminder_node
overdue_node
feedback_node
save_feedback_node
classify_intent_node
preferences_node
internal_catalog_node
external_enrichment_node
availability_node
response_node
audit_output_node
sanitize_response_node
block_response_node

## Required States

sin_actividad
en_curso
por_vencer
vencido
recien_devuelto

## Checklist

1. Define graph state.
2. Implement nodes, including `audit_input_node` and `audit_output_node`.
3. Implement conditional routing, including safe/unsafe branches.
4. Connect LLM provider.
5. Connect Biblioteca-MCP.
6. Connect Security-Audit-MCP.
7. Connect external MCP.
8. Test each state.
9. Test blocking and sanitization paths.
10. Document prompts.
