# AI Engineering — Bitácora de iteración — US-011 (rama `feature/US-011-reading-room-and-chatbot-resize`)

## Iteración 1 — Implementación inicial

- Story `Approved → In Progress`; rama `feature/US-011-reading-room-and-chatbot-resize`.
- **Backend (CQRS + Dispatcher propio, sin MediatR):**
  - `GetBookForReadingQuery(BookId, UserId) : BaseQuery<BookForReadingResponse>`.
  - `BookForReadingResponse` (BookResponse + `RentedAt`, `DueDate`).
  - `GetBookForReadingQueryHandler`: autorización por alquiler NO devuelto (`ReturnedAt == null`); `KeyNotFoundException` → 404 vía `GlobalExceptionHandler`.
  - Endpoint `GET /api/books/{bookId:guid}/reading` en `BooksController` (policy `books.read`, `UserId` del claim).
  - Registro del handler en `DependencyInjection.cs`. Sin migraciones.
- **Frontend (frontend-ui-ux, identidad "Sala de lectura" ADR-021):**
  - `BookCover` reutilizable: skeleton + `onError` + detección de portada en blanco (`naturalWidth/naturalHeight < 30`); causa raíz: `covers.openlibrary.org` devuelve placeholder blanco (no 404). `BookCard` refactorizado.
  - `SalaLecturaPage` + ruta `/sala-lectura/:bookId` (guard `rentals.view_own` + `books.read`).
  - Acción "Leer" en `MisAlquileresPage` para alquileres `Active`/`Overdue`.
  - Chatbot redimensionable: store Zustand (`chatWidgetStore.ts`) persistido en `localStorage` + `ChatWidget` con botón expandir/colapsar y asas de redimensionado (arrastre + teclado).
- Build backend OK (SDK .NET 10, 0 warnings/0 errors); frontend `npm run build` OK + `npm run lint` OK (solo warning preexistente `button.tsx`).

## Risk Register

| Risk | Nivel | Estado | Mitigación aplicada |
|---|---|---|---|
| Autorización incorrecta de la sala de lectura (Overdue post-devolución) | Alto | **Resolved** | Detectado en smoke test: `Status != Returned` permitía acceso a libros devueltos tarde (`Status=Overdue`). Corregido a `ReturnedAt == null`. |
| Portadas en blanco (placeholder de Open Library) | Medio | Mitigated | Detección por tamaño natural + `onError` + `CoverOrnament` como fallback final. |
| Contenido de lectura limitado a la descripción | Medio | Documented | Decisión explícita: la sala de lectura muestra la `Description` persistida; full-text fuera de alcance. |
| Redimensionado del chatbot rompe layout móvil | Medio | Mitigated | `max-w-[calc(100vw-1rem)]` / `max-h-[calc(100vh-1rem)]` con clamp de anchos. |
| Regresión del flujo de alquiler (US-005) | Bajo | Mitigated | Smoke test de alquiler/devolución en BD aislada; sin cambios en handlers de alquiler. |

## Validación runtime (BD aislada `/tmp/opencode/qa-us011.db`, backend localhost:5002)

- Registro/login `qaread@test.local` (Usuario) y login `qaadmin@test.local` (Admin seed).
- Alquiler de libro → `GET /api/books/{id}/reading` con token → **200** (libro + `rentedAt` + `dueDate`).
- Usuario sin alquiler → **404**; sin token → **401**.
- Devolución por Admin (el rol `Usuario` no tiene `rentals.return`) → `reading` → **404**.
- `npm run build` OK; `npm run lint` OK.

## Cierre (iteración de implementación)

- Builds verificados (backend 0/0, frontend OK), smoke test del endpoint de lectura OK.
- Ramas sincronizadas; story avanzada a `Implemented` vía MCP.
- Pendiente: fase `qa-check US-011` (validación formal, PR vía GitHub MCP `create_pull_request`, actualización de `## QA Result`, docs finales y story → `Validated`).