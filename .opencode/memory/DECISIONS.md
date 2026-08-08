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

The backend follows Clean Architecture with four projects: Domain (innermost, no dependencies), Application (CQRS Commands/Queries/Handlers + FluentValidation), Infrastructure (EF Core, Identity, JWT), and WebAPI (ASP.NET host + Controllers). Commands and Queries are routed via a custom in-house `Dispatcher` class; MediatR is forbidden.

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

The frontend container runs a custom `nginx.conf` (`listen 5173`) so compose mapping, `EXPOSE`, and the CORS origin stay aligned on one port. `try_files $uri $uri/ /index.html` avoids 404s when refreshing React Router routes. The `5173:80` mapping alternative was rejected to keep a single port for the service.

## ADR-016 — Mandatory compose env vars (fail-fast, no hardcoded secrets)

Backend secrets are injected exclusively at runtime: compose `Jwt__Key=${JWT_KEY:?...}`, `ADMIN_EMAIL=${ADMIN_EMAIL:?...}`, `ADMIN_PASSWORD=${ADMIN_PASSWORD:?...}` abort with a clear message if `.env` is missing (dev defaults are rejected as they would be committed). `appsettings.json` no longer carries the literal `${JWT_KEY}` placeholder; `Program.cs` fails fast when the key is empty.

## ADR-017 — VITE_API_BASE_URL as Docker build arg

The SPA API base URL is baked at image build time. The frontend Dockerfile exposes `ARG VITE_API_BASE_URL=http://localhost:5000` and compose passes it via `build.args`; source default (`http://localhost:5002`) remains only as local dev fallback.

## MCP Activation Rule

MCP servers must remain disabled until the corresponding User Story is Implemented and Validated:
- biblioteca-mcp → enabled when US-Biblioteca-MCP is Validated
- security-audit-mcp → enabled when US-Security-Audit is Validated
- open-library → enabled when US-External-MCP is Validated
