# MCP Servers — Python + FastMCP

Servidores MCP del proyecto en `workflow/mcp/`. Son la capa de integración para que el chatbot (y los agentes de desarrollo) accedan a la base de datos y a fuentes externas sin llamar al backend directamente (ADR-006/007/011).

```
workflow/mcp/
├── common/                 # Configuración y acceso SQLite compartidos
│   ├── settings.py         # DATABASE_PATH (obligatoria) + require_env
│   └── sqlite.py           # DbAccess (lectura WAL; escritura acotada)
├── biblioteca-mcp/         # Dominio: catálogo, disponibilidad, alquileres, preferencias, feedback
├── security-audit-mcp/     # Seguridad: auditoría de entrada/salida del chatbot
└── open-library-mcp/       # Externo: Open Library API (búsqueda, detalle, verificación ISBN)
```

## Configuración por variables de entorno (fail-fast)

Toda la configuración se lee de variables de entorno **obligatorias** (ADR-025). Si falta una, el servidor aborta con un mensaje claro. No hay valores por defecto hardcodeados.

| Variable | Servidor | Descripción |
|---|---|---|
| `DATABASE_PATH` | Biblioteca-MCP, Security-Audit-MCP | Ruta absoluta (o relativa a la raíz del repo) de la base SQLite principal |
| `AUDIT_DATABASE_PATH` | Security-Audit-MCP | Ruta de la base SQLite de auditoría (`audit_events`) |
| `GROQ_API_KEY` | Security-Audit-MCP | Clave del LLM usado para detección de inyección/datos sensibles |

## Biblioteca-MCP (dominio)

Servidor de solo lectura (salvo `registrar_feedback`, ADR-022) que consulta la base SQLite del backend.

| Herramienta | Tipo | Descripción |
|---|---|---|
| `ping` | lectura | Verificación de vida |
| `buscar_libros(search, limit)` | lectura | Búsqueda en catálogo interno |
| `verificar_disponibilidad(book_id)` | lectura | Copias disponibles de un libro |
| `get_estado_lectura(user_id)` | lectura | Estado de lectura del usuario |
| `consultar_alquileres_usuario(user_id)` | lectura | Historial de alquileres (JOIN catálogo) |
| `consultar_libro_en_curso(user_id)` | lectura | Alquiler activo actual |
| `obtener_preferencias(user_id)` | lectura | Preferencias de género |
| `listar_recomendaciones_por_genero(user_id, limit)` | lectura | Recomendaciones por historial/preferencias |
| `registrar_feedback(user_id, book_id, rating, comment)` | **escritura acotada** | Persiste feedback en `Feedbacks` |

## Security-Audit-MCP (seguridad)

Audita la **entrada** del chatbot (antes del grafo) y la **salida** (antes del frontend) para detectar prompt injection y datos sensibles (ADR-008). Registra cada evento en la base de auditoría (`audit_events`) **sin PII**.

| Herramienta | Descripción |
|---|---|
| `audit_user_input(text, correlation_id)` | Auditoría de entrada (bloqueo si no es segura) |
| `audit_model_output(text, correlation_id)` | Auditoría de salida antes del frontend |
| `detect_prompt_injection(text)` | Detección de prompt injection |
| `detect_sensitive_data(text)` | Detección de datos sensibles (emails, tokens, claves) |
| `sanitize_text(text)` | Redacción de PII / contenido peligroso |
| `register_audit_event(event_type, result, correlation_id)` | Registro estructurado de auditoría |

## Open Library MCP (externo)

Acceso a la API pública de Open Library.

| Herramienta | Descripción |
|---|---|
| `ol_search_books(query, limit)` | Búsqueda de obras |
| `ol_get_book_details(key)` | Detalle de una obra por clave OL |
| `ol_verify_by_isbn(isbn)` | Verificación de que un ISBN existe y coincide (ADR-020) |

## Uso

Cada servidor se lanza como subproceso por stdio. El chatbot configura los comandos por variables obligatorias (`BIBLIOTECA_MCP_COMMAND`, `OPEN_LIBRARY_MCP_COMMAND`, `SECURITY_AUDIT_MCP_COMMAND`) y reutiliza `McpStdioClient` (ver `workflow/chatbot/README.md`).

Ejecución local de un servidor:

```bash
export DATABASE_PATH=/ruta/a/BibliotecaVirtual.db
python workflow/mcp/biblioteca-mcp/server.py
```

## Tests

```bash
python3 -m pytest workflow/mcp/biblioteca-mcp/tests
python3 -m pytest workflow/mcp/open-library-mcp/tests
```