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
