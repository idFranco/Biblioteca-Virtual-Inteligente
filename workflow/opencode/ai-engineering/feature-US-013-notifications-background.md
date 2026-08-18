# AI Engineering — Bitácora de iteración — US-013 (rama `feature/US-013-notifications-background`)

## Iteración 1 — Implementación inicial

- Story `Approved → In Progress`; rama `feature/US-013-notifications-background` creada vía GitHub MCP (nombre elegido por el usuario); `main` actualizada (fast-forward `64d9a99..4052b36`) antes de abrir la rama.
- **Backend (.NET 9, CQRS con `IDispatcher` propio, ADR-009 — sin MediatR ni AutoMapper):**
  - `Domain/Entities/Notification.cs`: entidad con `Id`, `UserId`, `RentalId`, `Message`, `DueDate`, `IsRead`, `CreatedAt` y navegaciones `User`/`Rental`.
  - `Application`: `NotificationContracts.cs` (`NotificationResponse`, `GenerateDueDateNotificationsResult`); `GenerateDueDateNotificationsCommand`; `MarkNotificationReadCommand` + `MarkNotificationReadCommandValidator` (FluentValidation); `GetMyNotificationsQuery` (`Page`/`PageSize`/`UnreadOnly`).
  - `Infrastructure/Handlers/Notifications/`: `GenerateDueDateNotificationsCommandHandler` (ventana `0 < DueDate - Now <= 2 días`, `Status == Active`, exclusión de `RentalId` ya notificados, mensaje en español con título + fecha), `MarkNotificationReadCommandHandler` (ownership por `UserId`, `404` si ajena/inexistente), `GetMyNotificationsQueryHandler` (paginado estilo `GetMyRentalsQueryHandler`, `OrderByDescending(CreatedAt)`, filtro `unreadOnly`), `NotificationMapper` estático.
  - `Infrastructure/Services/RentalDueNotificationService.cs`: `BackgroundService` con `PeriodicTimer` + `IServiceScopeFactory`, sin lógica de negocio (despacha el Command), intervalo `Notifications:CheckIntervalSeconds` (default 3600s, min 30s), logging y manejo de errores sin romper el loop.
  - `BibliotecaDbContext.cs`: `DbSet<Notification>` + configuración Fluent (FKs Cascade, índice único `IX_Notifications_RentalId`, índice `IX_Notifications_UserId`).
  - `DependencyInjection.cs`: registro de handlers, validator y `AddHostedService<RentalDueNotificationService>()`.
  - `Program.cs`: policy `notifications.read` + seed del permiso en `Admin`, `Bibliotecario` y `Usuario`.
  - `appsettings.json`: `Notifications.CheckIntervalSeconds = 3600`; `docker-compose.yml`: `NOTIFICATIONS_CHECK_INTERVAL_SECONDS` (default 3600).
  - `WebAPI/Controllers/NotificationsController.cs`: controller delgado → `GET /api/notifications` y `PATCH /api/notifications/{id}/read` (policy `notifications.read`, ownership por `userId` claim).
- **Validación durante implementación:** `dotnet build BibliotecaVirtual.slnx` OK (0 warnings / 0 errors); smoke test aislado en `/tmp/opencode/us013-smoke` (eliminado tras verificar): ventana, idempotencia, ownership y `unreadOnly` todos PASS.
- Push vía MCP `feat(US-013)` (`e540256`); story → `Implemented` vía MCP; push final `docs(US-013)` (`eb11193`) con `US-013.md` en `Implemented`. Rama local sincronizada con `git reset --hard origin/...`.

## Risk Register

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| Concurrencia SQLite (background + requests) | Media | Mitigated | WAL activo (`SqlitePragmaInterceptor`); inserciones idempotentes; retry implícito en cada ciclo. |
| `BackgroundService` singleton resolviendo dependencias scoped | Media | Mitigated | `IServiceScopeFactory` por ciclo; nunca se inyecta `IDispatcher`/`DbContext` directo en el servicio. |
| Duplicación de notificaciones entre ejecuciones | Media | Mitigated | Índice único `RentalId` + guard previo a insertar (idempotencia verificada en QA). |
| Regeneración de esquema en bases existentes | Media | **Resolved** | Borrado único documentado de `workflow/database/BibliotecaVirtual.db` (backup previo); `EnsureCreated` regenera; seed idempotente (ADR-019/024). |
| Alcance creciente hacia la UI de campana | Media | Mitigated | UI de notificaciones pospuesta explícitamente a una historia futura; solo se exponen los endpoints. |
| Marcar notificaciones ajenas como leídas | Media | Mitigated | Ownership obligatorio por `UserId` en el handler; QA verificó `404` para notificación ajena. |

## Iteración 2 — QA formal (`qa-check US-013`)

- Repo indexado (`index_repository`, modo fast). Branch verificada: `feature/US-013-notifications-background`.
- Builds: backend `dotnet build` 0 errores / 0 warnings; frontend `npm run build` OK y `npm run lint` OK (solo warning preexistente `button.tsx`, ajeno a US-013).
- **Esquema:** BD dev regenerada (borrado único con backup previo en `/tmp/opencode`); `EnsureCreated` crea `Notifications` con FKs Cascade, índice único `RentalId` e índice `UserId` (verificado en SQLite).
- **Seed de permisos:** `notifications.read` presente en claims de `Admin`, `Bibliotecario` y `Usuario` (verificado en BD); policy protege ambos endpoints.
- **Smoke test del handler contra la BD dev real** (`/tmp/opencode/us013-qasmoke`, console .NET): alquiler `Active` `now+1d` → `RUN1_CREATED=1`; alquiler fuera de ventana (`now+5d`), vencido (`now-1d`) y `Returned` → no generan; `RUN2_CREATED=0` (idempotencia); mensaje correcto en español con `IsRead=false`.
- **API con JWT** (admin + usuario regular): `GET /api/notifications` solo las del usuario (admin `totalItems=0`); `unreadOnly=true` filtra; `PATCH .../read` → 204 propia / 404 ajena e inexistente; sin token → 401.
- **BackgroundService:** arranca con el host y loguea `Comprobación cada 3600 segundos`.
- **Limpieza:** artefactos QA eliminados de la BD dev (usuarios, alquileres, notificaciones); BD dev queda con esquema + seed (50 libros).
- Documentación: `README.md` sección 12 (notificaciones automáticas de vencimiento), `DECISIONS.md` → **ADR-024**, `US-013.md` → `## QA Result: PASS`.
- Pendiente documentado: `.env.example` no pudo actualizarse con `NOTIFICATIONS_CHECK_INTERVAL_SECONDS` — la lectura/escritura del archivo está bloqueada por reglas de permisos del agente (`*.env.*` deny); el intervalo sí está documentado en `README.md` y `appsettings.json` (default 3600).
- PR creado vía GitHub MCP `create_pull_request` (PR GATE); mergeable con `main`.
- Story → `Validated` vía MCP tras el PR Gate; push final de documentación y sync local.

## Próximos pasos
- Merge del PR en GitHub para cerrar la historia.
- Historia futura: UI de campana/panel de notificaciones en el frontend consumiendo `GET/PATCH /api/notifications`.
- Evaluar bind mount de SQLite (mejora futura ya registrada en DECISIONS) si se desea que los MCPs host lean la misma BD que el contenedor.