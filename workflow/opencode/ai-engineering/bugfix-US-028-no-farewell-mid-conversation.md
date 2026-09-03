# Iteration Log — bugfix/US-028-no-farewell-mid-conversation

## 2026-09-03 — qa-check US-028 → PASS

- **Story:** US-028 — Corregir saludos duplicados y despedidas prematuras del chatbot y limpiar/crear documentación README.
- **Verdicto global:** PASS — todos los criterios de aceptación y la limpieza/creación de documentación pasan con evidencia.
- **Criterios de aceptación:**
  - AC#1 Saludo en medio de conversación NO genera "hola de nuevo" — ✅ PASS
  - AC#2 Recomendación NO contiene frases de despedida — ✅ PASS
  - AC#3 Guidance NO contiene frases de despedida — ✅ PASS
  - AC#4 Despedida explícita sigue generando cierre cortés — ✅ PASS (regresión `test_farewell_still_close_regression`)
  - AC#5 Historial conversacional se pasa al LLM — ✅ PASS
- **Documentación (Parte B):** ✅ `## Tests` eliminado de chatbot/backend/MCP READMEs; `## 11. Notas de versiones recientes` eliminado del README raíz (renumerado CI/CD a 11); `workflow/database/README.md` creado; fila `Database` añadida a la tabla de documentación del README raíz.
- **Causa raíz corregida:** `generate_smalltalk()` no recibía historial (LLM saludaba de nuevo) y los prompts no prohibían despedidas prematuras. Solución: reglas 6/7 en smalltalk, regla 6 en guide, reglas 8/9 en recommendation, `generate_smalltalk(user_message, history_text="")` con inyección de historial enmascarado, y `llm_response_node.py` pasa `_history_window(state)`.
- **Pruebas ejecutadas:** chatbot **188 passed, 1 deselected** (5 nuevos en `test_no_farewell_mid_conversation.py`) · biblioteca-mcp **15 passed** · open-library-mcp **18 passed** · security-audit-mcp **77 passed** · `dotnet build` backend OK · `dotnet test` **13 passed**.
- **Documentation Gate:** cumplido — `## Implementation Notes` y `## QA Result` en US-028.md; limpieza/creación de READMEs verificada.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
