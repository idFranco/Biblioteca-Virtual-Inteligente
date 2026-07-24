# Chatbot Rules (Python / LangGraph / LangChain)

## Architectural Constraints
- The chatbot must be implemented as a LangGraph graph.
- Do not implement the assistant as a single linear prompt.
- Every user message must be audited by Security-Audit-MCP before being processed by the graph.
- Every chatbot response must be audited by Security-Audit-MCP before being sent to the frontend.
- If input is flagged as unsafe, return a safe blocking response instead of continuing the graph.
- If output is flagged as unsafe, sanitize it through Security-Audit-MCP before responding.
- Always load user reading state before recommendation.
- Always check availability before recommending a rentable book.
- Use persistent memory from SQLite through Biblioteca-MCP.
- Use conversational memory only for short-term session context.
- Do not hallucinate stock or rental state.
- If MCP is unavailable, return a graceful fallback response.
- Do not expose internal tool errors to the user.
- Do not log raw secrets, tokens or passwords in audit events.
- Implement and propagate a X-Correlation-ID header across all HTTP requests (Frontend -> Backend -> Chatbot -> LLM) to trace transactions end-to-end in logs.
- Explicitly mask or redact Personally Identifiable Information (PII) such as emails, real names, or exact locations before sending context to the external LLM provider.

## LangGraph Required Nodes
- `audit_input_node`
- `load_user_state`
- `route_by_state`
- `due_reminder_node`
- `overdue_node`
- `feedback_node`
- `save_feedback_node`
- `classify_intent_node`
- `preferences_node`
- `internal_catalog_node`
- `external_enrichment_node`
- `availability_node`
- `response_node`
- `audit_output_node`
- `sanitize_response_node`
- `block_response_node`

## LangGraph Reading States
`sin_actividad`, `en_curso`, `por_vencer`, `vencido`, `recien_devuelto`

## Code Conventions (Python)
- Use type hints.
- Use Pydantic schemas.
- Keep graph state typed.
- Keep LangGraph nodes small.
- Do not place all chatbot logic in `main.py`.
- MCP clients must be isolated.
- Prompts must live in `prompts/`.
- Tool errors must be handled gracefully.

## Testing Rules
- Test graph routing.
- Test states (sin_actividad, en_curso, etc).
- Test fallback when MCP fails.
- Test blocking behavior for malicious or unsafe input.
- Test sanitization behavior for unsafe output.

## Forbidden Actions
- Do not read, search, or modify `__pycache__/`, `.venv/` or `.pytest_cache/`.
- Do not implement chatbot without LangGraph.
- Do not bypass `Security-Audit-MCP` input/output checks.
