# AI Engineering Log — feature-US-007-docker-alignment

## Iteración 1 — 2026-08-08 (implement + qa)

### Historia
**US-007** — Alinear archivos Docker con las aplicaciones (estado al cerrar: Implemented → Validated).

### Problema (validado en runtime antes de planificar)
1. Frontend inalcanzable: nginx escucha en :80 por defecto pero compose mapeaba `5173:5173` → HTTP 000.
2. Auth backend rota en compose: `Jwt:Key` = literal `${JWT_KEY}` (no interpolado por .NET), sin `ADMIN_EMAIL`/`ADMIN_PASSWORD` → 400 IDX10653 y sin seed admin.
3. URL base SPA desalineada: default `http://localhost:5002` en Vite vs backend publicado en 5000.

### Decisión clave
| ADR | Decisión |
|---|---|
| ADR-015 | nginx.conf propio **listen 5173** + SPA fallback; mapeo `5173:5173` único puerto (se descartó `5173:80`) |
| ADR-016 | Env backend **obligatorios** `${VAR:?...}` (fail-fast, cero secretos commiteados); `Jwt:Key=""` + throw alcanzable |
| ADR-017 | `VITE_API_BASE_URL` como build arg (build-time del bundle), default dev en código intacto |

### Riesgo (nuevo)
**Hydra (LOW):** si se olvida `JWT_KEY` en el `.env` de desarrollo local, el backend falla al arrancar (intencional). Mitigación: `.env.example` con instrucciones `openssl rand -base64 48`; README §7.

### Eliminado
- Volumen bind mount para SQLite: **excluido** de US-007 (cambio de contrato de datos), documentado como "Future improvement" en DECISIONS.md.

### Validación
- Batería completa QA-01..QA-15: 15/15 PASS en entorno limpio con `docker compose up --build -d`.
- `dotnet build`: 0 errores/0 warnings.
- PR creado vía GitHub MCP al cierre del QA (mergeable).