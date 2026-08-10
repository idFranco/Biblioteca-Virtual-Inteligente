# AI Engineering Log — bugfix-US-008-refactor-clean-code-use-var-global

## Iteración 1 — 2026-08-10 (implement + qa)

### Historia
**US-008** — Limpieza de código, validación de variables de entorno y actualización de imágenes Docker (estado al cerrar: Implemented → Validated).

### Alcance ejecutado
1. **Backend (A):** `ConfigurationExtensions.cs` (Infrastructure/Common) con `GetRequiredString` (fail-fast nombrando la env var, `Jwt:Key`→`Jwt__Key`), `GetString(key, default)`, `GetInt(key, default)`. Aplicado en `Program.cs` (JWT Key/Issuer/Audience/CORS/`AUTH_RATE_LIMIT_PER_MINUTE`) y `TokenService.cs` (`GetRequiredString`, `GetInt` ×2), preservando defaults `15`/`7`/`"BibliotecaVirtual"`/`"http://localhost:5173"`/`10`. `appsettings.Development.json` con dev-key; `appsettings.Production.json` creado.
2. **Frontend (B):** `src/config/env.ts` (`API_BASE_URL` default `http://localhost:5000`, corrige `:5002` roto); `src/vite-env.d.ts` con `ImportMetaEnv`; `api.ts`/`auth.ts` importan desde `@/config/env`.
3. **MCP (C):** `workflow/mcp/common/settings.py` (solo stdlib) con `get_database_path()` (vacío=no definido, relativo→repo root `parents[3]`, valida directorio padre, `lru_cache`, `clear_settings_cache`); ambos `server.py` con bootstrap `sys.path` y `DATABASE_PATH = get_database_path()`.
4. **Docker (D):** `docker-compose.yml` 100% env-driven (`Jwt__Key`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `AUTH_RATE_LIMIT_PER_MINUTE`, `SQLITE_DATA_SOURCE`, `build.args.VITE_API_BASE_URL`, `HOST`/`PORT`); `image:` `:stable` para los 3 servicios; chatbot `Dockerfile` env-driven.
5. **`.env.example` + docs (F):** versionado (`.gitignore` no lo excluye), con `VITE_API_BASE_URL`, `CHATBOT_HOST/PORT`, `SQLITE_DATA_SOURCE` y placeholders futuros `LLM_API_*`/`CHATBOT_CORS_ORIGINS`; README §6.1 como tabla `Variable | Requerida | Default | Consumidor` + `cp .env.example .env` + aviso de recreación; README frontend con sección de entorno.

### Decisiones (refuerzo)
| ADR | Decisión |
|---|---|
| ADR-015/016/017 | Reafirmadas (nginx 5173, env obligatorios fail-fast, `VITE_API_BASE_URL` build arg). |

### Validación
- Batería completa Validation Plan A1–D3: **TODOS PASS** (backend build SDK 10, frontend build+lint, auditoría bidireccional env vars, `docker compose config` sin literales, smoke backend `:5000/health`=200 + login admin JWT → `GET /api/books`=200, chatbot `:8000/health`=200, escaneo de secretos, `.env.example` trackeado, tabla README==keys). Stack de prueba aislado `bvi-qa-us008` desmontado (`down -v`).
- PR creado vía GitHub MCP al cierre del QA.
