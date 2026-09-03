# Iteration Log — feature/US-027-hybrid-chatbot-llm-classify

## 2026-09-03 — qa-check US-027 → PASS

- **Story:** US-027 — Arquitectura híbrida del chatbot: clasificación LLM + ejecución determinista de herramientas y unificación de seguridad en Security-Audit-MCP.
- **Rama:** `feature/US-027-hybrid-chatbot-llm-classify`.
- **Veredicto global:** PASS — los 6 criterios de aceptación pasan (validados con credenciales reales del `.env`).
- **Criterios de aceptación:**
  - AC#1 Clasificación natural por LLM — ✅ PASS (llama3.2 real): «Quisiera que me recomiendes libro de lecturra» → `recommendation` (conf ≥0.9), no `book_query`
  - AC#2 Fallback a regex cuando el LLM no está disponible — ✅ PASS (unit `test_llm_classify`: LLM `None`/conf 0 → regex mejorado, sin colapso)
  - AC#3 Credenciales unificadas en Security-Audit-MCP (ES+EN) — ✅ PASS (local bilingüe + GROQ key real)
  - AC#4 Sin falsos positivos de credenciales — ✅ PASS (token/sesión en contexto de libro no dispara)
  - AC#5 Ejecución determinista de herramientas — ✅ PASS (`tool_executor`; `suggested_tools` solo Biblioteca-MCP)
  - AC#6 Open Library permanece determinista — ✅ PASS (nunca en `suggested_tools` del LLM)
- **Conectividad real verificada (credenciales del `.env`):**
  - Ollama **llama3.2** en `localhost:11434` → HTTP 200 (chat completion real).
  - **API_KEY_GROQ** (real) → HTTP 200 (`openai/gpt-oss-20b`).
  - (Nota: el `.env` apunta `OLLAMA_BASE_URL` a `host.docker.internal`, hostname solo resolvable en Docker; en el host el endpoint equivalente es `localhost:11434`. El nombre de modelo `llama3.2` es el del `.env`.)
- **Evidencia clave:**
  - Suite chatbot `-m "not e2e"` → **183 passed, 1 deselected** (sin regresión).
  - Suite security-audit-mcp → **77 passed**.
  - Validación real contra .env: 4/4 clasificaciones LLM correctas; 7/7 peticiones de credenciales ES/EN detectadas por fallback local; 3/3 detectadas por GROQ real; 3/3 sin falsos positivos.
- **Documentation Gate:** cumplido — `## QA Result` documentado en `US-027.md` (reemplazado `Pending`; `## Implementation Notes` verificadas y no modificadas).
- **Riesgo residual (no bloqueante):** smoke E2E HTTP completo (stack backend+chatbot vía docker compose) no ejecutado en este entorno (servicios apagados / Docker no disponible); el alcance crítico de US-027 (clasificación LLM real + GROQ real + fallback local) sí se validó con credenciales reales del `.env`.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
