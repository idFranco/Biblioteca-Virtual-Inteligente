# Skill Dotnet Clean Architecture

## Purpose

Use this skill when implementing backend features in ASP.NET Core Web API.

## Stack

- .NET 9
- ASP.NET Core Web API
- Entity Framework Core
- SQLite
- Identity
- JWT

## Rules

- Keep controllers thin.
- Put business logic in Application or Domain.
- Infrastructure owns EF Core.
- Domain must not depend on Infrastructure.
- Use DTOs for API contracts.
- Use async/await.
- Use CancellationToken.
- Validate permissions in backend.
- Do not expose internal EF entities directly if DTOs are needed.

## Checklist

1. Define domain entity.
2. Define DTOs.
3. Define service or handler.
4. Define repository if needed.
5. Add EF configuration.
6. Add migration.
7. Add endpoint.
8. Add authorization policy.
9. Add tests or manual validation.
10. Update memory.
