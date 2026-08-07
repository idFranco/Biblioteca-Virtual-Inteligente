# AI Engineering Iteration Log — US-004

- **Branch**: `feature/US-004-catalog-libros`
- **Story**: US-004 — Catálogo de libros, búsqueda y filtrado
- **Status**: In Progress → Implemented → QA Validated

## Summary

Implemented the book catalog with full CRUD (Admin/Bibliotecario) and search/filtering by title, author, genre and availability (any authenticated user), backed by permission-based authorization (`books.*`), with the React SPA pages for catalog and management.

## Iteration 1 (Implementation)

### Roles participating
- Technical Lead — plan, branch, authorization policies wiring.
- Backend Developer — queries/commands/handlers, permission claims, controller, seeds.
- Frontend Developer — catalog + admin pages, service layer, permission guard.

### What was built
1. **Application**: `GetBooksQuery` (page/pageSize/search/author/genre/availableOnly), `GetBookByIdQuery`, `CreateBookCommand`/`UpdateBookCommand`/`DeleteBookCommand`, `BookContracts` DTOs (`BookResponse`, `CreateBookRequest`, `UpdateBookRequest`, `PagedResult<T>`), validators with FluentValidation (title/author required ≤255, copies ≥0, `availableCopies ≤ totalCopies`).
2. **Infrastructure**: `GetBooksQueryHandler` (EF Core filters, case-insensitive search, ordering, skip/take + count), GetById/Create/Update/Delete handlers; `TokenService` now resolves `permission` claims from `RoleClaims` and includes them in the JWT and `AuthUserResponse`; DI registrations for queries/commands/validators.
3. **WebAPI**: `BooksController` (`api/books`) thin with `[Authorize(Policy = "books.read/create/update/delete")]`; `Program.cs` authorization policies; role seed with permission `RoleClaims` (Admin & Bibliotecario: all books.*, Usuario: books.read) and initial Admin user from env (`ADMIN_EMAIL`/`ADMIN_PASSWORD`).
4. **Frontend**: `services/books.ts` + `apiPut`/`apiDelete`; types `Book`/`PagedBooks`/`BookFilters`/`CreateBookInput`/`UpdateBookInput`; `CatalogPage` with search/filters/pagination; `BooksAdminPage` CRUD table+form; `PermissionGuard`; routes `/catalogo` (protected) and `/admin/books` (permission-guarded); Header conditional links; `auth.ts` maps `permissions` from API.

### Pitfalls resolved
- `PagedResult` constructor argument ordering (named args) — fixed at compile time.
- DI `using` for book validators missing → added `Commands.Books.Validators`.
- Empty GUID (`00000000-...`) fails `NotEmpty` validation with 400, while a valid-but-missing GUID correctly returns 404 from the handler — correct semantics per acceptance criteria.
- Permission claims must be read via `RoleManager.GetClaimsAsync` (not user claims) since they are seeded as `RoleClaims`.

## Risk Register (Riesgos)
- **NU1903 (HIGH)**: `SQLitePCLRaw.lib.e_sqlite3` 2.1.11 known vulnerability (GHSA-2m69-gcr7-jv3q) via EF Core SQLite. Candidate for dependency-upgrade story.
- **Admin seed**: only created when `ADMIN_EMAIL`/`ADMIN_PASSWORD` env vars are set; never hardcoded.
- **sessionStorage JWT**: accepted academic constraint; HttpOnly cookies preferred in production.
- **Rate limiting**: auth endpoints limited (10/min); books endpoints not rate-limited (accepted for internal catalog; chatbot endpoints to be limited separately).

## QA Validation (Iteration 1)

`dotnet build` → 0 errors. `npm run build` + `npm run lint` → clean (pre-existing fast-refresh warning in `button.tsx`).

Integration smoke (curl) — 17/17 scenarios:

| Scenario | Result |
|---|---|
| Admin permissions include books.* (4) | PASS |
| List paginated (page/pageSize/totalItems/totalPages) | 200 PASS |
| Search by title partial | PASS |
| Search by author | PASS |
| Filter by genre | PASS |
| Filter availableOnly (excludes 0 copies) | PASS |
| Create book 201 + availableCopies=totalCopies | PASS |
| Create without permission (Usuario) | 403 PASS |
| Create invalid | 400 PASS |
| Update 200 + title changed | PASS |
| Update available>total | 400 PASS |
| Delete | 204 PASS |
| Delete missing id | 404 PASS |
| Usuario reads catalog | 200 PASS |
| No token | 401 PASS |
| Usuario permissions only ['books.read'] | PASS |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated
