# AI Engineering Iteration Log — US-005

- **Rama**: `feature/US-005-rental-y-devolucion`
- **Story**: US-005 — Alquiler de libros con fecha límite y devolución que libera stock
- **Status**: In Progress → Implemented → QA Validated

## Summary

Implementada la funcionalidad de alquiler de libros con fecha límite (Usuario, `rentals.create`) y devolución que libera stock (Bibliotecario/Admin, `rentals.return`), con actualizaciones atómicas de stock, protección contra alquiler duplicado activo, detección de overdue y UI condicionada por permisos.

## Iteración 1 (Implementación)

### Roles participantes
- Technical Lead — plan, rama, políticas de autorización.
- Backend Developer — comandos/consultas/handlers de alquiler, stock atómico, permisos, controlador.
- Frontend Developer — páginas de alquiler/diálogo, capa de servicios, rutas protegidas.

### Qué se construyó
1. **Aplicación**: `CreateRentalCommand` + validator (BookId/UserId no vacíos, DueDate opcional en [hoy, hoy+30]), `ReturnRentalCommand` + validator, `GetMyRentalsQuery`/`GetRentalsQuery`/`GetRentalByIdQuery`, `RentalContracts` (request/asquientos), `ConflictException` → 409.
2. **Infra**: `CreateRentalCommandHandler` (decrement atómico `WHERE AvailableCopies > 0` dentro de transacción; alquiler duplicado activo → 409; DueDate por defecto +14 días), `ReturnRentalCommandHandler` (incremento atómico `WHERE AvailableCopies < TotalCopies`; ya devuelto → 409; `Returned` vs `Overdue`), 3 query handlers con paginación/filtros/scoping propietario, `RentalMapper`, registros DI.
3. **WebAPI**: `RentalsController` (POST /api/rentals; POST /api/rentals/{id}/return; GET /api/rentals/my|mine; GET /api/rentals; GET /api/rentals/{id}); policies `rentals.create/return/view_own/view_all/view`; seed de roles `rentals.*` (Admin/Bibliotecario/Usuario); `GlobalExceptionHandler` mapea `ConflictException` → 409; `UserId` del claim JWT `userId` (nunca del cliente).
4. **Frontend**: `services/rentals.ts`, tipos `Rental`/`PagedRentals`/`CreateRentalInput`, `CreateRentalDialog`, `MisAlquileresPage` (Mis Alquileres), `AlquileresAdminPage` (gestión + devolución), rutas protegidas `/mis-alquileres` y `/admin/rentals`, botón "Alquilar" en `CatalogPage`, enlaces condicionales en `Header`, mensajes de error desde ProblemDetails.

### Riesgos registrados
- **NU1903 (HIGH)**: `SQLitePCLRaw.lib.e_sqlite3` 2.1.11 vulnerable — ya registrado en US-002.
- **Promoción de rol para pruebas** hecha vía edición directa de DB (no existe endpoint de roles.manage aún; gestión de roles es historia futura).
- **Rate limiting auth (10/min)** puede provocar 429 falsos durante bursts de registro/login scriptados — mantener retraso entre llamadas auth.
- **JWT en sessionStorage** aceptado como constraint académico; cookies HttpOnly preferible en producción.

## Validación QA (Iteration 1)

`dotnet build` → 0 errores (4 warnings, NU1903 conocido). `npm run build` + `npm run lint` → OK (warning fast-refresh preexistente en `button.tsx`).

Integración smoke (curl) — B1–B13 all PASS:

| # | Escenario | Result |
|---|---|---|
| B1 | Alquiler OK... | PASS |
| B13 | Protección de propiedad (ajeno sin view_all → 404) | PASS |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated
