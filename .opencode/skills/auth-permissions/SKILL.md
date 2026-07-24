# Skill Auth Permissions

## Purpose

Use this skill for users, roles, claims, policies, JWT and protected endpoints.

## Roles

Admin
Bibliotecario
Usuario

## Permissions

books.read
books.create
books.update
books.delete
rentals.create
rentals.return
rentals.view_own
rentals.view_all
users.manage
roles.manage
notifications.read
chat.use

## Rules

- Backend is the source of truth.
- Frontend permission checks are UX only.
- JWT must include user id, roles and permissions.
- Never expose password hashes.
- Never log JWT tokens.
- Use policies for critical operations.
- Implement short-lived JWT Access Tokens (e.g., 15 minutes) and secure, revocable Refresh Tokens stored in the database.
- Provide an endpoint to revoke refresh tokens (Logout/Session termination).

## Checklist

1. Add permission constants.
2. Add claims to roles.
3. Seed roles and permissions.
4. Protect endpoints.
5. Return permissions in `/api/auth/me`.
6. Verify frontend receives permissions.
