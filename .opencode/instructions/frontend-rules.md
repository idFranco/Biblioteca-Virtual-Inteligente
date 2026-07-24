# Frontend Rules (React / TypeScript / Tailwind)

## Architectural Constraints
- Use TypeScript types for API responses.
- Keep API calls inside `services/`.
- Keep route protection inside `routes/`.
- Do not duplicate business rules from backend.
- UI hiding by permission is allowed, but backend must enforce security.
- Never hardcode secrets.
- Avoid large components.
- Prefer small reusable components.
- Store JWT tokens securely. Prefer HttpOnly cookies for token storage. If localStorage or sessionStorage must be used due to academic constraints, implement strict XSS mitigations.

## Code Conventions (TypeScript / React)
- Use strict TypeScript.
- Prefer named exports.
- API clients live in `services/`.
- Shared types live in `types/`.
- Protected routes live in `routes/`.
- Permission guards must be reusable.
- Never use `any`.
- Strongly typed model
- Avoid business rules only in frontend.

## Testing Rules
- Test route guards.
- Test permission-based rendering.
- Test critical flows manually if automated tests are out of scope.

## Forbidden Actions
- Do not read, search, or modify `node_modules/`.
- Do not call MCP directly from frontend.
