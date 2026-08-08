# AI Engineering Iteration Log — US-005

- **Branch**: `feature/US-005-rental-y-devolucion`
- **Story**: US-005 — Alquiler de libros con fecha límite y devolución que libera el inventario
- **Status**: In Progress → Implemented → QA Validated

## Summary

Implemented book rentals with due date (Usuario, rentals.create) and return flow that releases stock (Bibliotecario/Admin, rentals.return), with atomic stock updates, duplicate-active-rental protection, overdue detection, and permission-based UI.

## Iteration 1 (Implementation)

Roles participating: Technical Lead, Backend Developer, Frontend Developer.

### What was built (backend)
- Commands/queries/validators/handlers/contracts para rentales y devoluciones (FluentValidation).
- Stock atómico con `ExecuteUpdateAsync` + transacción; `ConflictException` → 409.
- `RentalsController` con policies `rentals.create/return/view_own/view_all/view` y seed de permisos.

### What was built (frontend)
- `services/rentals.ts`, tipos, diálogo de creación, páginas "Mis alquileres" y "Gestión de alquileres", rutas protegidas y botón en catálogo.

### Pitfalls resolved
- Identity must come from the claim (client-supplied ids ignored).
- Re-login needed after role changes (permission claims baked into JWT).
- Past dueDate → Overdue on return.
- SQLite GUIDs case: raw SQL must use uppercase.

## Risk Register (Riesgos)
- NU1903 (HIGH) SQLitePCLRaw 2.1.11 — tracked in US-002.
- Roles promoted via direct DB for tests (no roles.manage endpoint yet).
- Auth rate limiting may false-429 during scripted tests.

## QA Validation

`dotnet build` → 0 errors. `npm run build`/`lint` OK.

B1–B10 smoke through curl:

| Scenario | Result |
|---|---|
| B1 alquiler 201 + descuento stock | PASS |
| B2 sin stock 409 | PASS |
| B3 dueDate inválida 400 | PASS |
| B4 duplicado 409 | PASS |
| B5 devolución 200 + stock | PASS |
| B6 devuelto otra vez 409 | PASS |
| B7 vencido → Overdue | PASS |
| B8 sin permiso 403 | PASS |
| B9 mis alquileres | PASS |
| B10 listado paginado/filtros | PASS |
| B11 sin token 401 | PASS |
| B12 404 | PASS |
| B13 ajeno 404 | PASS |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated
