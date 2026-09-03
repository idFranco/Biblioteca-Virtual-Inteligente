# Iteration Log — bugfix/US-029-no-pii-leak-output-audit

## 2026-09-03 — implement US-029

- **Story:** US-029 — Eliminar leak de PII/tool-repr en el estado de lectura y reforzar la auditoría de salida de Security-Audit-MCP (detección de UUID + fail-closed).

### Part 1 — Leak de estado de lectura (no PII / tool-repr)
- **Causa raíz:** `get_estado_lectura` hacía `str(result)` cuando `result` no era `dict`, devolviendo la serialización cruda del `CallToolResult` (con `user_id`); `response_node` interpelaba `state.reading_state` verbatim.
- **Fix:**
  - `biblioteca_client._extract_estado(result)` extrae SOLO el valor `estado` desde `dict`, `str`-JSON o `repr` de MCP (con JSON/literal embebido); nunca devuelve la repr cruda.
  - `response_node._reading_state_text` interpola estados whitelisteados con etiqueta legible («en curso», «por vencer»…) y usa un fallback genérico ante valores inesperados.

### Part 2 — Security-Audit-MCP detecta UUID/PII en salida
- `local_audit.py`: se añadió patrón **UUID** a `_SENSITIVE_PATTERNS` (marcador `uuid`) y `sanitize_local` lo enmascara como `[ID]`.
- `groq_audit.py`: `_SENSITIVE_SYSTEM` y `_SANITIZE_SYSTEM` incluyen explícitamente los UUIDs del usuario (`user_id`) como PII.

### Part 3 — Fail-closed coherente de auditoría
- `security_audit_client._as_dict`: ya no devuelve `{"safe": True}` por defecto para respuestas no parseables → lanza `ValueError`.
- `audit_output_node`: ante fallo del MCP → `state.sanitized = True` (fuerza sanitización local `mask_pii`, que enmascara UUIDs → `[ID]`).
- `audit_input_node`: ante fallo del MCP → detección local determinista de credenciales/inyección y bloqueo si es malicioso (fail-closed).

### Pruebas
- Chatbot (`-m "not e2e"`): **201 passed, 1 deselected** (nuevos `test_estado_lectura_no_leak.py` y `test_audit_fail_closed.py`; actualizado `test_reading_state_loaded` a la etiqueta legible).
- Biblioteca-MCP: **15 passed** · Open-Library-MCP: **18 passed** · Security-Audit-MCP: **80 passed**.
- Backend: `dotnet build` 0 warnings/0 errors; `dotnet test` **13 passed**.

### Documentación
- `workflow/chatbot/README.md`: nodos `audit_input`/`load_user_state`/`response`/`audit_output`/`sanitize_response` actualizados (fail-closed + no-leak de estado).
- `workflow/mcp/README.md`: Security-Audit-MCP documenta detección de UUID y enmascaramiento `[ID]`.
- Log de iteración: este archivo.

### Siguiente paso
- Actualizar `## Implementation Notes` y `## QA Result` en US-029.md, avanzar a `Implemented`/`Validated` y crear el PR vía GitHub MCP.