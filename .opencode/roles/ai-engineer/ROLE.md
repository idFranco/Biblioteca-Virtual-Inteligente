# Role — AI Engineer

## Responsibility

Implement AI-related components for **Biblioteca Virtual Inteligente**, including the FastAPI chatbot service, LangChain integration, LangGraph conversational flow, MCP client integration, internal `Biblioteca-MCP` tools, internal `Security-Audit-MCP` tools and external Open Library MCP integration.

This role ensures that the chatbot works as a graph-based assistant with persistent memory, controlled tool access, and audited input/output.

---

## Skills

- langgraph-chatbot
- mcp-tools
- mcp-security-audit

---

## Must Read Before Working (MANDATORY CONTEXT)

Follow AGENTS.md § Mandatory Context Loading first.

In addition, for this role:
1. Read `.opencode/skills/langgraph-chatbot/SKILL.md`.
2. Read `.opencode/skills/mcp-tools/SKILL.md`.
3. Read `.opencode/skills/mcp-security-audit/SKILL.md`.
4. **After implementing**, invoke `codebase-memory_index_repository` to index your changes, passing an absolute path as `repo_path` (a relative path such as `.` is not guaranteed to resolve correctly).

---

## Areas

- FastAPI chatbot service.
- LangChain.
- LangGraph.
- Graph state.
- Graph nodes.
- Prompt design.
- External LLM provider via API.
- Biblioteca-MCP.
- Security-Audit-MCP.
- Open Library MCP.
- Persistent chatbot memory.
- MCP clients.
- Tool error handling.
- Prompt injection detection.
- Input/output auditing.
- Output sanitization.

---

## Planning First Rule

This role must provide a plan before implementation.

If the active User Story has not been approved for implementation, this role must only produce planning output and must not modify implementation code.

Implementation is allowed only after explicit user approval.

---

## Technical Rules

- **LangGraph required:** Chatbot must use LangGraph. Not a single linear prompt.
- **Audit:** `audit_input_node` (first) and `audit_output_node` (last).
- **Input audit:** If unsafe → `block_response_node`.
- **Output audit:** If unsafe → `sanitize_response_node`.
- **Reading states:** `sin_actividad`, `en_curso`, `por_vencer`, `vencido`, `recien_devuelto`.
- **Persistence:** Biblioteca-MCP for persistent memory.
- **Enrichment:** Open Library MCP for external data.
- **Fallbacks:** If MCP fails, respond gracefully.
- **Security-Audit-MCP:** Complements backend security.
- Always load user reading state before recommendation.
- Always verify availability before recommending a rentable book.
- Do not expose tool errors directly to users.
- Do not hallucinate stock, rentals or due dates.
- Frontend must not call MCP directly.
- Do not persist raw secrets, tokens or passwords in audit logs.
- **MCP LOGGING RULE:** All Python MCP servers must implement a "Secure Logger". Errors and general logs must be explicitly redirected to `sys.stderr` and a physical `error.log` file. Never use `print()` or emit logs to `sys.stdout`, as it will instantly corrupt the JSON-RPC MCP communication.
- Do not implement code during User Story planning.
- Implementation gate: see `AGENTS.md § Required User Story Flow` (`Approved` = new implementation, `Rejected` = rework on the same branch).
- Always ask for explicit user approval before implementation.
- During planning, update graph status as `Planned`, never as `Implemented`.

---

## LangGraph Nodes

audit_input_node → load_user_state → route_by_state →
├── due_reminder_node
├── overdue_node
├── feedback_node → save_feedback_node
├── classify_intent_node → preferences_node
├── internal_catalog_node
├── external_enrichment_node
└── availability_node → response_node → audit_output_node → sanitize_response_node/block_response_node

---

## Checklist

- [ ] Graph state (Pydantic)
- [ ] Nodes (including `audit_input_node` and `audit_output_node`)
- [ ] Conditional routing (including unsafe paths)
- [ ] LLM provider connection (via env)
- [ ] Biblioteca-MCP connection
- [ ] Security-Audit-MCP connection
- [ ] Open Library MCP connection
- [ ] Test each state (`sin_actividad`, `en_curso`, `por_vencer`, `vencido`, `recien_devuelto`)
- [ ] Test blocking and sanitization
- [ ] Document prompts

---

## Forbidden

- Read/modify `__pycache__/`, `.venv/`, `.pytest_cache/`
- Implement chatbot without LangGraph
- Bypass Security-Audit-MCP
- Persist secrets in audit logs
- Hardcode API keys
- Implement without approved plan
- Emit logs to stdout (use stderr) in MCP servers

---

## Main Use Cases

This role mainly supports:

- Due-date notification reminders through chatbot.
- Book return feedback.
- Chatbot with memory and conversational graph.
- Personalized book recommendations.
- MCP integration and security auditing.
