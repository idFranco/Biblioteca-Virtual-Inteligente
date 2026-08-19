# DECISIONS

## ADR-001 — Use SQLite

SQLite is used because it is portable, simple, and suitable for academic delivery.

## ADR-002 — Use ASP.NET Core Identity + JWT

Identity provides user and role infrastructure. JWT enables stateless frontend authentication.

## ADR-003 — Use permissions as claims

Roles alone are not enough. Permissions are represented as claims and enforced through policies.

## ADR-004 — Use FastAPI for chatbot

FastAPI is used because LangChain and LangGraph have strong Python support.

## ADR-005 — Use LangGraph

The chatbot must be modeled as a graph, not a linear prompt chain.

## ADR-006 — Use MCP

MCP separates agent tools from business logic and external APIs.

## ADR-007 — Frontend does not call MCP directly

Only the chatbot or development agents can call MCP tools.

## ADR-008 — Add Security-Audit-MCP

A dedicated MCP server audits chatbot input and output to detect prompt injection, malicious requests and sensitive-data exposure. It runs as the first and last step of the LangGraph flow and complements, but does not replace, backend authorization.

## ADR-009 — Backend Clean Architecture with CQRS + Custom Mediator

The backend follows Clean Architecture with four projects: Domain (innermost, no dependencies), Application (CQRS Commands/Queries/Handlers + FluentValidation), Infrastructure (EF Core, Identity, JWT), and WebAPI (ASP.NET host + Controllers). Commands and Queries are routed via a custom in-house `Dispatcher` class; the external `MediatR` NuGet package is strictly forbidden.

## ADR-010 — Frontend Tech Stack: Vite + React 18 + TypeScript + Tailwind CSS + shadcn/ui + Zustand + React Router

The frontend uses Vite as the build tool (fast HMR, native ESM), React 18 with strict TypeScript throughout, Tailwind CSS v3+ for utility-first styling, shadcn/ui for reusable accessible components, Zustand for global state management, and React Router v6 for client-side routing with nested layouts and route guards.

## ADR-011 — Chatbot Backend: FastAPI + LangChain + LangGraph

The chatbot runs as an independent Python FastAPI service in `workflow/chatbot/`. LangChain provides the LLM abstraction and tool integration layer; LangGraph models conversation flows as directed state-graphs. Persistent conversational memory is stored via the Biblioteca-MCP server. The chatbot never calls the core database directly — all data access goes through MCP tools.

## ADR-012 — Repository Layout: Monorepo with `workflow/` Prefix

All application source code lives under the `workflow/` directory at the repository root. The `workflow/backend/`, `workflow/frontend/`, `workflow/chatbot/`, `workflow/mcp/`, `workflow/database/`, and `workflow/opencode/` directories each contain their respective modules. No source code or build artifacts are placed at the repository root (except `.opencode/`, config files, and Docker Compose).

## ADR-013 — Multi-Container Orchestration with Docker Compose

All services (Frontend, Backend, Chatbot, and MCP servers) run as separate Docker containers defined in a root-level `docker-compose.yml`. Each service has its own `Dockerfile` in its respective `workflow/<module>/` directory.

## ADR-014 — MCP Activation Gating in opencode.json

MCP servers defined in `opencode.json` remain with `"enabled": false` until their corresponding User Story is validated. biblioteca-mcp is enabled when its US is validated; security-audit-mcp similarly; open-library similarly.

## ADR-015 — Nginx serves the SPA on port 5173 with SPA fallback

The frontend container runs a custom `nginx.conf` that listens on port `5173` (matching compose, `EXPOSE`, and the CORS origin) and serves the built SPA with `try_files $uri $uri/ /index.html` so React Router routes do not 404 on refresh. The `5173:5173` compose mapping is the single source of truth; nginx's conventional internal port 80 is deliberately not used to avoid two numbers for one service. The alternative `5173:80` was rejected.

## ADR-016 — Mandatory compose env vars for backend (fail-fast, no hardcoded secrets)

- `Jwt__Key=${JWT_KEY:?...}`, `ADMIN_EMAIL=${ADMIN_EMAIL:?...}`, `ADMIN_PASSWORD=${ADMIN_PASSWORD:?...}` — dev defaults for secrets are rejected (they would be committed); `docker compose up` aborts with a clear message if the `.env` is missing. `AUTH_RATE_LIMIT_PER_MINUTE` keeps a dev default (`:-10`). `appsettings.json` no longer contains the literal `${JWT_KEY}` placeholder; `Jwt:Key` defaults to `""` and `Program.cs` fails explicitly when no key is configured.

## ADR-017 — VITE_API_BASE_URL as Docker build arg

The SPA bundle bakes the API base URL at build time (`import.meta.env.VITE_API_BASE_URL`). The frontend Dockerfile exposes `ARG VITE_API_BASE_URL=http://localhost:5000` (ENV before `npm run build`) and compose passes it explicitly via `build.args`; the default in code stays as the local dev fallback.

## Future improvement (not in US-007): bind mount for SQLite

Swapping the named volume `database_data` for a bind mount (`./workflow/database:/app/database`) would let host-side MCP servers read the same SQLite file as the compose backend, and unify the filename (`BibliotecaVirtual.db`). Deliberately excluded from US-007 because it changes the data contract and risks data loss; to be evaluated in a future story.

## MCP Activation Rule

MCP servers must remain disabled until the corresponding User Story is Implemented and Validated:
- biblioteca-mcp → enabled when US-Biblioteca-MCP is Validated
- security-audit-mcp → enabled when US-Security-Audit is Validated
- open-library → enabled when US-External-MCP is Validated

## ADR-018 — BookRequest entity and request status

Registers the design debt left from US-009 (book request workflow) that was never captured in this file: a `BookRequest` entity tracks a request to add copies of a book not present in the database, with a `BookRequestStatus` lifecycle (Pending / Approved / Rejected). Administrators manage these requests from "Gestión de Libro" to bring requested books into the catalog, widening availability with external sources. Recorded in the US-010 documentation round.

## ADR-019 — Idempotent demo catalog seed

The demo catalog is seeded from a single manifest JSON, `workflow/backend/data/seed-books.json`, which is the single source of truth consumed by both the C# seeder (`CatalogSeeder`) and the Python verification script. Seeding runs at startup after `EnsureCreated`, role seed, and admin seed, and only inserts when the `Books` table is empty (same guard pattern as `SeedRolesAsync`), so re-runs never duplicate. Invalid entries are skipped with a warning instead of aborting startup. Behavior is controlled by `CatalogSeed:Enabled` and `CatalogSeed:FilePath`. No schema migration is required (`EnsureCreated` regenerates schema + seed when the `.db` is deleted).

## ADR-020 — Open Library verification as dev-time batch via MCP

