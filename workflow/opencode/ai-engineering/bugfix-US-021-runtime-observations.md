# Iteration Log — bugfix/US-021-runtime-observations

## 2026-09-01 — qa-check US-021 → PASS

- **Story:** US-021 — Corregir observaciones de runtime: guía conversacional del chatbot, JWT, restricción de alquileres, lectura en sala de lectura, devolución desde el usuario y solicitud de títulos.
- **Rama:** `bugfix/US-021-runtime-observations`.
- **Verdicto global:** PASS — los 5 escenarios de aceptación pasan.

### Escenarios de aceptación
- **1a — Guía conversacional al lector principiante** — ✅ PASS
  - Intención `guidance` en `classify_intent_node.py` evaluate antes de smalltalk/recommendation/book_query.
  - `guidance_node.py` consulta `buscar_libros` reales + `generate_guidance` + fallback heurístico `_guidance_fallback` que referencia **solo títulos reales** (nunca inventa).
  - `guide_prompt.txt` prohíbe explícitamente inventar títulos y prohibe hablar de credenciales.
  - Tests: `test_guidance.py` (6) — clasificación, catálogo real, fallback LLM, no-inventa-títulos, MCP caído, regresión smalltalk.
- **1b — Rechazo de JWT/credenciales** — ✅ PASS
  - Nodo determinista `credential_guard_node.py` (defensa en profundidad) tras `audit_input` y antes de todo razonamiento LLM; normalización Unicode NFKD + tokenización (evita falso negativo de `re` con acentos).
  - Patrones ES+EN con verbos de petición; `GUARD_RESPONSE` fijo, cortés, sin credenciales; `guard_triggered` en estado transitorio y reseteado en `reset_turn_node`.
  - Wiring `audit_input → credential_guard → {guard: audit_output | process: load_user_state}`; la guardia pasa por `audit_output` (auditoría de salida intacta, ADR-008/034).
  - Security-Audit-MCP: `local_audit.py` ampliado con `jwt|token|sesión|session|cookie`; test `test_audit_blocks_jwt_request` en suite security-audit-mcp (26 passed).
  - Tests: `test_credential_guard.py` (incluye BT no-falso-positivo con "token" en contexto de libro, respuesta fija, audit_output ejecutado, auditoría no debilitada).
- **2 — Restricción de alquileres en backend** — ✅ PASS
  - `CreateRentalCommandHandler`: 409 por título activo duplicado (case-insensitive `ToLower`, distintas filas `Book`) + tope `Rentals__MaxActivePerUser` (default 5) → 409; ambos sin decrementar stock.
  - appsettings `Rentals.MaxActivePerUser=5` + override por env `Rentals__MaxActivePerUser` vía `GetInt`.
  - Tests xUnit: `CreateRental_RejectsDuplicateActiveRental_SameBook`, `SameTitle_DifferentBookId`, `AllowsDifferentTitle`, `RejectsWhenMaxConcurrentReached`, `AllowsBelowMaxConcurrent`.
- **3 — Sala de lectura con contenido** — ✅ PASS
  - `Book.Content` (TEXT) + `BookForReadingResponse.content` + mapeo en `GetBookForReadingQueryHandler`.
  - Alineación de esquema idempotente `AlignSchemaAsync` (PRAGMA table_info + ALTER TABLE ADD COLUMN si falta) sin regenerar BD.
  - Validators `MaximumLength(100000)` en Create/Update.
  - Frontend `SalaLecturaPage` renderiza `content` (bg-paper, max-w-prose, font-serif, whitespace-pre-line) con placeholder on-brand (BookOpen + ornament + description) cuando vacío.
  - Tests: `Leer_ConAlquilerActivo_DevuelveContenido`, `Leer_SinAlquilerActivo_LanzaKeyNotFound`.
- **4 — Devolución self-service por propiedad** — ✅ PASS
  - Política `rentals.return_own` (rentals.return OR rentals.view_own); `ReturnRentalCommand(RequesterUserId, CanReturnAny)`.
  - Handler: `if (!CanReturnAny && UserId != RequesterUserId) → KeyNotFoundException` (404 anti-enumeración, mensaje idéntico al not-found).
  - Frontend `MisAlquileresPage`: botón "Devolver" gated por `rentals.view_own`/`rentals.return`, confirmación, `returningId` con "Devolviendo...", recarga tras devolución, solo Active/Overdue.
  - Tests: propio OK, ajeno → KeyNotFound, bibliotecario ajeno OK, ya devuelto → Conflict, restaura stock.
- **5 — Solicitud de títulos visible** — ✅ PASS
  - `BookRequestDialog` (title/autor obligatorios, ISBN opcional) con entradas en catálogo vacío, ficha sin copias, y Header (gated `books.request`).
  - `MisSolicitudesPage` + ruta `/mis-solicitudes` gated por `books.request`; badges Pending/Approved/Rejected.
  - Reutiliza endpoints existentes (POST /api/book-requests, GET /mine).

### Evidencia clave (gates)
- `dotnet build` 0 errores / 0 warnings.
- `dotnet test` → 13 passed (proyecto nuevo `BibliotecaVirtual.Tests`).
- `npm run build` (con `VITE_API_BASE_URL`/`VITE_CHATBOT_API_BASE_URL`) OK · `npm run lint` OK.
- pytest chatbot → **122 passed** · security-audit-mcp → **26 passed** · biblioteca-mcp → **15 passed** · open-library-mcp → **18 passed**.

### Documentation Gate
Cumplido — `## QA Result` documentado en `US-021.md` (reemplazado el `Pending`; `## Implementation Notes` verificadas sin modificar).

### Observaciones no bloqueantes
- No se realizó smoke E2E live (requiere stack docker + Ollama :11434 levantados); los escenarios de aceptación se cubren con la suite de tests (unitarios + grafo) y verificación estática de archivos.
- Lint muestra 1 warning preexistente (`react(only-export-components)` en `button.tsx`), no relacionado con esta historia y no bloqueante.

### Siguiente paso
PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
