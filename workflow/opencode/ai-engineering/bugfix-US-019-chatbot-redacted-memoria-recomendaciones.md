# Iteration Log — bugfix/US-019-chatbot-redacted-memoria-recomendaciones

## 2026-08-28 — qa-check US-019 (2º run) → REJECTED

- **Story:** US-019 — Corregir respuestas [REDACTED] del chatbot, restaurar memoria conversacional y validar recomendaciones cruzando catálogo local con Open Library.
- **Verdicto global:** REJECTED (1 criterio de aceptación falla).
- **Criterios de aceptación:**
  - AC#1 Auditoría degradada no redacta toda la salida — ✅ PASS
  - AC#2 PII enmascarado por segmentos — ✅ PASS
  - AC#3 Inyección real bloqueada con auditoría degradada — ✅ PASS
  - AC#4 Memoria conversacional entre turnos — ❌ FAIL (respuesta del turno 2 «cuéntame más sobre la primera» no refleja la recomendación previa)
  - AC#5 Aislamiento de sesiones — ✅ PASS
  - AC#6 Recomendación validada contra ambas fuentes — ✅ PASS
  - AC#7 Sugerencias externas solicitables — ✅ PASS
  - AC#8 Saludo conversacional (smalltalk) — ✅ PASS
- **Evidencia del fallo:** simulación E2E del grafo (2 turnos, mismo `thread_id`/`conversationId`, MCP mockeados, LLM caído). Turno 1 recomienda «El Nombre del Viento». Turno 2 responde «No hemos encontrado «este libro» en nuestro catálogo por el momento…». `llm_response_node.py:55` corta todo intent distinto de `recommendation`/`other`; `"cuéntame más sobre la primera"` se clasifica `book_query`.
- **Pruebas ejecutadas:** chatbot 78 passed · security-audit-mcp 17 passed · biblioteca-mcp 12 passed · open-library-mcp 18 passed · `npm run build` frontend OK.
- **Documentation Gate:** parcial — `## Implementation Notes` completa, pero ADR-034/035 ausentes en `DECISIONS.md` (llega hasta ADR-033).
- **Siguiente paso:** `implement-user-story US-019` (rework en el mismo branch) y re-ejecutar `qa-check US-019` desde el inicio.

## 2026-08-29 — qa-check US-019 (3º run) → PASS

- **Verdicto global:** PASS — todos los criterios de aceptación pasan. Rework AC#4 implementado y Documentation Gate cumplido.
- **Criterios de aceptación:**
  - AC#1 Auditoría degradada no redacta toda la salida — ✅ PASS
  - AC#2 PII enmascarado por segmentos — ✅ PASS
  - AC#3 Inyección real bloqueada con auditoría degradada — ✅ PASS
  - AC#4 Memoria conversacional entre turnos — ✅ PASS (rework: intención `follow_up` + `follow_up_node` resuelven «la primera»/«la segunda»/«la última» y títulos citados contra el historial del turno anterior; `record_turn` incrusta lista compacta por whitelist; `main.py` reutiliza `conversationId`/`thread_id`)
  - AC#5 Aislamiento de sesiones — ✅ PASS
  - AC#6 Recomendación validada contra ambas fuentes — ✅ PASS
  - AC#7 Sugerencias externas solicitables — ✅ PASS
  - AC#8 Saludo conversacional (smalltalk) — ✅ PASS
- **Pruebas ejecutadas (2026-08-29):** chatbot **102 passed** (78 previas + 24 nuevas de `tests/test_follow_up.py`) · security-audit-mcp **17 passed** · biblioteca-mcp **12 passed** · open-library-mcp **18 passed** · `npm run build` frontend OK · `dotnet build` backend OK (regresivo, 0 warnings/errors).
- **Documentation Gate:** cumplido — ADR-034 (fallback local determinista con `degraded`, sanitización por segmentos) y ADR-035 (checkpointer `InMemorySaver` + resolución `follow_up`) registrados en `DECISIONS.md`; `workflow/chatbot/README.md`, `.env.example` y `docker-compose.yml` actualizados con `CHAT_MEMORY_DB_PATH`.
- **Observación no bloqueante:** `workflow/mcp/README.md` no detalla explícitamente el fallback local degradado de Security-Audit-MCP (cubierto por ADR-034 y el README del chatbot); no afecta a ningún criterio de aceptación.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
