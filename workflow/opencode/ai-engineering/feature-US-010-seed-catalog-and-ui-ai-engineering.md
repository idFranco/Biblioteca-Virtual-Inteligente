# AI Engineering — Bitácora de iteración — US-010 (rama `feature/US-010-seed-catalog-and-ui`)

## Iteración 1 — Implementación inicial

- Story `Approved → In Progress`; rama `feature/US-010-seed-catalog-and-ui`.
- Backend: seeder idempotente `ICatalogSeeder`/`CatalogSeeder` (`Infrastructure/Data/Seed`), `Application/Contracts/Seed/` (`SeedBookDto`, `SeedBookValidator` FluentValidation, `CatalogSeedResult`), invocado en `Program.cs` tras `EnsureCreated` + roles + admin; config `CatalogSeed:Enabled`/`CatalogSeed:FilePath`; dataset `workflow/backend/data/seed-books.json` como fuente única (50 obras reales, 9 géneros, `TotalCopies` 1–5, al menos 1 libro con 0 copias, ISBN-13 únicos + `OpenLibraryKey` verificadas en forma OLID desnudo).
- Open Library MCP: nueva tool `ol_verify_by_isbn(isbn)` (`GET /api/books?bibkeys=ISBN:...&format=json&jscmd=data` → `{isbn, found, open_library_key, title}`), refactor `_get_json`/`_extract_edition_key` con cliente inyectable; script one-off `workflow/scripts/verify_seed_open_library.py` (reutiliza `McpStdioClient`, sleep ≥1s, backoff, timeout por env).
- Frontend: identidad "Sala de lectura" en `src/index.css` (paleta cálida/añeja `:root` + `.dark`), tipografía Fraunces Variable + Lora Variable, portadas derivadas de ISBN/OLID con fallback ornamental, componentes nuevos (`lib/utils.ts`, `lib/covers.ts`, `ui/*`, `books/BookCard`, `books/CoverOrnament`, `layout/PageHeader`, `pages/HomePage`) y migración de colores hardcodeados a tokens en Header/Footer/Layout/7 páginas/ChatWidget/CreateRentalDialog/RequestStatusBadge/ruta índice.
- Build backend OK (SDK 10.0.302 `/tmp/opencode/dotnet10`, 0 warnings/0 errors); frontend `npm run build` OK + `npm run lint` OK (solo warning pre-existente `button.tsx` documentado); pytest open-library-mcp **13/13**.

## QA 0 / Validación de datos (dev)

- Verificación del seed contra Open Library ejecutada y registrada en `workflow/database/openlibrary_verification.json` (no versionado): **50 total, 50 encontrados, 0 no encontrados, 14 títulos coincidentes**. Cobertura `OpenLibraryKey` 100%.
- Consultas en BD QA aislada (`/tmp/opencode/qa-us010.db`): 50 libros, 9 géneros, 0 duplicados por título/ISBN, `OpenLibraryKey` 50/50 distintas y no vacías, 1 libro sin copias disponibles ("Matar a un ruiseñor"), set de OL keys igual al dataset. Idempotencia estructural: `CatalogSeeder` guarda por tabla `Books` no vacía.

## Risk Register

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| Contraste WCAG de la paleta cálida | Alto | Mitigated | Cuerpo en espresso `#33241A`; validación de pares de tokens. |
| Swap incompleto de colores hardcodeados | Alto | Mitigated | Barrido por archivo; 0 ocurrencias de `blue-600`/`gray-*`/`red-600`/`green-100`/`bg-white`; revisión de diff por página. |
| Regresión funcional (rutas, guards, permisos, API) | Alto | Mitigated | Solo cambios de presentación; `services/`/`stores/`/guardias intactos; build + lint OK. |
| Homónimos/coincidencia de título incorrecta en OL | Alto | Mitigated | Validación de coincidencia normalizada; `found: false` con título real para decisión humana. |
| Ruta del API de solicitudes heredada (US-009) | Alto | Mitigated | Resuelta en US-009 (Rework 3); sin efecto en US-010. |
| Rate limiting/timeouts de Open Library en verificación masiva | Medio | Open | Script serializado (sleep ≥1s), reintentos con backoff, timeout por env, fallback `ol_search_books`. |
| Seed no idempotente (duplicados al rearrancar) | Medio | Open | Guard por tabla `Books` vacía; verificado por inspección. |
| `EnsureCreated()` sin migraciones pierde el seed | Medio | Open | Sin cambios de esquema; seeder idempotente; borrar `.db` regenera schema + seed. |
| SDK local 9 no compila `net10.0` | Medio | Open | Usar `/tmp/opencode/dotnet10/dotnet` (10.0.302). |
| Portadas de Open Library caídas/404 | Bajo | Open | `onError` → `CoverOrnament`; height fija; no bloquea el layout. |
| WAL de SQLite → `database is locked` | Bajo | Open | Consultas `sqlite3` en modo read-only o con backend detenido. |

## Cierre (iteración de implementación)

- Builds verificados (backend 0/0, frontend OK, pytest 13/13), datos de seed validados contra BD QA y Open Library.
- Ramas sincronizadas; story avanzada a `Implemented` vía MCP.
- Pendiente: fase `qa-check US-010` (PR vía GitHub MCP `create_pull_request`, actualización de `## QA Result`, docs y bitácora finales, story → `Validated`).
