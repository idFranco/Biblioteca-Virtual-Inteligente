# AI Engineering Log — feature-US-017-ollama-host-port-conflict

**Story:** US-017 — Resolver conflicto de puerto 11434 usando Ollama nativo del host

**Branch:** `feature/US-017-ollama-host-port-conflict`

**Fecha:** 2026-08-21

## Roles ejecutados

| Role | Contribution |
|---|---|
| Functional Analyst | Alcance deployment-only; 3 escenarios Gherkin (arranque sin conflicto, recomendación vía Ollama nativo, fallback preservado) |
| Architect | Topología host: eliminar servicio `ollama` del compose; chatbot → host vía `host-gateway`; requisito systemd condicional; ADR-032 |
| Technical Lead | Plan consolidado en 5 frentes (compose, `.env`, `.env.example`, sistema, docs); sin discrepancias entre roles |
| Backend Developer | No impactado |
| Frontend Developer | No impactado |
| AI Engineer | Cambios compose/`.env`/`.env.example`; verificación de `client.py` intacto y suite pytest verde |
| QA | Plan de validación de 7 pasos (drill de fallback pendiente en qa-check) |
| Technical Writer | README chatbot, `.env.example`, DECISIONS.md (ADR-032 + nota de deprecación en ADR-029), bitácora |

## Contexto

`docker compose up --build` fallaba con `bind: address already in use` al publicar el puerto `11434`: el equipo de desarrollo tiene un **Ollama nativo** como servicio systemd (`ollama.service`, bind por defecto `127.0.0.1`, con `llama3.2` ya descargado). Se elimina la topología "Ollama en contenedor" (US-016) y se adopta la alternativa que la propia US-016 dejó documentada: consumir el Ollama nativo desde los contenedores vía `host.docker.internal:host-gateway`.

## Cambios por área

### Infraestructura
- `docker-compose.yml`: eliminado el servicio `ollama` (imagen, `ports: "11434:11434"`, volumen, entrypoint de pull, env), el volumen `ollama_data` y `- ollama` de `depends_on` del chatbot. Ejemplo del fail-fast de `OLLAMA_BASE_URL` actualizado a la URL host. Añadido al chatbot:
  ```yaml
      extra_hosts:
        - "host.docker.internal:host-gateway"
  ```

### Configuración
- `.env` (no versionado): `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`.
- `.env.example`: default y comentarios actualizados a la topología host con matices Docker Desktop/Engine y nota de precedencia shell→compose.

### Sistema host (fuera del repo)
- **Docker Desktop (entorno real del desarrollador, 4.85.0 `desktop-linux`):** NO se requiere ningún cambio en systemd — su proxy resuelve `host.docker.internal` hacia el loopback del host. Verificado con inferencia real de `llama3.2`.
- **Docker Engine nativo (otros hosts):** drop-in `/etc/systemd/system/ollama.service.d/override.conf` → `Environment="OLLAMA_HOST=0.0.0.0"` + `sudo systemctl daemon-reload && sudo systemctl restart ollama`. Documentado como prerequisito condicional.
- Nota operativa: compose da prioridad a variables exportadas del shell sobre `.env`; si existe `DATABASE_PATH=./workflow/database/...` exportada para dev en host, recrear con `DATABASE_PATH=/app/database/BibliotecaVirtual.db AUDIT_DATABASE_PATH=/app/database/audit.db docker compose up -d --force-recreate chatbot`.

### Documentación
- `workflow/chatbot/README.md`: sección "LLM local Ollama (recomendaciones)" reescrita (URL base host, matices Docker Desktop/Engine, eliminación del servicio compose).
- `.opencode/memory/DECISIONS.md`: **ADR-032** nuevo; ADR-029 anotado con topología deprecada. Mirror en `codebase-memory_manage_adr`.
- README raíz: sin cambios requeridos.

### Sin cambios
- Código Python/C#/TypeScript, tests, Dockerfiles, CI. `app/llm/client.py` intacto: la selección de proveedor sigue siendo 100% env-driven.

## Decisiones (ADRs)

- **ADR-032 (nuevo):** Ollama nativo del host reemplaza al servicio `ollama` del compose; `extra_hosts: host-gateway`; prerequisito systemd solo para Docker Engine nativo; beneficios (sin re-descarga de ~2 GB, sin doble RAM/GPU) y trade-off aceptado en Engine (exposición LAN tras NAT).
- **ADR-029 (anotado):** topología contenedor marcada como deprecada por US-017.

