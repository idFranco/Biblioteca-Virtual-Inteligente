# Backend — ASP.NET Core Web API (.NET 9)

API REST de la Biblioteca Virtual Inteligente en `workflow/backend/`, construida con **Clean Architecture** en 4 capas y patrón **CQRS** con un Dispatcher propio (ADR-009). Autenticación con **ASP.NET Core Identity + JWT**, **EF Core** sobre **SQLite**.

## Arquitectura

```
workflow/backend/
├── BibliotecaVirtual.slnx
├── Dockerfile
└── src/
    ├── BibliotecaVirtual.Domain/          # Entidades, Enums, ValueObjects, Interfaces (sin dependencias)
    ├── BibliotecaVirtual.Application/     # Commands/Queries, Handlers, FluentValidation, Contratos
    ├── BibliotecaVirtual.Infrastructure/  # EF Core (DbContext), Identity, JWT, Services, Common
    └── BibliotecaVirtual.WebAPI/          # Program.cs, Controllers, Middleware
```

- **Controllers delgados:** despachan Commands/Queries por el `IDispatcher` propio. `MediatR` y AutoMapper están **prohibidos** (ADR-009).
- **Validación obligatoria:** FluentValidation antes de procesar cualquier entrada.
- **Autorización:** permisos como claims (`permission`) sembrados por rol y aplicados mediante policies (ADR-003).

## Configuración por variables de entorno (fail-fast)

Toda la configuración se lee de variables de entorno. Si falta una variable requerida, el proceso **aborta con un mensaje claro** (ADR-016, extendido en ADR-025). No hay valores por defecto hardcodeados ni en código ni en las imágenes Docker.

| Variable | Requerida | Descripción |
|---|---|---|
| `SQLITE_DATA_SOURCE` | Sí | Ruta de la base SQLite (absoluta o relativa a `workflow/database/`) |
| `JWT_KEY` | Sí | Clave de firma HS256 (≥ 32 bytes). En compose se mapea a `Jwt__Key` |
| `JWT_ISSUER` | Sí | Emisor del token (se mapea a `Jwt__Issuer`) |
| `JWT_AUDIENCE` | Sí | Audiencia del token (se mapea a `Jwt__Audience`) |
| `CORS_ORIGINS` | Sí | Origen(es) permitidos por CORS, p. ej. `http://localhost:5173` (se mapea a `Cors__Origins`) |
| `AUTH_RATE_LIMIT_PER_MINUTE` | Sí | Límite de la policy `auth` del rate limiter por minuto |
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Sí (seed) | Credenciales del usuario administrador inicial |
| `ASPNETCORE_URLS` | Sí (Docker) | Bind del servidor, p. ej. `http://+:5000` |
| `ASPNETCORE_ENVIRONMENT` | No | `Development`, `Production`, etc. (default en compose) |
| `NOTIFICATIONS_CHECK_INTERVAL_SECONDS` | Sí | Intervalo del `RentalDueNotificationService` en segundos |
| `CATALOG_SEED__ENABLED` / `CATALOG_SEED__FILEPATH` | No | Control del seed del catálogo |

### Local (sin Docker)

```bash
export SQLITE_DATA_SOURCE=./workflow/database/BibliotecaVirtual.db
export JWT_KEY=$(openssl rand -base64 48)
export JWT_ISSUER=BibliotecaVirtual
export JWT_AUDIENCE=BibliotecaVirtual
export CORS_ORIGINS=http://localhost:5173
export AUTH_RATE_LIMIT_PER_MINUTE=10
dotnet run --project src/WebAPI
```

La API queda en `http://localhost:5000` (Swagger en `/swagger`). La base se crea automáticamente con `EnsureCreated` en `workflow/database/`.

### Docker

El `Dockerfile` no fija variables por defecto; `docker-compose.yml` las inyecta como obligatorias (ver README raíz). Incluye un `HEALTHCHECK` que consulta `http://127.0.0.1:5000/health` cada 30 s (timeout 10 s, 3 reintentos, período de arranque 40 s) para que Docker y `docker compose` conozcan el estado real del servicio. Combinado con `depends_on: condition: service_healthy`, los servicios dependientes (frontend, chatbot) no arrancan hasta que el backend esté sano.

## Seed

- **Roles/permisos:** `SeedRolesAsync` es **autoritativo**: en cada arranque añade los claims del manifiesto de cada rol y **elimina** los sobrantes. Matriz:

| Permiso | Admin | Bibliotecario | Usuario |
|---|---|---|---|
| `books.read` | ✓ | ✓ | ✓ |
| `books.create` / `books.update` / `books.delete` | ✓ | ✓ | — |
| `rentals.create` | — | — | ✓ |
| `rentals.return` | ✓ | ✓ | — |
| `rentals.view_own` | — | — | ✓ |
| `rentals.view_all` | ✓ | ✓ | — |
| `books.request` | ✓ | ✓ | ✓ |
| `books.manage` | ✓ | ✓ | — |
| `roles.manage` | ✓ | — | — |
| `notifications.read` | ✓ | ✓ | ✓ |

  > **Admin no alquila:** el rol Admin no tiene `rentals.create` ni `rentals.view_own`, por lo que no puede alquilar ni consultar «Mis alquileres» (US-014).

- **Administrador inicial:** se crea con `ADMIN_EMAIL`/`ADMIN_PASSWORD` si no existe (idempotente).
- **Catálogo:** seed idempotente desde `workflow/backend/data/seed-books.json` (solo inserta si `Books` está vacía, ADR-019).

