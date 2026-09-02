# Frontend — React 18 + TypeScript + Vite

SPA de la Biblioteca Virtual Inteligente en `workflow/frontend/`, construida con **React 18**, **TypeScript** estricto, **Vite**, **Tailwind CSS** (identidad "Sala de lectura"), **shadcn/ui**, **Zustand** y **React Router v6** (ADR-010).

## Estructura

```
workflow/frontend/
├── src/
│   ├── routes/             # Router + guardas (ProtectedRoute, PermissionGuard)
│   ├── pages/              # Catálogo, libros, alquileres, solicitudes, sala de lectura, auth
│   ├── components/         # UI (chat, books, rentals, layout, ui, requests)
│   ├── services/           # Clientes API (auth, books, rentals, bookRequests, chat)
│   ├── stores/             # Zustand (authStore, chatWidgetStore)
│   ├── config/env.ts       # Variables de entorno requeridas (fail-fast)
│   ├── lib/                # Utilidades (cn, covers)
│   └── types/              # Tipos compartidos
├── Dockerfile              # Build multi-stage (node → nginx)
└── nginx.conf              # SPA fallback + puerto 5173
```

## Configuración por variables de entorno (fail-fast)

Las URLs base se leen de variables de entorno **sin valor por defecto** (`src/config/env.ts`). Si falta una, el build aborta con un mensaje claro (ADR-025).

| Variable | Requerida | Descripción |
|---|---|---|
| `VITE_API_BASE_URL` | Sí | URL base de la API backend (p. ej. `http://localhost:5000`) |
| `VITE_CHATBOT_API_BASE_URL` | Sí | URL base del chatbot FastAPI (p. ej. `http://localhost:8000`) |

- **Desarrollo local:** define ambas en un `.env.local` (ignorado por Git) antes de `npm run dev`.
- **Docker:** se inyectan en build time vía `ARG VITE_API_BASE_URL` / `ARG VITE_CHATBOT_API_BASE_URL` (sin defaults) en el `Dockerfile`; `docker-compose.yml` las pasa por `build.args`.

## Roles y permisos en la UI

- **Catálogo (`/catalog`):** el botón **«Alquilar»** aparece solo para libros disponibles y solo si el usuario tiene el permiso `rentals.create` (el rol Admin no lo tiene, por lo que no puede alquilar).
- **Solicitudes de libros (`/admin/gestion-libro`):** visible para quienes tienen `books.manage`.
- **Mis alquileres (`/mis-alquileres`):** solo con `rentals.view_own` (el rol Admin no lo tiene).
- La seguridad real la garantiza el backend; la UI solo oculta/condiciona por permisos (ADR-003).

## Sala de lectura con contenido (US-021)

`pages/SalaLecturaPage.tsx` renderiza el **contenido real** del libro alquilado (`BookForReadingResponse.content`, ADR-041) con tipografía de lectura: fondo "papel" (`texture-grain`, `bg-paper dark:bg-wood-dark`), columna `max-w-prose` centrada, `font-serif`, `whitespace-pre-line`, `leading-relaxed`. Cuando el libro **no tiene `Content`**, se muestra un **placeholder informativo on-brand** (ornamento + `BookOpen` + `book.description`) — nunca una pantalla en blanco. Mantiene la ficha superior y el botón "Volver a mis alquileres".

## Devolución self-service en Mis alquileres (US-021)

`pages/MisAlquileresPage.tsx` muestra un botón **«Devolver»** por fila cuando `Status == Active | Overdue` y el usuario puede devolver: `canReturn = permissions.includes('rentals.return') || permissions.includes('rentals.view_own')` (política `rentals.return_own`, ADR-039). Incluye confirmación (`window.confirm`), estado `returningId` con "Devolviendo..." y refresco de stock tras `rentalsService.returnRental(rental.id)`. `AlquileresAdminPage` (staff) permanece intacta.

## Solicitar título + Mis solicitudes (US-021)

- **Diálogo `BookRequestDialog`** (`components/requests/`): campos título ⚠, autor ⚠, ISBN opcional; submit → `bookRequestsService.createRequest({title, author, isbn})`; estados `submitting`/`error`; estética on-brand. Entradas en: (a) el **estado vacío de búsqueda** del catálogo (`books.length === 0`), (b) la **ficha de un libro sin copias disponibles**, (c) un **enlace en el Header** visible con `books.request` (los 3 roles).
- **Mis solicitudes (`/mis-solicitudes`):** página ligera `pages/MisSolicitudesPage.tsx` que consume `GET /api/book-requests/mine` con badges de estado Pending/Approved/Rejected; ruta protegida por `books.request`.
- Reutiliza los endpoints backend existentes (sin cambios backend, ADR-042); la prevención de duplicados pendientes (409) se mantiene.

## Chatbot (ChatWidget)

`src/components/chat/ChatWidget.tsx` + `src/stores/chatWidgetStore.ts`:

- Arranca **minimizado**: solo se muestra el botón flotante «Asistente de la Biblioteca» (abajo a la derecha). Al hacer clic se abre la ventana.
- La ventana abierta permite **maximizar/colapsar** (compacto/grande), **redimensionar** (asas de borde con teclado accesible) y **minimizar** (vuelve al botón flotante).
- El tamaño elegido se persiste en `localStorage`; el estado abierto/cerrado arranca siempre en `false` (minimizado).
- **CORS:** el origen de la SPA (p. ej. `http://localhost:5173`) debe estar listado en `CORS_ORIGINS` del servidor del chatbot para que el navegador no bloquee el `fetch` a `VITE_CHATBOT_API_BASE_URL`; no se requieren cambios de código en el frontend.

### Contrato `userId` (chatbot ↔ Biblioteca-MCP)

`getChatUserId()` en `src/services/chat.ts` devuelve el `userId` enviado a `POST /chat`, tomado **verbatim** del claim JWT `sub` (`useAuthStore.getState().user?.id`), sin transformación de case (ADR-037). El frontend **no normaliza** el case ni el formato del id: la comparación case-insensitive es responsabilidad exclusiva de Biblioteca-MCP (`UPPER(UserId) = UPPER(?)` + `registrar_feedback` en minúsculas), de modo que la recomendación personalizada funciona con `93C1CA75-...` y `93c1ca75-...`. Devuelve `null` cuando no hay sesión activa.

## Identidad visual

Tema "Sala de lectura" definido en `src/index.css` (paleta pergamino/madera/latón, tipografía Fraunces + Lora, portadas derivadas de `covers.openlibrary.org` con fallback ornamental). Cambio de presentación únicamente (ADR-021).

## Docker (HEALTHCHECK)

El `Dockerfile` (multi-stage: node → nginx) incluye un `HEALTHCHECK` que comprueba `http://127.0.0.1:5173/` con `wget` cada 30 s (timeout 5 s, 3 reintentos). Esto permite que `docker compose` con `depends_on: condition: service_healthy` detecte si el frontend no arrancó correctamente y detenga la pila en modo fail-fast global (US-025).

## Comandos

```bash
npm install
npm run dev        # desarrollo en http://localhost:5173
npm run build      # build de producción
npm run lint       # oxlint
```
