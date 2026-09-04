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

## 2026-09-04 — qa-check US-029 → PASS

- **Branch:** `bugfix/US-029-no-pii-leak-output-audit`
- **Result:** PASS — todos los criterios de aceptación verificados.

### Validación de criterios
| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | `get_estado_lectura` extrae SOLO `estado` sin `user_id` ni `TextContent` | ✅ PASS | `test_estado_lectura_no_leak.py::test_extract_estado_from_calltoolresult_repr_no_leak` |
| 2 | `response_node` con `reading_state` inválido usa fallback genérico (sin leak) | ✅ PASS | `test_estado_lectura_no_leak.py::test_response_node_status_uses_fallback_for_raw_value` |
| 3 | `response_node` con estado válido muestra etiqueta legible («por vencer») | ✅ PASS | `test_estado_lectura_no_leak.py::test_response_node_status_uses_label_for_valid_state` |
| 4 | `detect_sensitive_local` detecta UUID en texto | ✅ PASS | `test_local_fallback.py::test_detect_sensitive_local_flags_uuid` |
| 5 | `sanitize_local` enmascara UUID con `[ID]` | ✅ PASS | `test_local_fallback.py::test_sanitize_local_masks_uuid_with_id_token` |
| 6 | `audit_output_node` exception → `sanitized=True` (fail-closed) | ✅ PASS | `test_audit_fail_closed.py::test_audit_output_node_fail_closed_forces_sanitize` |
| 7 | `audit_input_node` exception + credential pattern → `blocked=True` | ✅ PASS | `test_audit_fail_closed.py::test_audit_input_node_fail_closed_blocks_credential_request` |
| 8 | `_as_dict` raises on unparseable (no more `{"safe": True}` default) | ✅ PASS | `test_audit_fail_closed.py::test_as_dict_raises_on_unparseable_value` |
| 9 | Regresión: rechazos de email/user_id existentes siguen bloqueados | ✅ PASS | `test_credential_guard.py::test_*` (suite existente, 0 regressions) |
| 10 | Regresión: salidas legítimas no corruptas tras sanitización | ✅ PASS | `test_audit_fail_closed.py::test_audit_output_node_safe_state_not_flagged` |
| 11 | UUID en salida con Groq caído → `safe=False, degraded=True, reasons=["uuid"]` | ✅ PASS | `test_local_fallback.py::test_audit_model_output_degrada_flagged_by_local_uuid` |

### Suites de prueba
| Suite | Result |
|---|---|
| Chatbot (`pytest -m "not e2e"`) | **201 passed**, 1 deselected |
| Biblioteca-MCP | **15 passed** |
| Open-Library-MCP | **18 passed** |
| Security-Audit-MCP | **80 passed** |
| Backend (`dotnet build` + `dotnet test`) | **0 warnings, 0 errors, 13 passed** |

### PR
- PR #30: https://github.com/idFranco/Biblioteca-Virtual-Inteligente/pull/30