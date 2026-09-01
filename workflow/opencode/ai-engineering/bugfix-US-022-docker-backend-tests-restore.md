# Iteration Log — bugfix/US-022-docker-tests-restore

## 2026-09-01 — qa-check US-022 → PASS

- **Story:** US-022 — Corregir build de Docker del backend por referencia al proyecto de tests en la solución.
- **Rama:** `bugfix/US-022-docker-tests-restore`.
- **Verdicto global:** PASS — los 4 criterios de aceptación pasan.

### Criterios de aceptación
- **AC#1 `docker compose build backend` tiene éxito tras el fix** — ✅ PASS
  - `docker compose build backend` → exit 0; imagen `biblioteca-virtual-backend:stable` creada.
- **AC#2 El error MSB3202 desaparece de la capa de restore** — ✅ PASS
  - Build `--no-cache --target build` (fuerza restore completo): ninguna mención de `MSB3202`; salida `Restored /src/src/...` y `Restored /src/tests/BibliotecaVirtual.Tests/BibliotecaVirtual.Tests.csproj`; todos los proyectos de `BibliotecaVirtual.slnx` restaurados.
- **AC#3 El proyecto de tests no se incluye en la imagen runtime** — ✅ PASS
  - `docker run --rm biblioteca-virtual-backend:stable ls /app` → contiene `BibliotecaVirtual.WebAPI.dll` y dependencias; NO contiene `BibliotecaVirtual.Tests.dll` ni artefactos de test.
- **AC#4 El build y los tests locales siguen pasando (regresión)** — ✅ PASS
  - `dotnet build BibliotecaVirtual.slnx` → 0 errores / 0 warnings.
  - `dotnet test BibliotecaVirtual.slnx` → 13 passed (proyecto `tests/BibliotecaVirtual.Tests`).

### Evidencia clave
- El cambio implementado es la línea `COPY tests/BibliotecaVirtual.Tests/BibliotecaVirtual.Tests.csproj tests/BibliotecaVirtual.Tests/` en `workflow/backend/Dockerfile`, entre `COPY src/WebAPI/...` y `RUN dotnet restore`.
- `dotnet publish src/WebAPI/BibliotecaVirtual.WebAPI.csproj` es project-scoped; la capa runtime (`COPY --from=build /app .`) no incluye el proyecto de tests.
- Se verificó (en planificación/implementación) que frontend y chatbot no presentan el bug análogo y que el `.dockerignore` del backend no excluye `tests/`.

### Documentation Gate
Cumplido — `## QA Result` documentado en `US-022.md` (reemplazado el `Pending`; `## Implementation Notes` verificadas sin modificar). El plan documental de US-022 no requiere cambios en READMEs (fix sin impacto de comportamiento documentado), conforme al plan.

### Observaciones no bloqueantes
- El gate de imágenes Docker requiere daemon Docker en ejecución (prerrequisito de entorno, no de código). Disponible en esta validación.
- Sin PR aún; la creación vía GitHub MCP es el siguiente paso previo a `Validated`.

### Siguiente paso
PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.