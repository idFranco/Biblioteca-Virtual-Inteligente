# AI Engineering Iteration Log — US-003

- **Branch**: `feature/US-003-auth-jw`
- **Story**: US-003 — Registro de usuarios y autenticación JWT
- **Status**: Implemented → QA Validated

## Summary

Implemented user registration and JWT authentication end-to-end: backend issuing short-lived access tokens (15 min) and rotating refresh tokens (7 days) stored hashed (SHA-256) in SQLite, plus the React SPA login/register/refresh flows with protected routes.

## Iteration 1 (Implementation)

### Roles participating
- Technical Lead — plan, branch, DI, rate limiting wiring.
- Backend Developer — domain entity, contracts/commands/validators, handlers, token services, controller, exception mapping.
- Frontend Developer — auth service, session store, pages, protected routes, header.

### What was built
1. **Domain**: `RefreshToken` entity; `BibliotecaDbContext` extended with `DbSet<RefreshToken>` (unique index on `TokenHash`, cascade delete).
2. **Application**: Auth contracts, commands, FluentValidation validators, `ITokenService`, `ResourceAlreadyExistsException`.
3. **Infrastructure**: `TokenHasher` (SHA-256), `TokenService` (JWT + refresh persistence), Register/Login/Refresh/Revoke handlers validating in pipeline, DI registrations.
4. **WebAPI**: thin `AuthController` (`/api/auth`: register, login, refresh, revoke), fixed-window rate limiter (10/min, 429), role seeding (Admin/Bibliotecario/Usuario), JWT bearer config, `GlobalExceptionHandler` +400/409 mappings.
5. **Frontend**: `services/api.ts` (Bearer header + auto-refresh on 401), `services/auth.ts`, zustand `authStore` persisted in sessionStorage, `LoginPage`, `RegisterPage`, `ProtectedRoute`, router, `Header` with user + logout.

### Pitfalls resolved
- Open-generic DI registration with closed handler types throws at startup → registered closed generic interfaces explicitly.
- `EnsureCreated` does not apply schema changes to an existing DB → removed local dev DB (gitignored) so it regenerates with `RefreshTokens`.
- `IList<string>` → `IReadOnlyList<string>` conversion in `AuthUserResponse`.
- Frontend default API base pointed at :5000 but backend listens at :5002 → aligned to `http://localhost:5002` (env-overridable via `VITE_API_BASE_URL`).
- Duplicate email originally mapped to 500 via `InvalidOperationException` → introduced `ResourceAlreadyExistsException` mapped to 409.

## Risk Register (Riesgos)
- **NU1903 (HIGH)**: `SQLitePCLRaw.lib.e_sqlite3` 2.1.11 — known vulnerability (GHSA-2m69-gcr7-jv3q) pulled transitively by EF Core. Backend warns on every build. Candidate for a future dependency-upgrade user story (bump Microsoft.EntityFrameworkCore.Sqlite).
- **JWT key**: `Jwt:Key` is a `${JWT_KEY}` placeholder resolved from env/secrets; must not be committed. Local QA used dev-only key.
- **Session storage**: refresh tokens stored in sessionStorage (academic constraint); strict XSS mitigations required. HttpOnly cookie approach documented as production preference.

## QA Validation (Iteration 1)

`dotnet build` → 0 errors. `npm run build` + `npm run lint` → clean (pre-existing fast-refresh warning in `button.tsx`).

Integration smoke (curl):

| Scenario | Result |
|---|---|
| Register success → access + refresh, role `Usuario` | 200 ✅ |
| Duplicate email | 409 ✅ |
| Weak password | 400 ✅ |
| Login success | 200 ✅ |
| Invalid credentials | 401 ✅ |
| Refresh rotates token; old token reuse → 401 | ✅ |
| Revoke + reuse → 401 | ✅ |
| Rate limit 10/min → 429 | ✅ |

## Result
- **QA**: PASS
- **Status**: Implemented → Validated