# AI Engineering Log — feature-US-014-docs-config-env-ux

**Story:** US-014 — Optimización de documentación, configuración por variables de entorno y ajustes de UX (roles, alquiler y chatbot)

**Branch:** `feature/US-014-docs-config-env-ux` (creada desde `main` `78d01d3` vía GitHub MCP)

**Date:** 2026-08-19

## Roles participantes

| Role | Participación |
|---|---|
| Functional Analyst | Alcance funcional y criterios de aceptación (5 frentes R1–R5) |
| Architect | Política fail-fast (extensión ADR-016), ADR-025/026/027 |
| Technical Lead | Plan consolidado D1–D6 |
| Backend Developer | D2 — config fail-fast + seed autoritativo |
| Frontend Developer | D3 — UX admin/alquiler/chatbot + env fail-fast |
| AI Engineer | D4 — chatbot/MCP env requeridas |
| QA | Validación de builds, fail-fast, permisos por rol, tests Python, docker compose config |
| Technical Writer | D6 — README raíz índice, READMEs de módulo, ADRs, bitácora |

## Iteración 1 — Implementación

### Cambios ejecutados (resumen)

**Backend:**
- `Infrastructure/Common/ConfigurationExtensions.cs`: `GetRequiredInt` añadido.
- `WebAPI/Program.cs`: `GetRequiredString("SQLITE_DATA_SOURCE")` (sin fallback), `Jwt:Issuer/Audience`, `Cors:Origins`, `AUTH_RATE_LIMIT_PER_MINUTE` fail-fast; `ResolveLocalSqlitePath` acepta ruta o connection string; seed de roles autoritativo (Admin sin `rentals.create`/`rentals.view_own`).
- `appsettings.json`/`.Development.json`/`.Production.json`: literales de configuración eliminados (clave dev JWT incluida).
- `Infrastructure/Data/Seed/CatalogSeeder.cs` y `Infrastructure/Services/RentalDueNotificationService.cs`: lecturas requeridas sin defaults en código (baseline no sensible en appsettings).
- `workflow/backend/README.md` creado.

**Frontend:**
- `Header.tsx` / `GestionLibroPage.tsx`: «Solicitudes de libros».
- `CatalogPage.tsx` + `CreateRentalDialog`: botón «Alquilar» para usuario con `rentals.create` y libro disponible.
- `chatWidgetStore.ts` / `ChatWidget.tsx`: `isOpen` default `false` + botón flotante «Asistente de la Biblioteca».
- `config/env.ts` + `vite.config.ts`: fail-fast en build y bundle.
- `frontend/Dockerfile`: ARG sin defaults.
- `workflow/frontend/README.md` reescrito.

**Chatbot/MCP:**
- `chatbot/Dockerfile` sin ENV defaults.
- `mcp_clients/*.py` + `stdio.py`: `require_env` para los 3 comandos MCP.
- `app/llm/client.py`: `LLM_MODEL` requerida si `LLM_API_KEY` está definida.
- `mcp/common/settings.py`: `DATABASE_PATH` requerida; `mcp/common/sqlite.py` sin default.
- `security-audit-mcp/server.py`: `AUDIT_DATABASE_PATH` requerida.
- `workflow/chatbot/README.md` y `workflow/mcp/README.md` actualizados/creados.

**Docker Compose:**
- `docker-compose.yml` reescrito: sustitución `:?` obligatoria (sin `:-`); `LLM_API_KEY`/`LLM_MODEL` passthrough opcional (capacidad opt-in).

**Documentación:**
- `README.md` raíz reducido a índice.
- `.opencode/memory/DECISIONS.md`: ADR-025 (fail-fast), ADR-026 (documentación por módulo), ADR-027 (Admin sin alquiler + seed autoritativo).
- `US-014.md` actualizado con plan ejecutado y validación.

### Validación ejecutada

| # | Validación | Resultado |
|---|---|---|
| 1 | `dotnet build BibliotecaVirtual.slnx` | ✅ 0 errores, 0 warnings |
| 2 | Inicio backend sin env → fail-fast | ✅ Aborta nombrando `SQLITE_DATA_SOURCE` |
| 3 | Inicio backend con env → `/health` + seed 50 libros | ✅ 200 + 50 insertados |
| 4 | Admin: `POST /api/rentals` / `GET /api/rentals/mine` / `GET /api/rentals` | ✅ 403 / 403 / 200 |
| 5 | Claims de Admin en BD (reconciliación) | ✅ 10 claims sin `rentals.create`/`rentals.view_own` |
| 6 | Usuario: register/login → `POST /api/rentals` / `mine` | ✅ 200 / 201 / 200 |
| 7 | `npm run build` con env / sin env | ✅ OK / fail-fast en build-time |
| 8 | `npm run lint` | ✅ OK (warning preexistente en `ui/button.tsx`) |
| 9 | `pytest` chatbot (40) + MCP (25) | ✅ 65 passed |
| 10 | MCP fail-fast sin `DATABASE_PATH`/`AUDIT_DATABASE_PATH` | ✅ `RuntimeError` claro |
| 11 | LLM: sin clave → fallback; con clave sin modelo → error claro | ✅ Correcto |
| 12 | `docker compose config` con/sin env | ✅ OK / aborta con mensaje claro |

### Caveats

- **`.env.example` no editable por el agente** (reglas de permisos niegan `*.env.*`). Las variables nuevas (listadas en US-014.md → Implementation Notes D6) deben añadirse manualmente por el usuario.
- El primer smoke del backend con `SQLITE_DATA_SOURCE` como ruta desnuda fallaba al parsear el connection string; corregido en `ResolveLocalSqlitePath` (ahora construye `Data Source=...` para rutas).

## Estado

Implementación completa y validada. Pendiente: push de la rama vía GitHub MCP y avance a `Implemented`, luego `qa-check US-014`.