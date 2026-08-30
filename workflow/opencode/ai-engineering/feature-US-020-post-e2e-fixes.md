# Iteration Log — feature/US-020-post-e2e-fixes

## 2026-08-30 — qa-check US-020 → PASS

- **Story:** US-020 — Resolver pendientes post-E2E (contrato `userId` case-insensitive, modelo GROQ final, smalltalk dedicado, limpieza E2E y propagación CI/Docker/docs).
- **Rama:** `feature/US-020-post-e2e-fixes`.
- **Verdicto global:** PASS — los 5 criterios de aceptación pasan.
- **Criterios de aceptación:**
  - AC#1 Contrato `userId` case-insensitive en Biblioteca-MCP — ✅ PASS
  - AC#2 GROQ final `openai/gpt-oss-20b` con `degraded:false`, sin `[REDACTED]` global — ✅ PASS
  - AC#3 Smalltalk con prompt dedicado, sin recomendaciones inventadas — ✅ PASS
  - AC#4 Bases runtime sin residuo E2E — ✅ PASS
  - AC#5 Propagación a CI/Docker/READMEs — ✅ PASS
- **Evidencia clave:**
  - AC#1: suite biblioteca-mcp 15 passed + consultas runtime UPPER/lower idénticas sobre la DB real (usuario Id `199C1335-823E-4890-AC18-64F5A7476918`).
  - AC#2: llamada GROQ live con `API_KEY_GROQ` → benigno `[]`, inyección intentada `['credential_request']`, sin excepción → `degraded:false`; suite security-audit-mcp 18 passed (regresión US-019).
  - AC#3: suite chatbot 103 passed; reproducción de grafo con `"gracias, que tengas un buen día"` → `intent=other`, respuesta cortés, `recommendations=[]`, catálogo NO consultado, sin `[REDACTED]`.
  - AC#4: `verify_cleanup.py` 10/10 PASS **sin ejecutar DELETEs** — el residuo E2E ya no existe en runtime (`AspNetUsers=1`, `Books=50`, 0 filas `e2e-*`/`test-*`, `foreign_key_check` limpio); el GATE humano del plan resultó innecesario y los scripts quedan como utilidad idempotente.
  - AC#5: docker compose config OK; `ci.yml` inyecta `GROQ_MODEL=openai/gpt-oss-20b`/`GROQ_TIMEOUT_SECONDS=10` en la suite security-audit-mcp; ADR-036/037 + READMEs + `.env.example` actualizados; sin secretos literales versionados.
- **Pruebas ejecutadas:** dotnet build 0/0 (regresivo) · npm run build OK · chatbot 103 passed · biblioteca-mcp 15 passed · security-audit-mcp 18 passed · open-library-mcp 18 passed · docker compose config OK.
- **Documentation Gate:** cumplido — `## QA Result` documentado en `US-020.md` (reemplazado el `Pending`; `## Implementation Notes` verificadas sin modificar), ADR-036/037 + READMEs ya actualizados por implementación.
- **Observación no bloqueante:** para el smalltalk LLM completo en runtime se requiere Ollama `:11434` levantado (prerequisito US-017); comportamiento AC#3 verificado por tests de grafo + fallback determinista.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.