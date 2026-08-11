# AI Engineering — Bitácora de iteración — US-009 (rama `feature/US-009-catalog-enrichment`)

## Iteración 1 — Implementación inicial (2026-08-10)

- Story `Draft → Approved`; rama `feature/US-009-catalog-enrichment`.
- Backend: `BookRequest` + `BookRequestStatus`, `Book.OpenLibraryKey`, Commands/Queries/Handlers/Validators (CQRS Dispatcher), policies `books.request`/`books.manage`, seed de RoleClaims, `BookRequestsController`.
- Frontend: `services/bookRequests.ts`, `GestionLibroPage`, `ChatWidget` con solicitud de copia, ruta `/admin/gestion-libro` con `PermissionGuard`, Header condicional.
- Chatbot: grafo LangGraph con `extract_query`/`internal_catalog`/`external_enrichment`/`availability`, cliente Open Library MCP con fallback (Bug 2), `action_offer`.
- MCP: `workflow/mcp/open-library-mcp/` (FastMCP) creado.
- Build backend OK (Docker SDK 10.0), pytest 12/12 (primera iteración), frontend build+lint OK.

## QA 1 (2026-08-10) — REJECTED

Hallazgos:
1. CRÍTICO — El grafo no produce `action_offer` en el flujo real (falta extracción del término de búsqueda: `external_enrichment_node`/`internal_catalog_node` usaban `state.message` completo).
2. ALTO — Security-Audit-MCP no bloquea prompt injection en español (patrones solo EN).

## Rework 1 (2026-08-10) — tras QA Rejected

- `extract_query_node` extrae título/autor del mensaje natural; `internal_catalog`/`external_enrichment` usan `state.query`.
- Detector ES/EN real en `workflow/mcp/security_audit_mcp/detector.py`; `server.py` pasa a `from fastmcp import FastMCP`; stdio hereda entorno completo.
- pytest **29/29**; smoke E2E real con los 3 MCP + Open Library OK.

## QA 2 (2026-08-10) — REJECTED

Hallazgo:
3. CRÍTICO — Ruta del API de solicitudes incompatible con el frontend (`[Route("api/[controller]")]` → `api/BookRequests`; el frontend usa `/api/book-requests`; el guion `-` rompía la coincidencia → 404).

## Rework 2 (2026-08-11) — Security-Audit-MCP basado en Groq LLM (petición del usuario)

- `server.py` pasa a auditoría LLM vía Groq (`API_KEY_GROQ`, modelo `llama-3.3-70b-versatile`, `httpx`); fallback seguro bloquea ante fallo/clave ausente.
- Nuevo `groq_audit.py` (`detect_injection`, `detect_sensitive`, `sanitize`).
- Deprecado el paquete `security_audit_mcp/`; `requirements.txt` + `httpx`; `docker-compose.yml` propaga `API_KEY_GROQ`; `.env.example` documenta.
- pytest **26/26** (test_security reescrito con `_groq_completion` fake).

## QA 3 (2026-08-11) — REJECTED

Hallazgo (heredado, no abarcado por Rework 2):
4. CRÍTICO — Ruta del API de solicitudes sigue incompatible (defecto #3 no resuelto): `api/BookRequests` vs `/api/book-requests` → 404.

## Rework 3 (2026-08-11) — Ruta del API corregida

- `BookRequestsController.cs`: `[Route("api/[controller]")]` → `[Route("api/book-requests")]` (kebab-case, coincide con frontend).
- Build backend con SDK 10.0.302 (instalado local en `/tmp/opencode/dotnet10`): **0 warnings / 0 errors**.

## QA 4 (2026-08-11) — APPROVED

- Smoke real (SDK 10.0.302, puerto 5099, BD `qa-bookrequests.db`): sin token todos los endpoints de solicitudes → **401** (ya NO 404). Flujo funcional con JWT: 201 crear, 409 duplicado, 400 sin título, 200 listar/filtrar/mine, 200 approve, 409 re-aprobar, 400 totalCopies 0, 404 id inexistente. Libro promovido visible en `GET /api/books?search=Cien` con `openLibraryKey: /works/OL274505W`, `availableCopies = totalCopies`.
- pytest **26/26**; backend build 0/0; frontend build OK (lint solo warning pre-existente `button.tsx`).
- `index_repository` OK (nodes 2135 / edges 4195).
- PR creado vía GitHub MCP; story → `Validated`.

## Cierre

- Story avanzada a `Validated` tras PR mergeable.
- Pendiente de actualización transversal: ADR-014/`opencode.json` (activar `open-library`) — confirmado conforme al plan técnico (ADR-014).
