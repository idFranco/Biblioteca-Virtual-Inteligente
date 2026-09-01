# Iteration Log — bugfix/US-023-docker-startup-healthcheck

## 2026-09-01 — qa-check US-023 → PASS

- **Story:** US-023 — Validar al arrancar bajo docker compose que el modelo local Ollama esté activo, que exista conexión a GROQ y exponerlo en healthcheck.
- **Rama:** `feature/US-023-startup-healthcheck`.
- **Veredicto global:** PASS — los 5 escenarios de criterios de aceptación pasan.

### Criterios de aceptación
- **AC#1 Stack sano — arranca y el chatbot queda healthy** — ✅ PASS
  - Gate arranque sano (fakes Ollama+GROQ en `host.docker.internal` vía `--add-host`): `[startup-checks] OK: modelo local Ollama activo y conexión a GROQ verificada.` → **exit 0**.
  - Runtime uvicorn: `GET /health` → **HTTP 200** `{"status":"healthy","ollama":"ok","groq":"ok"}`; `python -m app.healthcheck` → **exit 0**.
- **AC#2 Modelo local inactivo al arrancar → falla con diagnóstico claro** — ✅ PASS
  - Gate fail-fast Ollama (Ollama apagado en host): `python -m app.startup_checks` → **exit 1** con log `[startup-checks] ERROR: El modelo local Ollama no está activo: no se pudo consultar 'http://host.docker.internal:11434/v1/models' (ConnectError: All connection attempts failed).`
  - Caso "modelo no cargado" cubierto por unit test (`test_ollama_model_unloaded_raises`).
- **AC#3 GROQ sin conexión o clave inválida al arrancar → falla con diagnóstico claro** — ✅ PASS
  - Gate fail-fast GROQ (fake Ollama para avanzar el check + `API_KEY_GROQ` real del `.env`): pasa Ollama y falla en GROQ → **exit 1** con log `[startup-checks] ERROR: No hay conexión a GROQ: la clave 'API_KEY_GROQ' es inválida o no autorizada (HTTP 401).`
  - Fallo de red cubierto por unit test (`test_groq_network_error_raises`).
- **AC#4 Dependencia cae en runtime → /health degradado y contenedor unhealthy** — ✅ PASS
  - Con el stack arriba y el fake GROQ detenido (tras TTL 30 s): `GET /health` → **HTTP 503** `{"status":"degraded","ollama":"ok","groq":"down"}`; `python -m app.healthcheck` → **exit 1** (`unhealthy` en `docker compose ps`); `POST /chat` sigue respondiendo **HTTP 200** con fallback heurístico (no cae).
- **AC#5 Regresión — tests del chatbot siguen verdes** — ✅ PASS
  - `python3 -m pytest tests -q` en `workflow/chatbot` → **150 passed in 1.86s, 0 failed**.

### Evidencia clave / gates
| Gate | Comando | Resultado |
|---|---|---|
| Tests chatbot | `cd workflow/chatbot && python3 -m pytest tests -q` | 150 passed |
| Tests biblioteca-mcp | `cd workflow/mcp/biblioteca-mcp && python3 -m pytest tests -q` | 15 passed |
| Tests open-library-mcp | `cd workflow/mcp/open-library-mcp && python3 -m pytest tests -q` | 18 passed |
| Tests security-audit-mcp | `cd workflow/mcp/security-audit-mcp && python3 -m pytest tests -q` | 26 passed |
| Gate fail-fast Ollama | `docker build ... && docker run ... -m app.startup_checks --env-file .env` | exit 1, log claro |
| Coherencia README↔comportamiento | Lectura sección "Validación de arranque (US-023)" + contrato `/health` | coherente |

### Documentation Gate
Cumplido — `## QA Result` documentado en `US-023.md` (reemplazado el `Pending`); README `workflow/chatbot` actualizado con la sección de validación/healthcheck. Estado en `project_state.json` y frontmatter coinciden (`Implemented`).

### Observaciones no bloqueantes
- **Redacción README:** la frase "Sin API key configurada, GROQ se marca como `down` (degraded), no bloquea el arranque" describe `probe_health()` (runtime), no `check_groq()` (que sí hace fail-fast si falta la clave). No es defecto: bajo compose la variable es obligatoria (`API_KEY_GROQ:?`). Sugerencia menor de redacción.
- **`API_KEY_GROQ` del `.env` es inválida (401):** detectada correctamente por el fail-fast; no se modifica por seguridad. Para arranque sano real: clave válida + Ollama activo.
- Sin PR aún; la creación vía GitHub MCP es el siguiente paso previo a `Validated`.

### Siguiente paso
PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.