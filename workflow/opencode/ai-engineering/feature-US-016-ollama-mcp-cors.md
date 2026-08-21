# AI Engineering Log — feature-US-016-ollama-mcp-cors

**Story:** US-016 — Configurar LLM local Ollama en el chatbot, empaquetar los 3 MCP en la imagen del chatbot y corregir CORS

**Branch:** `feature/US-016-ollama-mcp-cors`

**Date:** 2026-08-20

## Roles participantes

| Role | Participación |
|---|---|
| Functional Analyst | Alcance funcional y 10 escenarios Gherkin (Ollama, GROQ auditor, MCP in-image, CORS, fallback) |
| Architect | Cliente LLM a Ollama vía `ChatOpenAI` + `base_url`; empaquetado de los 3 MCP en la imagen del chatbot (contexto de build raíz); volumen `database_data` compartido; servicio `ollama`; CORS con `CORSMiddleware`; ADR-029/030/031 + actualización ADR-023/025 |
| Technical Lead | Plan consolidado (5 frentes); resolución de discrepancias de naming (`OLLAMA_BASE_URL`/`OLLAMA_MODEL`), topología de Ollama, `CORS_ORIGINS` compartida, volumen único, `allow_credentials=False` |
| Backend Developer | Ningún cambio de código; solo se comparte el volumen `database_data` con el chatbot |
| Frontend Developer | Ningún cambio de código; la SPA ya envía `Content-Type` + `X-Correlation-ID` |
| AI Engineer | `client.py` (prioridad Ollama → cloud → heurístico), `main.py` (`_cors_origins` + `CORSMiddleware`), `Dockerfile` (contexto raíz + `COPY workflow/mcp`), `requirements.txt` (`fastmcp`), tests nuevos |
| QA | Plan de validación funcional F1-F20, tests automatizados sin red/claves, integración `docker compose up --build`, seguridad/permisos |
| Technical Writer | README chatbot (Ollama, Clientes MCP in-image, CORS), README MCP (despliegue en imagen + fix `GROQ_API_KEY`→`API_KEY_GROQ`), `.env.example`, DECISIONS.md (ADR-023/025 actualizados + ADR-029/030/031), bitácora |

## Contexto

El chatbot FastAPI (LangGraph, US-012) generaba sus recomendaciones con un LLM cloud de OpenAI (`LLM_API_KEY`/`LLM_MODEL`) o, en su defecto, con la heurística de `response`. Tres problemas impedían un despliegue robusto bajo docker compose:

1. **LLM cloud como única vía:** dependencia de una clave cloud para la redacción de recomendaciones; sin ella, solo heurística.
2. **MCPs fuera de la imagen:** los 3 MCP (biblioteca, security-audit, open-library) se invocaban por comandos que asumían el host (`npx -y mcp-open-library`, rutas de repo) — inválidos dentro del contenedor del chatbot bajo compose.
3. **Sin CORS:** `main.py` no exponía cabeceras CORS, por lo que el navegador (SPA en `:5173`) bloqueaba `POST /chat` hacia `:8000`.

US-016 resuelve los tres con: **Ollama llama3.2 local** como proveedor primario de recomendaciones (GROQ queda exclusivo de Security-Audit-MCP), **empaquetado de los 3 MCP en la imagen del chatbot** con contexto de build en la raíz del repo, y **CORS vía `CORSMiddleware`** leyendo `CORS_ORIGINS` (fail-fast).

## Cambios por área

### Ollama (LLM local para recomendaciones)

- `app/llm/client.py`: `ChatOpenAI` apuntado a `OLLAMA_BASE_URL` (`/v1`, compatible OpenAI); sin dependencia nueva (`langchain-openai` ya presente; no se usa `ChatOllama`).
- **Prioridad de proveedor:** 1) Ollama local (`OLLAMA_BASE_URL` + `OLLAMA_MODEL=llama3.2`, `api_key="ollama"` placeholder no secreto, `temperature=0.4`, `max_tokens=300`, `timeout=_llm_timeout()`); 2) cloud (`LLM_API_KEY`/`LLM_MODEL`, opcional); 3) `None` → fallback heurístico `response` (ADR-023 preservado: el chatbot nunca colapsa).
- **Nuevas variables:** `OLLAMA_BASE_URL` (opcional en código; obligatoria `:?` en compose), `OLLAMA_MODEL` (requerida si `OLLAMA_BASE_URL` está definida; `llama3.2`), `LLM_TIMEOUT_SECONDS` (nueva, requerida cuando el LLM está habilitado; `120` en compose para no matar a llama3.2 en CPU).
- PII masking (`app/utils/pii_masker.py`) sigue siendo obligatorio antes de enviar contexto a cualquier proveedor.
- **GROQ intocable:** `groq_audit.py` conserva `API_KEY_GROQ`, `GROQ_MODEL=llama-3.3-70b-versatile`, `GROQ_API_URL`, `GROQ_TIMEOUT_SECONDS`. Ninguna ruta de recomendación usa GROQ.

### Empaquetado de los 3 MCP en la imagen del chatbot

- `docker-compose.yml`: `chatbot.build.context: .` + `chatbot.build.dockerfile: workflow/chatbot/Dockerfile` (Docker `COPY` no escapa del contexto; los MCP viven en `workflow/mcp/`).
- Nuevo **`.dockerignore` raíz** (ignore-all + whitelist `workflow/chatbot` + `workflow/mcp`): evita enviar `node_modules/`, `.venv/`, `.git`, `*.db`, `.env`, `dist/`, `bin/`, `obj/`, etc.
- `workflow/chatbot/Dockerfile`: `COPY workflow/chatbot` → `/app` y `COPY workflow/mcp` → `/app/workflow/mcp`, preservando el prefijo `workflow/` para que el bootstrap `sys.path` y `parents[3]` de `workflow/mcp/common/settings.py` sigan resolviendo sin cambios de código. `pip install` de los requirements del chatbot + los 3 MCP (`fastmcp>=0.2.0` añadido; `httpx` ya estaba).
- **Comandos MCP in-image:**
  - `BIBLIOTECA_MCP_COMMAND=python /app/workflow/mcp/biblioteca-mcp/server.py`
  - `SECURITY_AUDIT_MCP_COMMAND=python /app/workflow/mcp/security-audit-mcp/server.py`
  - `OPEN_LIBRARY_MCP_COMMAND=python /app/workflow/mcp/open-library-mcp/server.py` (servidor local empaquetado, no `npx -y mcp-open-library`: sin Node en la imagen, versionado en el repo).
- **Rutas de BD en el contenedor:** `DATABASE_PATH=/app/database/BibliotecaVirtual.db`, `AUDIT_DATABASE_PATH=/app/database/audit.db`, ambas sobre el volumen compartido `database_data:/app/database` (mismo SQLite que el backend). `depends_on: backend` para orden de arranque (la BD existe antes de las peticiones MCP).
- **Servicio `ollama`:** imagen `ollama/ollama`, puerto `11434`, volumen `ollama_data:/root/.ollama`, inicialización con `ollama serve` + `ollama pull "$OLLAMA_MODEL"`. El chatbot recibe `OLLAMA_BASE_URL=http://ollama:11434/v1` y `depends_on: ollama`. Alternativa de desarrollo documentada: Ollama en el host + `http://host.docker.internal:11434/v1` con `extra_hosts: ["host.docker.internal:host-gateway"]`.

### CORS

- `workflow/chatbot/main.py`: FastAPI `CORSMiddleware`.
  - `allow_origins = _cors_origins()` parseando `CORS_ORIGINS` (coma-separada), fail-fast `RuntimeError` si falta (ADR-025, sin default).
  - `allow_methods=["POST","GET"]`; `allow_headers=["Content-Type","X-Correlation-ID"]`; `allow_credentials=False` (la SPA no envía cookies/Authorization al chatbot; `userId` viaja en el body).
  - El preflight `OPTIONS` lo maneja el middleware automáticamente.
- **Variable reutilizada:** `CORS_ORIGINS` (ya existía para el backend con `http://localhost:5173`) — una sola fuente de verdad para el origen de la SPA.

### docker-compose

- Servicio `ollama` nuevo.
- Chatbot: `build.context: .`, env `CORS_ORIGINS` (`:?`), `OLLAMA_BASE_URL` (`:?`), `OLLAMA_MODEL` (`:?`), `LLM_TIMEOUT_SECONDS` (`:?`), comandos MCP in-image (`:?`), `DATABASE_PATH`/`AUDIT_DATABASE_PATH` absolutos, volumen `database_data:/app/database`, `depends_on: backend` + `depends_on: ollama`.

### Tests

- `tests/test_llm_client.py` (nuevo): construcción de `ChatOpenAI` con `base_url`/modelo Ollama; `OLLAMA_MODEL` requerido cuando `OLLAMA_BASE_URL` definido; vía cloud sin cambios; sin proveedor → `None`; `ainvoke` lanza → fallback `None`; salida vacía → `None`; PII masked.
- `tests/test_cors.py` (nuevo): parseo de `CORS_ORIGINS`; fail-fast si falta; preflight OPTIONS con TestClient → `Access-Control-Allow-Origin`; POST `/chat` con origen → ACAO; origen no permitido sin ACAO.
- `tests/test_stdio.py` (nuevo): parseo de comando in-image (`python /app/workflow/mcp/...` → `command=python`, `args=[...]`); `require_env` fail-fast; herencia de `DATABASE_PATH`/`AUDIT_DATABASE_PATH` al subproceso.
- Los 40 tests existentes se mantienen verdes (los tests no importan `main`; monkeypatch en la frontera de red, sin Ollama/GROQ/claves).

### Documentación (Technical Writer)

- `workflow/chatbot/README.md`: sección "LLM externo (opcional)" → **"LLM local Ollama (recomendaciones)"** (OLLAMA_BASE_URL, OLLAMA_MODEL=llama3.2, LLM_TIMEOUT_SECONDS, prioridad Ollama → cloud → heurístico, PII masking vigente, GROQ solo auditoría); fila `llm_response` de la tabla de nodos actualizada; "Clientes MCP" con comandos in-image y nota de que la imagen empaqueta los 3 MCP; nueva subsección **CORS**.
- `workflow/mcp/README.md`: nueva sección **"Despliegue en Docker (imagen del chatbot)"** (cómo viajan los 3 MCP, `DATABASE_PATH`/`AUDIT_DATABASE_PATH`/`API_KEY_GROQ` bajo compose, diferencia vs. local standalone); fix `GROQ_API_KEY` → `API_KEY_GROQ` + opcionales `GROQ_API_URL`/`GROQ_MODEL`/`GROQ_TIMEOUT_SECONDS`.
- `.env.example`: grupo chatbot actualizado (Ollama primario, cloud opcional), `CORS_ORIGINS`, rutas in-image de los MCP, rutas absolutas de BD, `API_KEY_GROQ` anotada como solo Security-Audit-MCP.
- `.opencode/memory/DECISIONS.md`: ADR-023 y ADR-025 actualizados; ADR-029/030/031 agregados. Mirror en `codebase-memory_manage_adr` (`mode=update`).

## ADRs

- **ADR-023 (actualizado):** LLM de recomendaciones → proveedor local Ollama `llama3.2` primario con fallback cloud (`LLM_API_KEY`/`LLM_MODEL`) y heurístico; PII masking obligatorio; GROQ reservado a Security-Audit-MCP.
- **ADR-025 (actualizado):** lista nuevas variables requeridas del chatbot: `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `LLM_TIMEOUT_SECONDS`, `CORS_ORIGINS`; `DATABASE_PATH`/`AUDIT_DATABASE_PATH` in-image sobre `database_data`; `LLM_API_KEY`/`LLM_MODEL` solo fallback opcional.
- **ADR-029 (nuevo):** Ollama `llama3.2` como LLM local de recomendaciones (`ChatOpenAI` → `OLLAMA_BASE_URL`); GROQ queda solo para auditoría de Security-Audit-MCP.
- **ADR-030 (nuevo):** los 3 MCP se empaquetan en la imagen del chatbot (`/app/workflow/mcp/<server>/server.py`, invocados con `python`, sin `npx`); build context = raíz del repo con `.dockerignore` raíz; layout preserva `parents[3]`; bases sobre volumen `database_data`.
- **ADR-031 (nuevo):** CORS del chatbot vía `CORSMiddleware` con `CORS_ORIGINS` (fail-fast), `allow_methods=["POST","GET"]`, `allow_headers=["Content-Type","X-Correlation-ID"]`, `allow_credentials=False`.

## Registro de iteraciones

| # | Iteración | Rol(es) | Resultado |
|---|---|---|---|
| 1 | Planificación (2026-08-20) | Functional Analyst, Architect, Technical Lead, AI Engineer, QA, Technical Writer | Plan consolidado; 5 discrepancias resueltas (naming Ollama, topología de Ollama, variable CORS, volumen único, `allow_credentials`); historia avanzada a `Planned` y aprobada |
| 2 | Implementación | AI Engineer, Technical Writer | Código (client.py, main.py, Dockerfile, compose, tests) + documentación (READMEs, .env.example, DECISIONS.md, bitácora) |
| 3 | QA (2026-08-21) | QA | PASS: 86 tests verdes (61 chatbot + 12 biblioteca-mcp + 13 open-library-mcp), 5 criterios de aceptación validados, regresión backend/frontend/compose OK; PR creado vía GitHub MCP e historia avanzada a `Validated` |

## Registro de riesgos

| Severidad | Módulo Afectado | Descripción | Acción de Reparación |
|---|---|---|---|
| Media | Chatbot (Ollama) | Latencia de llama3.2 en CPU supera el timeout → fallback silencioso | `LLM_TIMEOUT_SECONDS=120` (fail-fast cuando el LLM está habilitado); documentar latencia esperada; el fallback garantiza respuesta |
| Media | Chatbot (Ollama) | Modelo llama3.2 no descargado → 404 → fallback | Inicialización del servicio `ollama` con `ollama pull "$OLLAMA_MODEL"`; `depends_on: ollama`; README documenta warm-up |
| Media | Docker (build) | Contexto de build en la raíz envía todo el repo → imagen pesada/lenta | `.dockerignore` raíz (ignore-all + whitelist `workflow/chatbot` + `workflow/mcp`) |
| Media | MCP (bootstrap) | `parents[3]`/`sys.path` se rompe si cambia la profundidad del layout en la imagen | Preservar `/app/workflow/mcp/<server>/server.py`; acoplamiento registrado en ADR-030 |
| Media | Config (.env) | Una `.env` debe servir dos topologías (rutas in-image vs host) | `.env.example` documenta ambas; compose es la topología objetivo; MCPs de opencode.json deshabilitados (ADR-014) |
| Media | Chatbot (CORS) | CORS mal configurado (`127.0.0.1` vs `localhost`) bloquea el despliegue | Orígenes restringidos (nunca `*`); `allow_credentials=False`; escenarios F14-F17 + `test_preflight` |
| Media | Docker (imagen) | Imagen del chatbot crece con los 3 MCP + latencia del primer pull de llama3.2 | Documentar tamaño y comando `ollama pull` en README/compose; modelo local aceptable (ADR-001) |
| Baja | Security-Audit-MCP | GROQ no configurado en runtime rompe la auditoría | Fallback seguro existente (bloquear entrada / sanitizar salida) cuando `API_KEY_GROQ` falta; propagada al subproceso vía `_inherit_environment` |
| Baja | SQLite | Multi-proceso (backend + `registrar_feedback` vía MCP) sobre el mismo archivo | Escritura de baja frecuencia; volumen compartido; aceptable para carga académica |
| Baja | Docker (deps) | Dependencias de los 3 MCP duplicadas en la imagen | `requirements.txt` del chatbot incluye `fastmcp`; `httpx` ya presente; pip install consolidado |

## Resumen de validación

- **Unit tests (CI, sin red/claves):** `test_llm_client.py`, `test_cors.py`, `test_stdio.py` nuevos + 40 existentes verdes.
- **Integración:** `docker compose up --build` (puerta principal); `find /app/workflow/mcp -name "*.py"` → 3 servidores + `common/`; smoke stdio in-container; `GET :8000/health` 200; preflight OPTIONS + POST `/chat` con `Origin: http://localhost:5173`; recomendación real con llama3.2; auditoría persistida en `AUDIT_DATABASE_PATH` con `correlation_id` coincidente; drill de fallback (parar Ollama → heurístico → recuperación); regresión de los 10 casos de uso.
- **Seguridad:** auditoría de entrada/salida obligatoria intacta; GROQ acotado a `groq_audit.py`; sin secretos hardcodeados; PII masking antes del LLM; permisos/roles sin cambios.

## Notas de entrega

- Documentación ejecutada por el Technical Writer en esta iteración: READMEs de chatbot y MCP, `.env.example`, DECISIONS.md (ADR-023/025 + 029/030/031), bitácora de AI Engineering, mirror en `codebase-memory_manage_adr`.
- Pendiente del resto del equipo: push de la rama vía GitHub MCP, avance a `Implemented`, luego `qa-check US-016` (validación completa + PR gate vía `create_pull_request`).
- Al desplegar por primera vez, Ollama descargará `llama3.2` en el primer arranque (warm-up documentado).

## Iteración QA (qa-check US-016)

- **Fecha:** 2026-08-21. **Rol:** QA. **Skill:** testing-qa. **Rama:** `feature/US-016-ollama-mcp-cors`.
- **Tests automatizados:** chatbot 61 passed (21 nuevos: llm_client 10, cors 6, stdio 5), biblioteca-mcp 12 passed, open-library-mcp 13 passed — sin red, sin Ollama/GROQ/claves.
- **Criterios de aceptación:** (a) Ollama llama3.2 con prioridad Ollama→cloud→fallback y PII masking: PASS; (b) GROQ acotado a `groq_audit.py` (`grep -ri "api.groq"` único match): PASS; (c) 3 MCP empaquetados en la imagen (Dockerfile + `.dockerignore` + comandos in-image + volumen compartido): PASS; (d) CORS: preflight OPTIONS 200 con ACAO correcto para origen permitido y sin ACAO para origen no permitido (smoke TestClient): PASS; (e) fallback heurístico cuando Ollama no está disponible: PASS.
- **Regresión:** `dotnet build Release` 0w/0e; `npm run build` OK con env vars de CI; `docker compose config` válido; sin secretos hardcodeados; `.env` gitignored.
- **Resultado:** PASS → historia avanzada a `Validated` tras crear el PR vía GitHub MCP.