Verification that seed books exist in Open Library is a development/QA batch task, not a runtime feature. It is executed by the script `workflow/mcp/open-library-mcp/verify_seed_open_library.py`, which invokes the custom open-library MCP tool `ol_verify_by_isbn` over stdio (reusing the chatbot's `McpStdioClient`, consistent with ADR-006/007 and the data-flow frontier defined in US-010). The backend never adds an HTTP client to Open Library. Semantics of "available in Open Library": the work exists in OL and the returned title matches the seeded one (normalized, case- and accent-insensitive comparison); it does NOT imply rental availability, and no invented key is ever seeded.

## ADR-021 — Frontend-only library visual identity

The SPA adopts a warm, aged "Sala de lectura" (traditional library) identity as a presentation-only change, redefining the shadcn/ui tokens in `src/index.css` (light `:root` + `.dark`) with a palette of parchment/paper backgrounds, espresso/wine/wood warm browns, and brass/olive/ochre accents. Serif typography uses Fraunces Variable (display) and Lora Variable (body). Book covers are derived client-side from ISBN/OLID via `covers.openlibrary.org` with an ornamental fallback on error. No routes, permission guards, business logic, or API contracts change.

## ADR-022 — Feedback write via Biblioteca-MCP (scoped write)

User feedback on recommendations (`registrar_feedback`) is the ONLY write operation allowed on Biblioteca-MCP. ADR-011 forbids the chatbot from touching the database directly and routes all data access through MCP, so the feedback is persisted via `registrar_feedback` (Biblioteca-MCP gains write capability exclusively for this tool; `common/sqlite.py::execute` already existed). The backend remains the schema owner (`Feedback`/`UserPreference` entities + `DbSet`s created by `EnsureCreated`). The frontend never calls MCP directly (ADR-007): the recommendation cards' «Me gustó»/«No me gustó» buttons send a follow-up message to the chatbot, which persists it via `registrar_feedback`. Table name follows EF Core pluralization convention (`Feedbacks`, not `Feedback`) — a QA-caught bug fixed in US-012.

## ADR-023 — External LLM as a graph node with fallback and PII masking

The final recommendation wording can be generated by an external LLM (LangChain, OpenAI-compatible chat model) via a dedicated graph node `llm_response` placed after availability. Rules: the API key is read from `LLM_API_KEY` (never hardcoded, ADR-016); `LLM_MODEL` selects the model (default `gpt-4o-mini`); PII masking (`app/utils/pii_masker.py`) is mandatory before sending context to the external provider (chatbot-rules); the prompt (`app/prompts/recommendation_prompt.txt`) forbids inventing titles/authors/availability and personal data. If the provider is unavailable (no key, missing package, network error, 20s timeout) the node returns None and the graph falls back to the heuristic `response_node` — the chatbot never collapses.

## ADR-024 — BackgroundService for due-date notifications (US-013)

A .NET `BackgroundService` (`RentalDueNotificationService` in `Infrastructure/Services`) periodically detects Active rentals whose `DueDate` falls inside the window `0 < DueDate - Now <= 2 days` and persists one row per rental in a new `Notifications` table. Design decisions: (1) the hosted service holds no business logic — each cycle creates a scope via `IServiceScopeFactory` and dispatches `GenerateDueDateNotificationsCommand` through the in-house `IDispatcher` (ADR-009); (2) idempotency is guaranteed by a unique index on `Notifications.RentalId` plus a pre-insert guard in the handler, so repeated cycles never duplicate; (3) the interval is configurable via `Notifications:CheckIntervalSeconds` (default 3600s, min 30s), overridable through `NOTIFICATIONS_CHECK_INTERVAL_SECONDS` (ADR-016); (4) the notification is a DB row only — real delivery (email/websocket/push) and the frontend bell/panel UI are explicitly out of scope; (5) read/mark endpoints (`GET /api/notifications`, `PATCH /api/notifications/{id}/read`) are protected by the seeded `notifications.read` permission (Admin/Bibliotecario/Usuario) and enforce ownership by `UserId` (marking another user's notification returns 404). The chatbot's `due_reminder`/`overdue` nodes are untouched.

## ADR-025 — Fail-fast configuration via environment variables everywhere (US-014)

All runtime configuration across every module is read from environment variables with **no hardcoded defaults** — not in code, not in Dockerfiles, not in Docker Compose. Missing required variables cause a clear fail-fast startup error naming the missing variable. Scope: backend reads connection string (`SQLITE_DATA_SOURCE`), JWT issuer/audience (`JWT_ISSUER`/`JWT_AUDIENCE`), CORS origin (`CORS_ORIGINS`) and rate limit (`AUTH_RATE_LIMIT_PER_MINUTE`) via required configuration helpers (`GetRequiredString`/`GetRequiredInt`); the dev-only JWT key in `appsettings.Development.json` was removed; frontend requires `VITE_API_BASE_URL`/`VITE_CHATBOT_API_BASE_URL` at build time (no `??` fallbacks in `src/config/env.ts`); the chatbot requires `BIBLIOTECA_MCP_COMMAND`/`OPEN_LIBRARY_MCP_COMMAND`/`SECURITY_AUDIT_MCP_COMMAND` and `LLM_MODEL` whenever `LLM_API_KEY` is set (ADR-023 fallback behaviour is kept — the LLM remains optional); MCP servers require `DATABASE_PATH` and `AUDIT_DATABASE_PATH`; Docker Compose uses `:?` (mandatory) substitutions only. `LLM_API_KEY`/`LLM_MODEL` pass through compose as optional (empty when unset) because the external LLM is an opt-in capability, not a default value.

## ADR-026 — Documentation lives in each module; root README is an index (US-014)

The root `README.md` is a high-level index (overview, architecture, AI Engineering pipeline, stack, quick start) that links to per-module READMEs; the deep technical detail (env vars, endpoints, seed, services, themes) lives in `workflow/backend/README.md`, `workflow/frontend/README.md`, `workflow/chatbot/README.md` and the new `workflow/mcp/README.md`. This fulfils the promise made in the root README (module READMEs) and avoids the monolith.

## ADR-027 — Admin role no longer rents; authoritative role-claim seed (US-014)

The `Admin` role no longer includes `rentals.create` nor `rentals.view_own`: an administrator cannot rent books nor access "Mis alquileres" (backend policies and frontend permission-guards already enforce this, so removing the claims is sufficient). `SeedRolesAsync` is now **authoritative**: on each startup it adds missing `permission` claims from each role's manifest and **removes** stale `permission` claims no longer present, so existing databases lose revoked permissions without manual cleanup. The `Usuario` role keeps `rentals.create`/`rentals.view_own`, and `CatalogPage` shows the «Alquilar» action only for available books and users holding `rentals.create`.

## ADR-028 — CI coverage of the whole stack with fail-fast config (US-015)

The GitHub Actions pipeline (`.github/workflows/ci.yml`) validates all applications, not just backend/frontend. It defines three jobs: `backend` (`dotnet restore` + `dotnet build --no-restore --configuration Release`; the previous `dotnet test --no-build ... || true` was removed because no test projects exist and it was a silent false-green), `frontend` (`npm ci` + `npm run build`), and `python` (installs the requirements of the chatbot and the three MCP servers and runs `pytest` over the chatbot, Biblioteca-MCP and Open Library MCP suites — 65 tests, self-contained, no network nor API keys). The `frontend` job injects the build-time variables required by the fail-fast config of ADR-025 (`VITE_API_BASE_URL=http://localhost:5000`, `VITE_CHATBOT_API_BASE_URL=http://localhost:8000`) as workflow `env` values — these are CI build environment values, not hardcoded code defaults, so ADR-025 (no defaults in code) still holds. `python` tests run from each module directory (`working-directory`) because the chatbot conftest resolves its `app` package relative to the module root. No secrets are used anywhere in the workflow.