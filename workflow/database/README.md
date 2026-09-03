# Database — SQLite

Carpeta `workflow/database/` del sistema. Almacena las bases SQLite en tiempo de ejecución y los scripts de utilidad de limpieza/verificación.

## Bases de datos (runtime)

Estas bases se generan y mantienen por el sistema; **no están versionadas en Git** (`.gitignore` excluye `*.db`, `*.sqlite`):

| Archivo | Propósito | Creador / escritor |
|---|---|---|
| `BibliotecaVirtual.db` | Base principal del sistema: usuarios, roles, catálogo, alquileres, notificaciones, preferencias, feedback, book-requests | Backend (.NET 9 / EF Core) al arrancar (`EnsureCreated`, seed idempotente — ADR-019); leída por Biblioteca-MCP y Security-Audit-MCP |
| `audit.db` | Eventos de auditoría del chatbot (`audit_events`) | Security-Audit-MCP |

- **Docker:** ambas bases se persisten en el volumen compartido `database_data` (montadas en `/app/database`), accesibles por backend y por los MCP empaquetados en la imagen del chatbot.
- **Local standalone:** apuntan a esta carpeta del repo vía `SQLITE_DATA_SOURCE` (backend) y `DATABASE_PATH` / `AUDIT_DATABASE_PATH` (MCP).
- El backend siembra roles/permisos y el usuario administrador en el primer arranque; el catálogo (~50 obras reales) se siembra desde `workflow/backend/data/seed-books.json` solo si la tabla `Books` está vacía (idempotente).

## Scripts de utilidad

| Archivo | Propósito |
|---|---|
| `cleanup_biblioteca.sql` | Elimina (idempotente y FK-safe) el residuo de datos de prueba E2E de `BibliotecaVirtual.db`, conservando los datos demo y el admin (US-020). |
| `cleanup_audit.sql` | Limpieza similar para el residuo de auditoría E2E en `audit.db`. |
| `verify_cleanup.py` | Verifica que las bases runtime quedaron sin residuo de pruebas E2E y con los datos demo + admin (US-020). |
| `openlibrary_verification.json` | Registro de la verificación de que los títulos sembrados existen en Open Library (tarea de desarrollo/QA). |

> **GATE de aprobación humana:** la ejecución de los scripts `cleanup_*.sql` y de `verify_cleanup.py` requiere aprobación previa y, de hacerse sobre las bases runtime, respaldo en `/tmp` (ver cabeceras de los archivos).

## Consideraciones

- Los archivos `*.db`, `-shm` y `-wal` son artefactos de SQLite (el `-wal`/`-shm` aparecen con journaling WAL) y no deben versionarse.
- No edites las bases a mano si el stack está levantado; los MCP leen con journaling WAL y puede haber escrituras concurrentes del backend.
