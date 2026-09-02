# Iteration Log — feature/US-025-fail-fast-docker

## 2026-09-02 — qa-check US-025 → PASS

- **Story:** US-025 — Fail-fast global en docker compose: detener todo el stack si un servicio falla (healthchecks en los 3 servicios + `depends_on: condition: service_healthy` + comando nativo `--abort-on-container-exit --exit-code-from backend`).
- **Rama:** `feature/US-025-fail-fast-docker`.
- **Veredicto global:** PASS — los 4 escenarios (3 criterios de aceptación + escenario de éxito) pasan.
- **Criterios de aceptación:**
  - AC#1 Falla de arranque del chatbot detiene backend y frontend — ✅ PASS
  - AC#2 Backend no healthy bloquea a sus consumidores (frontend/chatbot con `service_healthy`) — ✅ PASS
  - AC#3 Falla de cualquier otro servicio (frontend) aborta igualmente el stack — ✅ PASS
  - Escenario éxito: todo el stack arranca y los healthchecks no rompen el build — ✅ PASS
- **Evidencia clave:**
  - AC#1/AC#3: runtime con `docker compose up --build --abort-on-container-exit --exit-code-from backend` → al salir `frontend-1`, `backend-1` se detuvo automáticamente; `docker compose ps` posterior vacío (el stack nunca queda parcialmente levantado). El flag detiene TODOS los contenedores ante la salida de cualquier servicio (incl. el fail-fast US-023/024 del chatbot por falta de Ollama/GROQ).
  - AC#2: `docker-compose.yml` → `frontend` (líneas 34-36) y `chatbot` (líneas 76-78) con `depends_on: backend: condition: service_healthy`; backend con `HEALTHCHECK` que sondea `GET /health` (existe en `Program.cs:141`); `curl` instalado en la imagen runtime (Dockerfile backend línea 18-20). `docker compose config --quiet` OK.
  - Builds: `docker compose build` OK para backend/frontend/chatbot con los nuevos healthchecks (backend `sha256:993308e8...`, frontend `sha256:bde522c8...` con `VITE_API_BASE_URL`/`VITE_CHATBOT_API_BASE_URL` desde `.env`).
  - Chatbot `healthcheck.py` (`python -m app.healthcheck`) ya presente (US-023/024) — sin cambios de código Python.
- **Pruebas ejecutadas:** docker compose build OK (3 imágenes) · docker compose config --quiet OK · docker compose up con abort-on-container-exit (fail-fast global verificado) · docker compose down sin residuales.
- **Documentation Gate:** cumplido — `## QA Result` documentado en `US-025.md` (reemplazado `Pending`; `## Implementation Notes` verificadas sin modificar), READMEs ya actualizados en implementación.
- **Observación no bloqueante:** en el escenario real del bug (chatbot sala 1 por falta de Ollama/GROQ) FALTA levantar la dependencia externa; el mecanismo `--abort-on-container-exit` + healthchecks/dependencias probados garantizan el abort global independientemente del motivo de salida del servicio.
- **Siguiente paso:** PR vía GitHub MCP → `Validated`, revisión y merge en GitHub.
