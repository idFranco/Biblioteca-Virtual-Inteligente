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

## Chatbot (ChatWidget)

`src/components/chat/ChatWidget.tsx` + `src/stores/chatWidgetStore.ts`:

- Arranca **minimizado**: solo se muestra el botón flotante «Asistente de la Biblioteca» (abajo a la derecha). Al hacer clic se abre la ventana.
- La ventana abierta permite **maximizar/colapsar** (compacto/grande), **redimensionar** (asas de borde con teclado accesible) y **minimizar** (vuelve al botón flotante).
- El tamaño elegido se persiste en `localStorage`; el estado abierto/cerrado arranca siempre en `false` (minimizado).

## Identidad visual

Tema "Sala de lectura" definido en `src/index.css` (paleta pergamino/madera/latón, tipografía Fraunces + Lora, portadas derivadas de `covers.openlibrary.org` con fallback ornamental). Cambio de presentación únicamente (ADR-021).

## Comandos

```bash
npm install
npm run dev        # desarrollo en http://localhost:5173
npm run build      # build de producción
npm run lint       # oxlint
```