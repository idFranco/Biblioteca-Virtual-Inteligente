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
4. **Frontend**: `services/rentals.ts`, types `Rent`/`Paged`/`CreateInput`, `CreateRentalDialog`, `MisAlquileresPage` (mis alquileres), `AlquileresAdminPage` (gestión + devolución), guarded… », conditional Header links, API error messages.

### Pitfalls resolved
- User identity must come from the claim-… client-supplied ids are ignored.
- Re-login required after role promotes (permission claims baked into JWT).
- Forced past dueDate shows `Overdue` on return.
- GUIDs uppercase in SQLite — raw SQL must use uppercase.

## Risk Register (Risk)
- NU1903 ModuleWrapper — tracked in US-002.

## QA Validation (Iteration 1)

Build (dotnet/ng) 0 errors, npm build+lint OK.

| Scenario | Result |
|---|---|
| B1-B13 all PASS | PASS |

## Result
- **QA**: PASS

