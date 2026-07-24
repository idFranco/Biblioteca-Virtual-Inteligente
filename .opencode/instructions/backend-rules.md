# Backend Rules (C# / .NET 9 / EF Core / SQLite)

## Architectural Constraints
- Do not put business logic in controllers.
- Do not trust frontend permissions.
- Always validate authorization in backend.
- Use DTOs for API input/output.
- Use async/await.
- Always use CancellationToken when possible.
- Never expose password hashes.
- Never log secrets or JWT tokens.
- Keep domain rules explicit.
- Implement a Global Exception Handler (Middleware or IExceptionHandler in .NET 9) to catch all unhandled exceptions.
- Return standardized API errors using RFC 7807 (ProblemDetails).
- Never expose stack traces or internal infrastructure errors in HTTP responses.
- Log critical backend errors locally without exposing sensitive data.
- Implement and propagate a X-Correlation-ID header across all HTTP requests (Frontend -> Backend -> Chatbot -> LLM) to trace transactions end-to-end in logs.
- Configure strict CORS policies (do not allow * in production).
- Implement API Rate Limiting, especially for authentication and chatbot endpoints, to prevent DoS attacks and LLM quota exhaustion.
- Implement structured audit logging for critical business actions (e.g., user registration, role changes, book creation/deletion, and rentals). Log 'Who' did 'What' and 'When'.
- SQLite Concurrency: Explicitly enable WAL (Write-Ahead Logging) mode in the SQLite connection strings for both EF Core (.NET) and Python (Biblioteca-MCP). Configure a reasonable 'Busy Timeout' (e.g., 5000ms) to prevent database is locked exceptions during multi-process access.
- Implement short-lived JWT Access Tokens (e.g., 15 minutes) and secure, revocable Refresh Tokens stored in the database.
- Provide an endpoint to revoke refresh tokens (Logout/Session termination).
- Prevent Mass Assignment (Overposting) by strictly mapping DTOs to Domain Entities (e.g., never accept an IsAdmin flag in a regular user registration payload).
- Implement the CQRS (Command Query Responsibility Segregation) pattern for all business logic. Separate use cases strictly into Commands (state changes) and Queries (data retrieval).
- Implement a custom, in-house Mediator pattern (Dispatcher) to route Commands and Queries to their respective handlers. Strictly forbidden: Do not install or use the external `MediatR` NuGet package.
- Enforce strict validation in the CQRS pipeline using the `FluentValidation` NuGet package. Handlers must only process pre-validated requests.


## Code Conventions (C# / .NET)
- File-scoped namespaces.
- `sealed` classes for concrete services when possible.
- `record` for DTOs.
- Interfaces prefixed with `I`.
- Async methods end with `Async`.
- Controllers should be thin.
- Business logic belongs in Application/Domain services.
- Infrastructure owns EF Core implementations.
- Avoid throwing controlled business exceptions.
- Prefer explicit validation.

## Testing Rules
- Unit tests for domain rules.
- Integration tests for API endpoints when possible.
- Test rental stock behavior.
- Test permissions.

## Forbidden Actions
- Do not read, search, or modify `bin/` or `obj/` directories.
- Do not read `.env` files.
- Do not expose API keys.
- Do not commit SQLite database files.
- Do not bypass backend authorization.
