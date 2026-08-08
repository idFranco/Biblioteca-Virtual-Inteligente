# AI Engineering — Iteration Log — bugfix/US-006-mitigacion-riesgos

Story: US-006 — Mitigar riesgos técnicos de US-005 y limpiar la estructura de workflow/opencode
Branch: `bugfix/US-006-mitigacion-riesgos`

## Summary

US-006 mitigó los cuatro riesgos registrados en el Risk Register de US-005 (NU1903, ausencia de endpoint de gestión de roles, falsos 429 por rate limiting y JWT en sessionStorage como constraint académico) y eliminó la carpeta espuria `workflow/opencode/other`.

## Iteration 1 (Implementation)

### Roles participating

- backend-developer (dotnet-clean-architecture, auth-permissions)
- qa (testing-qa)

### What was built

- **NU1903:** pin `SQLitePCLRaw.lib.e_sqlite3` `2.1.12` en `Infrastructure.csproj`; `dotnet list package --vulnerable` → 0. Las versiones 3.x del paquete no eran compatibles con glibc 2.31 (host Debian 11) → 2.1.x línea mantiene el runtime localista; aun así el .so patched exige glibc ≥ 2.34 → ejecución/QA vía Docker (decisión usuario).
- **Endpoint de roles:** `PUT /api/users/{id}/role` (CQRS: `AssignUserRoleCommand` + `AssignUserRoleCommandValidator` + `AssignUserRoleCommandHandler` + `UsersController` con policy `roles.manage`); permiso sembrado en rol `Admin`; `UserManager` para remover/asignar roles; 404 usuario/rol inexistente; 409 ya tiene el rol; 403 sin permiso; 400 validación FluentValidation.
- **Rate limiting auth:** `AUTH_RATE_LIMIT_PER_MINUTE` (default 10) env-configurable en `Program.cs`.
- **JWT sessionStorage:** decisión documentada (constraint académico aceptado con mitigación XSS estricta; sin migración a cookies — fuera de alcance).
- **Limpieza repo:** `git rm -r workflow/opencode/other`.

## Risk Register (Riesgos)

| Severidad | Área | Riesgo | Estado |
|---|---|---|---|
| HIGH | backend/Infrastructure | NU1903 — `SQLitePCLRaw.lib.e_sqlite3` <2.1.12 (GHSA-2m69-gcr7-jv3q / CVE-2025-6965) | **Mitigado** — pin 2.1.12; 0 vulnerables en audit NuGet |
| MED | backend/WebAPI | Endpoint `roles.manage` ausente → promoción de rol por edición directa de DB en pruebas | **Mitigado** — endpoint `PUT /api/users/{id}/role` (Admin) |
| LOW | backend/WebAPI | Falsos 429 en baterías de pruebas (límite auth fijo de 10/min) | **Mitigado** — `AUTH_RATE_LIMIT_PER_MINUTE` configurable |
| LOW | frontend | JWT en sessionStorage (constraint académico; HttpOnly preferible) | **Aceptado con mitigación** (sin dangerouslySetInnerHTML, logout limpia, SameOrigin) |
| LOW | runtime | `.so` patched exige glibc ≥ 2.34; host Debian 11 tiene 2.31 | **Aceptado con mitigación** — ejecución/QA vía contenedor `dotnet/aspnet:10.0` |

## QA Validation (Iteration 1)

- Batería ejecutada con contenedor Docker (host + glibc constraint): health 200; assigns roles 200/403/400/404/401/409; re-login refleja nuevo rol; `AUTH_RATE_LIMIT_PER_MINUTE=3` → 429 en request 4+ y 5; `/health` no limitado; `git ls-tree` sin `other/`; frontend build+lint OK.
- Detalle completo: ver `workflow/opencode/user-stories/US-006.md` → QA Result.

## Result

- Implementación completa; PR creado en GitHub; story avanzada a `Validated`.
- NuGet audit clean, builds clean (0/0), sin regresión frontend.