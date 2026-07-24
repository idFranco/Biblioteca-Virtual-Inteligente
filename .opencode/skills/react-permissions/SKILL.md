# Skill React Permissions

## Purpose

Use this skill for React + TypeScript frontend development.

## Rules

- Use strict TypeScript.
- Keep API calls in `services/`.
- Keep auth state in Context or Zustand.
- Use protected routes.
- Use permission guards.
- Do not implement real security only in frontend.
- Avoid `any`.
- Store JWT tokens securely. Prefer HttpOnly cookies for token storage. If localStorage or sessionStorage must be used due to academic constraints, implement strict XSS mitigations.

## Suggested Structure

src/
├── components/
├── pages/
├── routes/
├── services/
├── hooks/
├── contexts/
├── types/
└── lib/

## Required Components

ProtectedRoute
PermissionGate
AppLayout
LoginPage
RegisterPage
BookCatalogPage
BookAdminPage
RentalsPage
NotificationsPage
ChatWidget

## Checklist

1. Add API client.
2. Add auth context/store.
3. Add protected routes.
4. Add permission-based rendering.
5. Add pages.
6. Validate with test users.
