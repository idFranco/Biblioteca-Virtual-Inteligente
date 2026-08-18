# Chatbot — FastAPI + LangChain + LangGraph

Servicio Python independiente en `workflow/chatbot/` que implementa el asistente de la biblioteca como un **grafo de estados dirigido** (LangGraph). Nunca toca la base de datos directamente: todo el acceso a datos va por los MCP servers (ADR-011).

## Flujo del grafo (US-012)

```text
START
  → audit_input            (Security-Audit-MCP: auditoría de entrada obligatoria)
      ├─ bloqueada → block_response → audit_output
      └─ segura   → load_user_state → classify_intent (route_by_state)
          ├─ recommendation → preferences → internal_catalog → external_enrichment → availability → response → llm_response → audit_output
          ├─ due_reminder   → due_reminder → audit_output
          ├─ overdue        → overdue → audit_output
          ├─ feedback       → feedback → save_feedback → response → llm_response → audit_output
          ├─ book_query     → extract_query → internal_catalog → external_enrichment → availability → response → llm_response → audit_output
          └─ status_plain/other → response → llm_response → audit_output
  audit_output              (Security-Audit-MCP: auditoría de salida obligatoria)
      ├─ sanitizar → sanitize_response → END
      └─ limpio   → END
```

### Nodos

| Nodo | Responsabilidad |
|---|---|
| `audit_input` | Audita la entrada del usuario con Security-Audit-MCP (prompt injection, datos sensibles). Si no es segura, el flujo va a `block_response`. |
| `block_response` | Respuesta de bloqueo segura sin procesar el mensaje en el grafo. |
| `load_user_state` | Carga el estado de lectura del usuario (por MCP) con fallback si MCP no está disponible. |
| `classify_intent` | Clasifica la intención (`recommendation`, `due_reminder`, `overdue`, `feedback`, `book_query`, `status_plain`, `other`) y enruta por `route_by_state`. |
| `preferences` | Carga preferencias de género y perfil de historial vía Biblioteca-MCP (`obtener_preferencias`, `consultar_alquileres_usuario`). |
| `internal_catalog` | Recomienda por historial/preferencias o consulta el catálogo interno por género (`listar_recomendaciones_por_genero`, `buscar_libros`). |
| `external_enrichment` | Enriquece/verifica contra Open Library MCP. |
| `availability` | Filtra las recomendaciones a solo libros disponibles (`verificar_disponibilidad`). |
| `due_reminder` / `overdue` | Informan de alquileres por vencer / vencidos según el estado de lectura. |
| `feedback` / `save_feedback` | Detectan el feedback del usuario y lo persisten vía `registrar_feedback` (Biblioteca-MCP, escritura acotada). |
| `response` | Respuesta heurística (fallback y base). |
| `llm_response` | Redacta la recomendación con el LLM externo (LangChain) **con PII masking**; si no está disponible, usa la heurística de `response`. |
| `audit_output` | Audita la respuesta con Security-Audit-MCP antes de enviarla al frontend. |
| `sanitize_response` | Sanitiza la salida si la auditoría lo requiere. |

## LLM externo (opcional)

- Cliente: `app/llm/client.py` (LangChain `ChatOpenAI`, compatible OpenAI).
- Config: `LLM_API_KEY` (obligatoria para activar) y `LLM_MODEL` (default `gpt-4o-mini`).
- El contexto enviado al proveedor pasa por `app/utils/pii_masker.py` (PII masking obligatorio).
- Si el proveedor no responde (timeout 20s, sin clave o error de red), el nodo devuelve `None` y el grafo usa el fallback heurístico; el chatbot nunca colapsa (ADR-023).

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

## API

- `GET /health` → `{"status": "healthy"}`.
- `POST /chat` (`{message, userId}` + header `X-Correlation-ID`) → `ChatResponse` con `message`, `recommendations` y `action_offer`. La correlación se propaga a la auditoría (US-009/012).

## Tests

`python3 -m pytest -q` (40 tests): grafo, seguridad, PII masking, recomendaciones, esquemas.