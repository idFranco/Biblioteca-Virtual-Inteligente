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

## Iteración 2 — Rework por rechazo de QA (qa-check US-010)

- QA rechazó US-010 por fallo del criterio de la Parte A: `openlibrary_verification.json` registraba **50 found / 0 not_found pero solo 14 `matched`** (28%); el dataset sembraba keys que resuelven a obras distintas ("Ficciones"→*The Woman in Black*, "Siddhartha"→*The Moonstone*, etc.), violando ADR-020 ("jamás se siembra una key sin coincidencia").
- Corrección: **30 libros** del dataset `seed-books.json` actualizados a ediciones OL confirmadas con título coincidente (ISBN + `OpenLibraryKey`), y **3 obras sustituidas** por otras confirmadas en OL:
  - "La vida de Galileo" → "Hamlet" (William Shakespeare, `9706660488`/`OL35737312M`, género **Teatro**).
  - "Historia de la conquista del Perú" → "Historia de la conquista de México" (W.H. Prescott, `1020714999`/`OL50770184M`).
  - "La máquina del tiempo" → "El hombre invisible" (H.G. Wells, `9780613830669`/`OL10975654M`).
- Verificación re-ejecutada vía MCP (`ol_verify_by_isbn`): `openlibrary_verification.json` = **50 found / 0 not_found / 50 matched (100%)**; OLIDs 50/50 resuelven en Open Library.
- Re-validación en BD QA aislada: 50 libros, **10 géneros**, 0 duplicados, stock coherente, 1 sin copias, seed idempotente, búsqueda/filtrado OK (Hamlet, Ficciones, Teatro), build backend 0/0, pytest chatbot 26/26 + open-library-mcp 13/13.
- Story `Rejected → In Progress` vía MCP; pendiente re-ejecutar `qa-check US-010`.

## Risk Register (actualización iteración 2)

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| Keys/ISBN del seed que resuelven a obra distinta en OL | Alto | **Resolved** | Dataset corregido con ediciones OL de título coincidente; verificación 50/50 `matched`; 3 obras sustituidas. |
| Homónimos / coincidencia de título incorrecta en OL | Alto | **Resolved** | Coincidencia normalizada confirmada para el 100% del seed. |

## Iteración 3 — QA final PASS (qa-check US-010, 2026-08-15)

- Re-ejecución completa de `qa-check US-010` sobre la rama `feature/US-010-seed-catalog-and-ui`.
- **Capa A (local):** build backend OK con SDK 10.0.400 (`/tmp/opencode/dotnet10`, 0 warnings/0 errors); `npm run build` OK (221ms, assets Fraunces/Lora emitidos); `npm run lint` OK (único warning preexistente `button.tsx:58`); pytest chatbot **26/26** + open-library-mcp **13/13**.
- **Capa B (integración, BD QA aislada `/tmp/opencode/qa-us010.db`, backend `localhost:5002`):**
  - Datos del seed: 50 libros, 10 géneros, 0 duplicados por título/ISBN, `TotalCopies` 1–5, stock coherente, 1 libro sin copias ("Matar a un ruiseñor"), `OpenLibraryKey` 50/50 (100%).
  - Idempotencia: segundo arranque → "La tabla de libros ya contiene datos; seed omitido", 50 libros sin duplicados.
  - UC-5: `search=Don Quijote` → obra encontrada; `genre=Poesía` → "La divina comedia"; `availableOnly=true` → 49 libros, 0 sin copias.
  - Verificación OL: `openlibrary_verification.json` = **summary {total: 50, found: 50, not_found: 0, matched: 50}**; comprobación independiente curl confirmó títulos (De Ratones y Hombres, Los Doce Césares, Peter Pan, Orgullo y prejuicio, Moby Dick vía ISBN).
  - Regresión: auth register/login JWT OK; POST `/api/books` sin `books.create` → **403**; sin token → **401**; CRUD catálogo admin (create→update→delete **204**); alquiler "1984" stock 4→3 y devolución 3→4 con `returnedAt`; solicitud US-009 crear→listar→approve→**Approved**; `/health` → **200**.
  - Identidad visual: paleta cálida en `index.css` (wine/espresso/parchment/brass/olive/ochre), tipografía Fraunces+Lora, 0 ocurrencias de `blue-600`/`gray-*`/`red-600`/`green-100`/`bg-white` en `src/`, Header/Footer `wood-panel` + `brass`/`parchment`.
- **Los 21 criterios (QA-01..QA-21) PASS, incluidos los imprescindibles QA-01..04, QA-07, QA-16..20.**
- Story `In Progress → Implemented` ya cumplida; con este QA se crea el PR vía GitHub MCP (PR Gate) y la story avanza a `Validated`.

## Risk Register (actualización iteración 3)

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| SDK local 9 no compila `net10.0` | Medio | **Resolved** | SDK 10.0.400 instalado en `/tmp/opencode/dotnet10`; build 0 warnings/0 errors. |
| Rate limiting/timeouts de Open Library en verificación masiva | Medio | **Open** | Script serializado (sleep ≥1s) con backoff; verificación 50/50 confirmada; reintentos aplicados durante spot-checks. |
| Seed no idempotente (duplicados al rearrancar) | Medio | **Resolved** | Guard por tabla `Books` vacía; doble arranque verificado → 50 libros sin duplicados. |
| Regresión funcional (rutas, guards, permisos, API) | Medio | **Resolved** | Regresión completa QA-16..19 PASS (auth 401/403, CRUD, alquiler/devolución, solicitudes, `/health`). |
| Portadas de Open Library caídas/404 | Bajo | **Open** | `onError` → `CoverOrnament`; height fija; no bloquea el layout. |
| WAL de SQLite → `database is locked` | Bajo | **Resolved** | Consultas `sqlite3` con backend detenido durante validación de datos. |
