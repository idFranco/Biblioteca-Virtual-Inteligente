# Iteration Log — bugfix/US-026-fluid-chatbot-e2e

## 2026-09-02 — qa-check US-026 → PASS

- **Story:** US-026 — Corregir la guía conversacional del chatbot para lograr conversaciones fluidas y añadir una prueba e2e con las credenciales del `.env`.
- **Rama:** `bugfix/US-026-conversacion-fluid-chatbot-e2e`.
- **Causa raíz:** `workflow/chatbot/app/prompts/smalltalk_prompt.txt` solo tenía una regla de cierre (despedida/agradecimiento, Regla 4) y ninguna de saludo; el LLM cerraba la conversación ante un simple "hola". El fallback `_greeting_fallback()` en `llm_response_node.py` era correcto pero solo se alcanzaba si el LLM devolvía `None`.
- **Fix:** Regla 5 (saludo mantiene el hilo conversacional ABIERTO: saludar de vuelta, presentarse, terminar con pregunta/invitación, nunca despedirse) + bloque discriminador saludo-vs-despedida; se preservó la Regla 4 (cierre cortés). Sin cambios de nodos/ruteo/grafo.
- **Veredicto global:** PASS — los 4 criterios de aceptación + el escenario e2e con credenciales del `.env` pasan.
- **Criterios de aceptación:**
  - AC#1 Saludo de un solo turno abre la conversación (no la cierra) — ✅ PASS (e2e en vivo + guard determinista)
  - AC#2 Continuidad multi-turno mantiene el hilo (mismo conversationId, no reinicia ni repite saludo) — ✅ PASS (e2e)
  - AC#3 Saludo se clasifica como smalltalk, no busca catálogo — ✅ PASS (unit: `intent=="other"`, sin `buscar_libros`/`generate_recommendation`)
  - AC#4 Despedida y agradecimiento conservan cierre cortés — ✅ PASS (regresión)
  - E2E con credenciales del `.env` — ✅ PASS (login + "hola" + seguimiento, 1 passed en 23.07s)
- **Evidencia clave:**
  - `test_smalltalk_guidance.py` → **6 passed**: `test_smalltalk_prompt_has_open_greeting_rule`, `test_smalltalk_prompt_distinguishes_farewell_close`, `test_smalltalk_prompt_has_keep_open_phrasing`, `test_greeting_open_response_via_graph`, `test_greeting_response_is_conversational_not_farewell`, `test_farewell_still_close_regression`.
  - Suite chatbot completa `-m "not e2e"` → **162 passed, 1 deselected** (sin regresión).
  - **e2e en vivo** (`test_e2e_conversation.py`, marker `e2e`): con el stack `docker compose up -d --build backend chatbot` (backend Healthy, chatbot `/health` 200, Ollama local disponible), login `POST http://localhost:5000/api/auth/login` con credenciales del `.env` → 200 (JWT + `user.id`); `POST http://localhost:8000/chat` con `message="hola"` → respuesta abierta sin marcadores de despedida; seguimiento en el mismo `conversationId` → hilo continuo (`conversation_id` idéntico). **1 passed en 23.07s.**
  - Credenciales leídas SOLO desde variables de entorno (`.env`), nunca hardcodeadas; sin loguear contraseña ni JWT.
- **Pruebas ejecutadas:** pytest unit/regresión (162+6 greens) · e2e live con stack completo (1 passed) · `docker compose up -d --build backend chatbot` OK.
- **Documentation Gate:** cumplido — `## QA Result` documentado en `US-026.md` (reemplazado `Pending`; `## Implementation Notes` verificadas y no modificadas); README del chatbot ya actualizado en implementación.
- **Riesgo residual (no bloqueante):** salida LLM no determinista; mitigado por el guard determinista del prompt y el fallback `_greeting_fallback()` que garantiza respuesta abierta ante un saludo incluso si el LLM fallara en aplicar la regla 5.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
