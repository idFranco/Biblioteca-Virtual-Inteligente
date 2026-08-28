# Chatbot — FastAPI + LangChain + LangGraph

Servicio Python independiente en `workflow/chatbot/` que implementa el asistente de la biblioteca como un **grafo de estados dirigido** (LangGraph). Nunca toca la base de datos directamente: todo el acceso a datos va por los MCP servers (ADR-011).

## Flujo del grafo (US-012)

```text
START → reset_turn (limpia transitorios + registra mensaje user)
  → audit_input            (Security-Audit-MCP: auditoría de entrada obligatoria)
      ├─ bloqueada → block_response → audit_output
      └─ segura   → load_user_state → classify_intent (route_by_state)
          ├─ recommendation → preferences → internal_catalog → external_enrichment → availability → response → llm_response → audit_output
          ├─ follow_up     → follow_up → llm_response → audit_output
          ├─ due_reminder   → due_reminder → audit_output
          ├─ overdue        → overdue → audit_output
          ├─ feedback       → feedback → save_feedback → response → llm_response → audit_output
          └─ status_plain/other → response → llm_response → audit_output
  audit_output              (Security-Audit-MCP: auditoría de salida obligatoria)
      ├─ sanitizar → sanitize_response → record_turn → END
      └─ limpio   → record_turn → END
```

### Nodos

| Nodo | Responsabilidad |
|---|---|
| `audit_input` | Audita la entrada del usuario con Security-Audit-MCP (prompt injection, datos sensibles). Si no es segura, el flujo va a `block_response`. |
| `block_response` | Respuesta de bloqueo segura sin procesar el mensaje en el grafo. |
| `load_user_state` | Carga el estado de lectura del usuario (por MCP) con fallback si MCP no está disponible. |
| `classify_intent` | Clasifica la intención (`recommendation`, `follow_up`, `due_reminder`, `overdue`, `feedback`, `book_query`, `status_plain`, `other`) y enruta por `route_by_state`. |
| `preferences` | Carga preferencias de género y perfil de historial vía Biblioteca-MCP (`obtener_preferencias`, `consultar_alquileres_usuario`). |
| `internal_catalog` | Recomienda por historial/preferencias o consulta el catálogo interno por género (`listar_recomendaciones_por_genero`, `buscar_libros`). |
| `external_enrichment` | Enriquece/verifica contra Open Library MCP. |
| `availability` | Filtra las recomendaciones a solo libros disponibles (`verificar_disponibilidad`). |
| `due_reminder` / `overdue` | Informan de alquileres por vencer / vencidos según el estado de lectura. |
| `feedback` / `save_feedback` | Detectan el feedback del usuario y lo persisten vía `registrar_feedback` (Biblioteca-MCP, escritura acotada). |
| `follow_up` | Resuelve preguntas sobre una recomendación previa («cuéntame más sobre la primera»): busca el selector en el historial, compone la respuesta con los detalles del libro elegido y enriquece con Open Library si hay OLID. |
| `response` | Respuesta heurística (fallback y base). |
| `llm_response` | Redacta la recomendación con el LLM local Ollama `llama3.2` (LangChain `ChatOpenAI` → `OLLAMA_BASE_URL`) **con PII masking**; prioridad Ollama → nube (`LLM_API_KEY`/`LLM_MODEL`) → heurística de `response` (ADR-023/029). Actúa también en `follow_up` y smalltalk. |
| `audit_output` | Audita la respuesta con Security-Audit-MCP antes de enviarla al frontend. |
| `sanitize_response` | Sanitiza la salida si la auditoría lo requiere. |
| `reset_turn` / `record_turn` | Abren/cierran el par user/assistant del turno en la ventana de historial (poda a 12 entradas); `record_turn` incrusta las recomendaciones compactas del turno para resolver seguimientos. |

## Memoria conversacional

- **Checkpointer:** LangGraph compilado con `InMemorySaver` cuando `CHAT_MEMORY_DB_PATH` está definida (en Docker `/app/database/chat_memory.db` del volumen `database_data`; standalone en `.env`); `thread_id = conversationId`. Sin la variable, se compila sin checkpointer (dev/tests). **Limitación registrada (ADR-035):** la memoria por sesión se conserva durante la vida del proceso; la persistencia entre reinicios queda como mejora (`AsyncSqliteSaver`).
- **Sesión:** `POST /chat` recibe y reutiliza `conversationId` (generado por el frontend y persistido en `sessionStorage`); dos conversaciones con ids distintos no comparten contexto.
- **Seguimientos referenciales (AC#4):** tras recibir una recomendación, mensajes como «cuéntame más sobre la primera», «la segunda» o «háblame de tu recomendación» se clasifican `follow_up` y responden con los detalles del libro ya recomendado (orden del selector o título citado). Si no hay recomendación previa, el chatbot orienta a pedir una sin colapsar.

## LLM local Ollama (recomendaciones)

- Cliente: `app/llm/client.py` (LangChain `ChatOpenAI` compatible OpenAI apuntando a `OLLAMA_BASE_URL`).
- Config: `OLLAMA_BASE_URL` (obligatoria, fail-fast si falta; en Docker `http://host.docker.internal:11434/v1`, US-017), `OLLAMA_MODEL` (obligatoria; `llama3.2`) y `LLM_TIMEOUT_SECONDS` (obligatoria; timeout de la llamada al proveedor, p. ej. `120`).
- **Topología host (US-017/ADR-032):** el compose **ya no incluye un servicio `ollama`**; el chatbot consume el Ollama nativo del host vía `extra_hosts: ["host.docker.internal:host-gateway"]` y `OLLAMA_BASE_URL=http://host.docker.internal:11434/v1`.
  - **Docker Desktop:** resuelve `host.docker.internal` hacia el loopback del host con su propia capa de proxy → **no requiere ningún cambio en el servicio nativo**.
  - **Docker Engine nativo:** los contenedores no alcanzan el loopback; expón el servicio systemd en todas las interfaces añadiendo al drop-in `/etc/systemd/system/ollama.service.d/override.conf` la línea `Environment="OLLAMA_HOST=0.0.0.0"` y reiniciando (`sudo systemctl daemon-reload && sudo systemctl restart ollama`). Verificación: `ss -ltnp | grep 11434` → `0.0.0.0:11434`.
- **Prioridad de proveedor (ADR-023/029):** 1) Ollama local (`OLLAMA_BASE_URL` + `OLLAMA_MODEL=llama3.2`); 2) LLM en la nube (`LLM_API_KEY`/`LLM_MODEL`, fallback cloud); 3) heurística de `response`.
- `LLM_API_KEY`/`LLM_MODEL` pasan a ser **opcionales** (fallback cloud): solo se usan si Ollama no está disponible o no responde.
- El contexto enviado al proveedor pasa por `app/utils/pii_masker.py` (PII masking obligatorio) tanto hacia Ollama como hacia la nube.
- GROQ (`API_KEY_GROQ`) se usa **exclusivamente** en Security-Audit-MCP para auditar entrada/salida; nunca redacta recomendaciones (ADR-029).
- Si ningún proveedor responde (timeout `LLM_TIMEOUT_SECONDS`, Ollama caído, error de red o sin clave), el nodo devuelve `None` y el grafo usa el fallback heurístico; el chatbot nunca colapsa.

## CORS

El chatbot habilita CORS con el `CORSMiddleware` de FastAPI leyendo `CORS_ORIGINS` (lista de orígenes separados por coma, **fail-fast**: si falta la variable, no arranca). Configuración: `allow_methods=["POST","GET"]`, `allow_headers=["Content-Type","X-Correlation-ID"]` y `allow_credentials=False`.

Motivo: la SPA de React se sirve en `:5173` y el chatbot responde en `:8000`; sin esta configuración el navegador bloquea `POST /chat` y su preflight `OPTIONS` por same-origin policy. `X-Correlation-ID` se permite explícitamente para preservar la trazabilidad extremo a extremo (US-009/012). `allow_credentials=False` porque el chatbot no usa cookies ni credenciales de sesión (el JWT no viaja al chatbot).

## Prompts

`app/prompts/`:
- `recommendation_prompt.txt`: redacción de recomendaciones (no inventar títulos/autores/disponibilidad; no mencionar datos personales).
- `classify_intent_missing_book.md`, `external_enrichment_open_library.md`, `book_request_offer.md`, `book_request_confirmed.md`: prompts del flujo de solicitud de libros (US-009).

## Clientes MCP

`app/mcp_clients/`:
- `biblioteca_client.py` → Biblioteca-MCP (catálogo, alquileres, preferencias, recomendaciones, feedback).
- `open_library_client.py` → Open Library MCP (enriquecimiento externo).
- `security_audit_client.py` → Security-Audit-MCP (auditoría de entrada/salida).
- `stdio.py` → transporte stdio compartido (reutiliza `McpStdioClient`).

Los comandos de los MCP se configuran por variables de entorno **obligatorias** (sin valores por defecto, ADR-025): `BIBLIOTECA_MCP_COMMAND`, `OPEN_LIBRARY_MCP_COMMAND` y `SECURITY_AUDIT_MCP_COMMAND`. Si falta alguna, el chatbot falla al construir el cliente con un mensaje claro.

### Empaquetado de los MCP en la imagen del chatbot (ADR-030)

La imagen Docker del chatbot incluye los **3 servidores MCP** en `/app/workflow/mcp/` (layout del monorepo preservado: `/app/workflow/mcp/<servidor>/server.py`) y se invocan **en la propia imagen** (`python .../server.py`, sin `npx`). Bajo docker compose el chatbot los lanza con:

```bash
BIBLIOTECA_MCP_COMMAND=python /app/workflow/mcp/biblioteca-mcp/server.py
OPEN_LIBRARY_MCP_COMMAND=python /app/workflow/mcp/open-library-mcp/server.py
SECURITY_AUDIT_MCP_COMMAND=python /app/workflow/mcp/security-audit-mcp/server.py
```

Los servidores reciben `DATABASE_PATH=/app/database/BibliotecaVirtual.db` y `AUDIT_DATABASE_PATH=/app/database/audit.db` desde el volumen compartido `database_data` (misma base SQLite que el backend).

## API

- `GET /health` → `{"status": "healthy"}`.
- `POST /chat` (`{message, userId, conversationId}` + header `X-Correlation-ID`) → `ChatResponse` con `message`, `recommendations`, `action_offer` y `conversation_id`. La correlación se propaga a la auditoría (US-009/012).

## Tests

`python3 -m pytest -q` (102 tests): grafo, memoria conversacional y seguimiento `follow_up`, seguridad, PII masking, recomendaciones, esquemas, cliente LLM (Ollama/nube/fallback), CORS y cliente stdio MCP.
