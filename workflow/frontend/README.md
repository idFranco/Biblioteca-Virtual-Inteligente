# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some Oxlint rules.

## Configuración de entorno

La URL base de la API se define con la variable de entorno `VITE_API_BASE_URL`. Se lee, con fallback a `http://localhost:5000`, desde el módulo `src/config/env.ts`, usado por los clientes API (`src/services/api.ts`, `src/services/auth.ts`).

- **Desarrollo local:** define la variable en un archivo `.env.local` (ignorado por Git) antes de `npm run dev`, p. ej. `VITE_API_BASE_URL=http://localhost:5000`.
- **Docker:** el valor se inyecta en build time vía `ARG VITE_API_BASE_URL` / `ENV VITE_API_BASE_URL` en el `Dockerfile`; `docker-compose.yml` lo pasa a través de `build.args.VITE_API_BASE_URL`.

## Tema / Identidad visual

La SPA usa la identidad **"Sala de lectura"** (librería tradicional), definida exclusivamente en el frontend mediante tokens de tema en `src/index.css` (`@theme` / `:root` / `.dark`), conservando la arquitectura de CSS variables de shadcn/ui.

- **Paleta (light y dark):** fondos crema/pergamino (`parchment`, `paper`), marrones cálidos de madera/cuero (`espresso`, `wine`, `wood`), acentos ámbar/dorado (`brass`, `ochre`) y verde musgo (`olive`, `oxide`), con tonos `tan`/`sepia` para metadatos.
- **Tipografía:** Fraunces Variable (display/serif) para títulos y encabezados; Lora Variable (serif) para cuerpo, instaladas vía `@fontsource-variable/fraunces` y `@fontsource-variable/lora`.
- **Portadas de libros:** derivadas en cliente desde ISBN o OLID (`src/lib/covers.ts`) usando `covers.openlibrary.org` (`b/isbn/{isbn}-M.jpg` → `b/olid/{olid}-M.jpg`), con `referrerPolicy="no-referrer"` y fallback ornamental (`CoverOrnament`) ante error; altura fija para no romper el layout.
- **Componentes temáticos:** `StatusBadge` (badges de disponibilidad/alquiler/solicitud), `Pagination`, `PageHeader`, `BookCard`, `CoverOrnament`.
- **Alcance:** cambio de presentación únicamente — no altera rutas, guardias de permisos, `services/`, `stores/authStore.ts` ni contratos de API (ADR-021).

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the Oxlint configuration

If you are developing a production application, we recommend enabling type-aware lint rules by installing `oxlint-tsgolint` and editing `.oxlintrc.json`:

```json
{
  "$schema": "./node_modules/oxlint/configuration_schema.json",
  "plugins": ["react", "typescript", "oxc"],
  "options": {
    "typeAware": true
  },
  "rules": {
    "react/rules-of-hooks": "error",
    "react/only-export-components": ["warn", { "allowConstantExport": true }]
  }
}
```

See the [Oxlint rules documentation](https://oxc.rs/docs/guide/usage/linter/rules) for the full list of rules and categories.
