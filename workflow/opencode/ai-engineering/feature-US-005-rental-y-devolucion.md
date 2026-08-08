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
4. **Frontend**: `services/rentals.ts`, types `Rental`/`PagedRentals`/`CreateRentalInput`, `CreateRentalDialog`, `MisAlquileresPage` (mis alquileres), `AlquileresAdminPage` (gestión + devolución), guarded routes `/mis-alquileres` and `/admin/rentals`, "Alquilar" button in `CatalogPage`, conditional Header links, API error messages from ProblemDetails.

### Pitfalls resolved
- User identity must come from the `userId` claim in the JWT — client-supplied ids are ignored for ownership.
- Re-login required after role promotion, because `permission` claims are baked into the JWT at login time.
- Forced `DueDate` in the past via DB shows `Overdue` status on return and releases stock.
- GUIDs stored uppercase in SQLite — matching by id in raw SQL needs the uppercase form (case-sensitive text).
- Story file pushed via MCP must be byte-identical to local (`git hash-object` check) to avoid doc drift.

## Risk Register (Riesgos)
- **NU1903 (HIGH)**: `SQLitePCLRaw.lib.e_sqlite3` 2.1.11 known vulnerability — already tracked in US-002.
- **Role promotion for tests** done via direct DB edit (no roles.manage endpoint yet; role/permission management is a future story).
- **Auth rate limiting (10/min)** can produce false 429s during scripted register/login bursts — keep delay between auth calls.
- **sessionStorage JWT** accepted academic constraint; HttpOnly cookies preferred in production.

## QA Validation (Iteration 1)

`dotnet build` → 0 errors (4 warnings, NU1903 known). `npm run build` + `npm run lint` → OK (pre-existing fast-refresh warning in `button.tsx`).

Integration smoke (curl) — B1–B13 all PASS, plus 404/401/403 ownership checks:

| Scenario | Result |
|---|---|
| B1 Usuario alquila libro disponible (201 Active, dueDate, stock 2→1) | PASS |
| B2 Libro sin stock → 409 | PASS |
| B3 dueDate inválida (pasado / >30 días) → 400 | PASS |
| B4 Alquiler duplicado activo mismo libro → 409 | PASS |
| B5 Bibliotecario devuelve → 200 Returned + returnedAt + stock +1 | PASS |
| B6 Devolver ya devuelto → 409 | PASS |
| B7 Devolución vencida → Overdue + stock liberado | PASS |
| B8 Usuario sin rentals.return → 403 | PASS |
| B9 /mine scoped (solo alquileres propios) | PASS |
| B10 /api/rentals view_all paginado + filtros | PASS |
| B11 Sin token → 401 | PASS |
| B12 Id inexistente → 404 | PASS |
| B13 Alquiler ajeno sin view_all → 404 | PASS |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated