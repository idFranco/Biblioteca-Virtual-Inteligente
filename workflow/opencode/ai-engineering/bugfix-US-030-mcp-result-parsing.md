# Iteration Log — bugfix/US-030-mcp-result-parsing

## 2026-09-04 — implement US-030

- **Story:** US-030 — Corregir leak de repr raw de CallToolResult en el chatbot y reforzar la extracción de resultados MCP.
- **Branch:** `bugfix/US-030-mcp-result-parsing`

### Causa raíz
- `_parse_result()` en `app/mcp_clients/stdio.py` tenía `except AttributeError: return result`, devolviendo el objeto `CallToolResult` sin parsear cuando la extracción de texto fallaba. El SDK expone la respuesta ya parseada en `structured_content` (dict) que nunca se usaba.
- `sanitize_text()` en `app/mcp_clients/security_audit_client.py` caía en `return str(result)` cuando `result` no era `dict`, exponiendo el repr (`meta=None content=[TextContent(...)]`) en la respuesta al usuario.

### Fix
- `stdio.py::_parse_result`: prioriza `structured_content` (dict ya parseado), luego `json.loads` sobre el texto; elimina el `except AttributeError: return result` → un resultado inesperado lanza para que el llamador aplique su fallback (todos ya tienen try/except).
- `security_audit_client.py`: nuevo `_safe_text()` (patrón `_extract_estado` de US-029) extrae `safe_text`/`text` de `dict` o `str`-JSON; `sanitize_text()` devuelve el input original ante objetos inesperados, nunca el repr.

### Pruebas
- Chatbot (`pytest tests/`): **214 passed, 1 skipped** (18 tests nuevos: 10 en `test_stdio.py`, 8 en `test_security_client.py`).

### Documentación
- `workflow/opencode/user-stories/US-030.md`: descripción funcional, criterios de aceptación, plan técnico, riesgos y QA result.
- Log de iteración: este archivo.

### Siguiente paso
- Crear el PR vía GitHub MCP y, si es mergeable, avanzar la historia a `Validated`.

## 2026-09-04 — qa-check US-030 → PASS

- **Branch:** `bugfix/US-030-mcp-result-parsing`
- **Result:** PASS — todos los criterios de aceptación verificados.

### Validación de criterios
| # | Criterion | Status | Evidence |
|---|---|---|---|
| 1 | El chatbot responde texto limpio al saludar (sin `meta=` ni `TextContent`) | ✅ PASS | `test_security_client.py::test_sanitize_text_never_returns_raw_repr`, `test_sanitize_text_falls_back_to_input_on_non_dict` |
| 2 | `_parse_result` usa `structured_content` cuando está disponible | ✅ PASS | `test_stdio.py::test_parse_result_prefers_structured_content` |
| 3 | Nunca se expone la serialización cruda de un objeto MCP | ✅ PASS | `test_stdio.py::test_parse_result_never_returns_raw_object`, `test_security_client.py::test_safe_text_raw_object_returns_none` |

### Suite de prueba
| Suite | Result |
|---|---|
| Chatbot (`pytest tests/`) | **214 passed**, 1 skipped |

### PR
- PR #31: https://github.com/idFranco/Biblioteca-Virtual-Inteligente/pull/31
