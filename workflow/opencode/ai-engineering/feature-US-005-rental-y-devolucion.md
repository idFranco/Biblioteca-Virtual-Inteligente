# AI Engineering Iteration Log — US-005

- **Branch**: `feature/US-005-rental-y-devolucion`
- **Story**: US-005 — Alquiler de libros con fecha límite y devolución que libera stock
- **Status**: In Progress → Implemented → QA Validated

## Summary

Implemented book rentals with due date (Usuario, `rentals.create`) and return flow that releases stock (Bibliotecario/Admin, `rentals.return`), with atomic stock updates, duplicate-active-rental protection, overdue detection, and permission-based UI.

## Iteration 1 (Implementation)

### Roles participating
- Technical Lead — plan, branch, authorization policies wiring.
- Backend Developer — rental commands/queries/handlers, atomic stock, permissions, controller.
- Frontend Developer — rental pages/dialog, service layer, guarded routes.

### What was built
1. **Application**: `CreateRentalCommand` + validator (BookId/UserId not empty, DueDate optional in [today, today+30]), `ReturnRentalCommand` + validator, `GetMyRentalsQuery`/`GetRentalsQuery`/`GetRentalByIdQuery`, `RentalContracts` (requests/responses), `ConflictException` → 409.
2. **Infrastructure**: `CreateRentalCommandHandler` (atomic `ExecuteUpdateAsync` decrement `WHERE AvailableCopies > 0` inside a transaction; duplicate active rental → 409; default DueDate +14 days), `ReturnRentalCommandHandler` (atomic increment `WHERE AvailableCopies < TotalCopies`; already-returned → 409; `Returned` vs `Overdue`), 3 query handlers with paging/filters/ownership scoping, `RentalMapper`, DI registrations.
3. **WebAPI**: `RentalsController` (POST /api/rentals; POST /api/rentals/{id}/return; GET /api/rentals/mine|all; GET /api/rentals/{id}); policies `rentals.create/return/view_own/view_all/view`; role seed `rentals.*` (Admin/Bibliotecario/Usuario); `GlobalExceptionHandler` maps `ConflictException` → 409; `UserId` from JWT claim `userId` (never from client input).
4. **Frontend**: `services/rentals.ts`, types `Rental`/`PagedRentals`/`CreateRentalInput`, `CreateRentalDialog`, `MisAlquileresPage`, `AlquileresAdminPage`, guarded routes, "Alquilar" button, conditional Header links, ProblemDetails error messages.

### Pitfalls resolved
- Identity must come from the claim (never client-supplied ids).
- Re-login required after role changes (permission claims baked into JWT).
- Forced past dueDate shows `Overdue` on return and frees stock.
- GUIDs uppercase in SQLite — raw SQL must use uppercase.
- Story pushed via MCP must stay byte-identical to local.

## Risk Register (Riesgos)
- NU1903 (HIGH) SQLitePCLRaw 2.1.11 — already tracked in US-002.
- Roles promoted via direct DB (no roles.manage endpoint yet).
- Auth rate limiting can false-429 heavy scripted tests.
- sessionStorage JWT accepted for academic scope.

## QA Validation (Iteration 1)

`dotnet build` → 0 errors (NU1903 known). `npm run build` + lint → OK (pre-existing warning).

Integration smoke (curl) — B1–B13:

| Scenario | Result |
|---|---|
| B1 alquiler 201 Active + stock decrement | PASS |
| B2 sin stock 409 | PASS |
| B3 dueDate inválida 400 | PASS |
| B4 duplicado activo 409 | PASS |
| B5 devolución 200 Returned + stock | PASS |
| B6 devuelto otra vez 409 | PASS |
| B7 vencido → Overdue | PASS |
| B8 sin permiso 403 | PASS |
| B9 mis alquileres scoped | PASS |
| B10 listado paginado/filtrado | PASS |
| B11 sin token 401 | PASS |
| B12 id inexistente 404 | PASS |
| B13 ajeno 404 | PASS |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated
