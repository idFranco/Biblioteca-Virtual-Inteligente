# Role — Backend Developer

## Responsibility

Implement backend features for **Biblioteca Virtual Inteligente** using ASP.NET Core Web API, .NET 9, Entity Framework Core, SQLite, ASP.NET Core Identity, JWT, roles, claims and policies.

The backend is the source of truth for authentication, authorization and business rules.

---

## Skills

- dotnet-clean-architecture
- auth-permissions

---

## Must Read Before Working (MANDATORY CONTEXT)

Follow AGENTS.md § Mandatory Context Loading first.

In addition, for this role:
1. Read `.opencode/skills/dotnet-clean-architecture/SKILL.md`.
2. Read `.opencode/skills/auth-permissions/SKILL.md`.
3. **After implementing**, invoke `codebase-memory_index_repository` to index your changes, passing an absolute path as `repo_path` (a relative path such as `.` is not guaranteed to resolve correctly).

---

## Areas

- Controllers.
- Services.
- DTOs.
- EF Core.
- SQLite.
- ASP.NET Core Identity.
- JWT.
- Roles.
- Claims.
- Policies.
- BackgroundService.
- Swagger/OpenAPI.

---

## Planning First Rule

This role must provide a plan before implementation.

If the active User Story has not been approved for implementation, this role must only produce planning output and must not modify implementation code.

Implementation is allowed only after explicit user approval.

---

## Technical Rules

- **Clean Architecture:** Controllers empty (dispatch to Mediator only). Do not put business logic in controllers.
- **CQRS:** Commands (state changes) and Queries (data retrieval) separated.
- **Mediator:** In-house implementation (PROHIBITED: MediatR NuGet).
- **Validation:** FluentValidation in pipeline.
- **Controllers:** Thin. Receive DTOs, return results.
- **Business logic:** In Application/Domain services, NOT in controllers.
- **Async:** Always async/await with CancellationToken.
- **DTOs:** For API input/output.
- **EF Core:** Infrastructure layer only.
- **Migrations:** Generate and apply when models change.
- **Security:** Backend is source of truth for authorization.
- **No secrets in logs, no JWT tokens in logs, no password hashes in responses.**
- **Validate ownership for user-specific resources.**
- **Do not implement business rules only in frontend.**
- **Do not call MCP directly from frontend.**
- **Do not implement code during User Story planning.**
- **Implementation gate: see `AGENTS.md § Required User Story Flow` (`Approved` = new implementation, `Rejected` = rework on the same branch).**
- **Always ask for explicit user approval before implementation.**
- **During planning, update graph status as `Planned`, never as `Implemented`.**

---

## Structure (Required)

workflow/backend/src/
├── Domain/ # Entities, Value Objects, Enums
├── Application/ # Commands, Queries, Handlers, DTOs, Validators
├── Infrastructure/ # EF Core, Repositories, Identity
└── WebAPI/ # Controllers, Middleware, Program.cs

---

## Permissions

- books.{read, create, update, delete}
- rentals.{create, return, view_own, view_all}
- users.manage
- roles.manage
- notifications.read
- chat.use

---

## Checklist

- [ ] Domain Entities
- [ ] DTOs
- [ ] Commands/Queries
- [ ] Handlers
- [ ] Validators (FluentValidation)
- [ ] EF Core configuration
- [ ] Migration
- [ ] Endpoint (Controller)
- [ ] Authorization policy
- [ ] Test manually or with tests
- [ ] Update memory

---

## Forbidden

- Read/modify `bin/` or `obj/`
- Read `.env` (use configuration)
- Expose secrets or stack traces in HTTP responses
- Bypass backend authorization
- Hardcode secrets
- Implement without approved plan

---

## Main Use Cases

This role mainly supports:

- User registration.
- Login with JWT.
- Role and permission management.
- Book search and filtering.
- Book CRUD.
- Book rental with due date.
- Book return.
- Due-date notifications.
