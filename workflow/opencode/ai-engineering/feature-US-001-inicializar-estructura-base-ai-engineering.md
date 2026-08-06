# AI Engineering Log — US-001 — Iteración de rework (QA)

- **Branch:** `feature/US-001-inicializar-estructura-base`
- **Story:** US-001 — Inicializar estructura base del repositorio
- **Ciclo:** Draft → Approved → In Progress → Implemented → Rejected (QA #1) → In Progress (rework) → Implemented → **Validated (QA #2)**
- **Fecha:** 2026-08-06

## Detalle del rework (Rejected → In Progress → Implemented)

| Ítem | Descripción |
|---|---|
| **Problema QA #1** | Backend crasheaba al iniciar: la connection string usaba keywords no soportados por Microsoft.Data.Sqlite (`Cache Size`). La DB no se creaba. |
| **Fix** | `appsettings.json`: connection string `Data Source=../database/BibliotecaVirtual.db;Pooling=True`; en Docker se sobreescribe vía env var. |
| **Fix** | `Program.cs`: `ResolveLocalSqlitePath` para resolver rutas relativas a `workflow/database/` sin depender del CWD. Registro del interceptor en `AddDbContext`. |
| **Fix** | `Infrastructure/Services/SqlitePragmaInterceptor.cs` (nuevo): aplica `PRAGMA journal_mode=WAL` y `PRAGMA busy_timeout=5000` por conexión. |
| **Restauración docs** | `AGENTS.md`, `.opencode/instructions/git-rules.md`, `.opencode/commands/qa-check.md`, `.opencode/commands/implement-user-story.md` restaurados byte-a-byte desde fuente canónica; eliminado archivo espurio `DO_NOT_COMMIT`. |

## Results de re-QA (Validado)

| # | Validación | Resultado |
|---|---|---|
| 1 | `dotnet build BibliotecaVirtual.slnx` | PASS — 0 errors (warning NU1903 preexistente) |
| 2 | `npm run build` | PASS |
| 3 | `docker compose config` | PASS — config válida, Dockerfiles presentes |
| 4 | MCP server files | PASS |
| 5 | Healthcheck | PASS — HTTP 200 en `http://localhost:5002/health` |
| 6 | EF Core SQLite | PASS — DB creada, tablas presentes, WAL activo |

## Decisiones registradas
- Backend en rama `feature/US-001-inicializar-estructura-base` con solución `BibliotecaVirtual.slnx`.
- Connection string SQLite sin keywords no soportados; pragmas WAL/busy_timeout vía interceptor EF Core.