## Iteraciones

| # | Fase (fecha) | Roles | Resultado |
|---|---|---|---|
| 1 | Planificación (2026-08-21) | Functional Analyst, Architect, Technical Lead, AI Engineer, QA, Technical Writer | Plan consolidado en 5 frentes sin discrepancias; historia avanzada a `Planned` y aprobada por el usuario |
| 2 | Implementación (2026-08-21) | AI Engineer, Technical Lead | 5 frentes aplicados; hallazgos de entorno integrados a docs (Docker Desktop sin systemd; precedencia shell→compose para `DATABASE_PATH`); validación de despliegue PASS (detalle abajo) |

## Registro de riesgos

| Nivel | Módulo | Riesgo | Mitigación / Estado |
|---|---|---|---|
| Media→N/A en Docker Desktop | Host | Exposición LAN al bindear Ollama en `0.0.0.0` | Solo aplica a Docker Engine nativo; documentado con opción ufw. En Docker Desktop no se requiere el cambio systemd |
| Baja | Chatbot | `host.docker.internal` no resuelve sin `extra_hosts` | `extra_hosts: host-gateway` en compose; conectividad verificada (200 + inferencia real). Cerrado |
| Baja | Docker | Contenedor `ollama-1` residual en estado `Created` | `docker compose up --remove-orphans` ejecutado limpio; `docker ps` sin ollama. Cerrado |
| Baja | Host | Firewall bloquea tráfico hacia 11434 | En Docker Desktop el proxy alcanza el loopback del host; verificado empíricamente. En Engine nativo queda como paso de diagnóstico |
| Baja | Chatbot | Precedencia shell→compose filtra `DATABASE_PATH` relativa al contenedor | Recreación con rutas in-image explícitas; documentado en `.env.example`/ADR-032. Cerrado |
| Baja | Chatbot | Regresión en recomendaciones/fallback | Suite pytest 61 passed; E2E `/chat` OK; drill de fallback pendiente en `qa-check`. Abierto para QA |

## Validación (ejecutada en implementación)

1. **Estático:** `docker compose config` OK — solo `backend`, `chatbot`, `frontend`; sin publicación `11434`; `OLLAMA_BASE_URL` interpolada a `http://host.docker.internal:11434/v1`; `extra_hosts: host.docker.internal=host-gateway` presente. PASS
2. **Regresión:** `pytest -q` en `workflow/chatbot` → **61 passed** (con `.venv` de la raíz). PASS
3. **Despliegue:** `docker compose up --build --remove-orphans -d` → backend/frontend/chatbot **Up**; sin contenedor ollama; `/health` de backend y chatbot OK. PASS
4. **Conectividad:** desde el chatbot, GET `host.docker.internal:11434/api/tags` → 200 con `llama3.2:latest` listado; inferencia real vía `POST /api/generate` → respuesta generada. PASS
5. **Funcional E2E:** `POST /chat` (`X-Correlation-ID: us017-smoke-1`) → respuesta en lenguaje natural del nodo `llm_response`. PASS
6. **Auditoría:** MCP `Security-Audit-MCP` inició por stdio in-image tras corregir `DATABASE_PATH`; consulta de vencimientos respondió saneada (`[REDACTED]`, comportamiento preexistente US-012). PASS
7. **Fallback drill:** pendiente de `qa-check` (requiere parar el servicio nativo).

### Incidencia resuelta durante la validación

Los MCP internos crasheaban al arranque: el shell del host tenía exportada `DATABASE_PATH=./workflow/database/BibliotecaVirtual.db` (válida solo para dev fuera de Docker) y **compose prioriza el entorno del shell sobre `.env`**, así que el contenedor recibía la ruta relativa en lugar de `/app/database/...` (ADR-030). Resuelto recreando el chatbot con las dos rutas in-image explícitas (comando documentado arriba y en ADR-032). No requiere cambios de código.

## Notas de entrega

- **Docker Desktop:** el cambio de systemd NO es necesario en este entorno (proxy nativo hacia loopback del host); queda documentado como requisito solo para Docker Engine nativo.
- **Precedencia shell→compose:** documentada en `.env.example`, ADR-032 y esta bitácora; comando de recreación con rutas in-image explícitas.
- El pipeline de auditoría puede responder `[REDACTED]` en consultas con datos personales (p. ej. vencimientos): comportamiento preexistente de US-012, sin relación con esta historia.