## Endpoints

| Método | Ruta | Permiso | Descripción |
|---|---|---|---|
| `POST` | `/api/auth/register` | público | Registro de usuario |
| `POST` | `/api/auth/login` | público | Login → JWT |
| `POST` | `/api/auth/refresh` | público | Renovar tokens |
| `POST` | `/api/auth/revoke` | autenticado | Cerrar sesión / revocar refresh token |
| `GET` | `/api/books` | `books.read` | Catálogo paginado con filtros (título, autor, género, disponibles) |
| `POST` | `/api/books` | `books.create` | Crear libro |
| `PUT` | `/api/books/{id}` | `books.update` | Actualizar libro |
| `DELETE` | `/api/books/{id}` | `books.delete` | Eliminar libro |
| `GET` | `/api/books/{bookId}/reading` | `books.read` + alquiler activo | Contenido de lectura (Sala de lectura) — incluye `content` (US-021) |
| `POST` | `/api/rentals` | `rentals.create` | Crear alquiler con fecha límite (reglas de negocio US-021: sin duplicado de título activo + tope de concurrentes) |
| `GET` | `/api/rentals/mine` | `rentals.view_own` | Alquileres del usuario autenticado |
| `GET` | `/api/rentals` | `rentals.view_all` | Todos los alquileres (paginado) |
| `PATCH` | `/api/rentals/{id}/return` | `rentals.return_own` | Registrar devolución y liberar stock (self-service por propiedad, US-021) |
| `POST` | `/api/book-requests` | `books.request` | Solicitar copia de un libro no disponible |
| `GET` | `/api/book-requests` | `books.manage` | Solicitudes (admin/bibliotecario) |
| `PATCH` | `/api/book-requests/{id}/approve` | `books.manage` | Aprobar solicitud y dar de alta el libro |
| `PATCH` | `/api/book-requests/{id}/reject` | `books.manage` | Rechazar solicitud |
| `GET` | `/api/notifications` | `notifications.read` | Notificaciones del usuario (paginado, `unreadOnly`) |
| `PATCH` | `/api/notifications/{id}/read` | `notifications.read` | Marcar notificación como leída |
| `GET` | `/api/users` | `roles.manage` | Gestión de usuarios |
| `GET` | `/health` | público | Healthcheck (incluye check del DbContext) |

## Notificaciones de vencimiento (US-013)

`RentalDueNotificationService` es un `BackgroundService` que por cada ciclo despacha `GenerateDueDateNotificationsCommand` (CQRS) y detecta alquileres **activos** con `0 < DueDate - Now <= 2 días`. Idempotente por índice único sobre `RentalId`. Intervalo configurable por `NOTIFICATIONS_CHECK_INTERVAL_SECONDS`.

## Reglas de negocio de alquiler (US-021)

Forzadas en el **backend** (`CreateRentalCommandHandler`, fuente de verdad, no solo UI):

1. **Sin duplicado de título activo:** un usuario no puede tener un alquiler activo de un libro del **mismo título** que otro alquiler activo suyo (comparación case-insensitive `ToLower()`, sin importar si son filas `Book` distintas). → `409 Conflict` "Ya tienes un alquiler activo de este libro." y **no decrementa stock**.
2. **Tope de alquileres activos concurrentes:** máximo **5** por usuario (un `Overdue` cuenta como activo), configurable vía `Rentals__MaxActivePerUser` (default 5). Al superarlo → `409 Conflict` indicando el límite y **no decrementa stock**.

Sin cambios de contrato de API (nuevo 409) ni de índice DB (tablas pequeñas; el handler es la fuente de verdad). Cubierto por tests xUnit del proyecto `tests/BibliotecaVirtual.Tests`.

## Devolución self-service por propiedad (US-021)

El endpoint `PATCH /api/rentals/{id}/return` usa la política **`rentals.return_own`** = `rentals.return` **o** `rentals.view_own`:

- **Usuario** (con `rentals.view_own`): puede devolver **solo su propio** alquiler desde "Mis alquileres".
- **Bibliotecario/Admin** (con `rentals.return`): pueden devolver **cualquier** alquiler.
- **Anti-enumeración:** si un usuario intenta devolver un alquiler ajeno sin `rentals.return`, el handler lanza `KeyNotFoundException` → **404** (no revela la existencia del alquiler ajeno).
- `ReturnRentalCommand` gana `RequesterUserId` y `CanReturnAny`; solo el controller construye el comando. Resto del flujo intacto (stock +1, `ReturnedAt`, `Status` → `Overdue` si vencido).

## Contenido de lectura (US-021)

- `Book.Content` (TEXT, opcional) expuesto en `BookForReadingResponse.content` y en `CreateBookRequest`/`UpdateBookRequest` (opcional, `MaximumLength(100000)`).
- **Alineación de esquema idempotente sin regenerar la BD runtime:** helper en `Program.cs` tras `EnsureCreated` que ejecuta `PRAGMA table_info(Books)` y, si falta la columna, `ALTER TABLE Books ADD COLUMN Content TEXT` (no destructivo).
- Seed opcional con extractos de dominio público en `seed-books.json`.
- El frontend renderiza el contenido con tipografía de lectura y un placeholder on-brand cuando está vacío (nunca pantalla en blanco).

## Tests / validación

```bash
dotnet build BibliotecaVirtual.slnx
dotnet test BibliotecaVirtual.slnx   # proyecto tests/BibliotecaVirtual.Tests (US-021)
```
