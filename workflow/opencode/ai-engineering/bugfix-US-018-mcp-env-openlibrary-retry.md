# Bitácora AI Engineering — US-018

- **Historia:** US-018 — Corregir arranque de MCP en contenedor y resiliencia de Open Library
- **Rama:** `bugfix/US-018-mcp-env-openlibrary-retry`
- **Fecha:** 2026-08-21
- **Estado MCP al cierre de implementación:** Implemented
- **Roles ejecutados:** technical-lead (coordinación), ai-engineer (compose + OL MCP + tests), technical-writer (.env.example, DECISIONS.md, bitácora). Backend/Frontend: no impactados.

## Objetivo

Que `docker compose up --build` funcione sin errores aunque el shell del host exporte rutas relativas de base de datos (precedencia shell > `.env`), y que open-library-mcp tolere fallos transitorios de red (`ConnectError` tras el build) con reintento y backoff.

## Diagnóstico previo (planificación)

- `biblioteca-mcp`/`security-audit-mcp` crasheaban con `FileNotFoundError` (`DATABASE_PATH='./workflow/database/BibliotecaVirtual.db'` llegaba al contenedor porque Compose resuelve `${VAR}` de `environment:` con prioridad del shell; el export legítimo de dev vive en `~/.bashrc:142`).
- `open-library-mcp` falló una vez con `ConnectError` justo tras el build; un solo intento con timeout de 10 s resultó frágil (host sin proxy, DNS OK, egres OK).

## Cambios realizados

| Archivo | Cambio |
|---|---|
| `docker-compose.yml` | Se eliminaron `DATABASE_PATH`/`AUDIT_DATABASE_PATH` del bloque `environment:` del chatbot y se añadió `env_file: [.env]` (lee disco, inmune al shell). Las demás claves conservan su fail-fast `:?` |
| `workflow/mcp/open-library-mcp/server.py` | `OPEN_LIBRARY_TIMEOUT` 10→12 s; nuevo `OPEN_LIBRARY_RETRIES` (default 1); `_get_json` reintenta solo `httpx.TransportError` con backoff fijo de 1 s; errores HTTP 4xx/5xx no se reintentan; `RuntimeError` estructurado intacto. Peor caso ≈25 s < cap de 30 s de `run_mcp_tool` |
| `workflow/mcp/open-library-mcp/tests/test_get_json_retry.py` | Nuevo: 5 tests (reintento exitoso, agotamiento de intentos, 500 sin reintento, reintento deshabilitado, E2E de `ol_search_books` recuperándose de un ConnectError) con `MockTransport`, sin red |
| `.env.example` | Retirado el workaround inline obsoleto (líneas 39–41) y documentado el mecanismo `env_file` (US-018/ADR-033) |
| `.opencode/memory/DECISIONS.md` | ADR-033 (env_file + retry), marcado el caveat operativo de ADR-032 como superseded |
| `workflow/opencode/user-stories/US-018.md` | Plan técnico consolidado, aprobación y notas de implementación |

## Commits

| Commit | Contenido |
|---|---|
| `e42b2cf` | `docs(US-018): plan técnico consolidado por roles y estado Planned` |
| *(push implementación vía GitHub MCP)* | `fix(US-018): resolver rutas DB desde .env vía env_file y reintentar fallos transitorios en Open Library MCP` |

## Evidencia de validación (implementación)

1. **Estático:** `docker compose config` con exports contaminantes activos (`DATABASE_PATH=./workflow/database/...`) resuelve igualmente `DATABASE_PATH: /app/database/BibliotecaVirtual.db` y `AUDIT_DATABASE_PATH: /app/database/audit.db`.
2. **OL MCP:** `pytest workflow/mcp/open-library-mcp/tests/ -q` → **18 passed** (13 existentes + 5 nuevos).
3. **Chatbot:** `pytest tests/ -q` desde `workflow/chatbot` → **61 passed**.
4. **Biblioteca MCP:** `pytest tests/ -q` → **12 passed**.
5. **Backend:** `dotnet build workflow/backend -v q` → 0 warnings, 0 errors.
6. **Frontend:** `npm run build` con las variables build-time requeridas (ADR-025) → built OK.
7. Pendiente de QA: arranque real del stack y E2E `/chat` (fase `qa-check`).

## Riesgos materializados

Ninguno. La advertencia teórica de doble carga de `.env` (auto-load + `env_file`) no apareció en `docker compose config`.
