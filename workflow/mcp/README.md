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
| `API_KEY_GROQ` | Security-Audit-MCP | Clave del LLM usado para detección de inyección/datos sensibles (solo auditoría, ADR-029) |

Opcionales para Security-Audit-MCP (si no se definen, se usan los valores por defecto del servidor): `GROQ_API_URL` (endpoint de Groq), `GROQ_MODEL` (modelo de auditoría) y `GROQ_TIMEOUT_SECONDS` (timeout de la llamada).

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

## Despliegue en Docker (imagen del chatbot)

Desde US-016 (ADR-030), los **3 servidores MCP se empaquetan dentro de la imagen Docker del chatbot** y se invocan **en la propia imagen** (sin `npx`). El `Dockerfile` del chatbot usa como build context la **raíz del repositorio** (con un `.dockerignore` raíz nuevo) y copia los servidores a `/app/workflow/mcp/<servidor>/server.py`.

Bajo `docker compose`, el chatbot inyecta a los MCP:

| Variable | Valor en compose | Descripción |
|---|---|---|
| `DATABASE_PATH` | `/app/database/BibliotecaVirtual.db` | Misma base SQLite que el backend (volumen compartido `database_data`) |
| `AUDIT_DATABASE_PATH` | `/app/database/audit.db` | Base de auditoría de Security-Audit-MCP (mismo volumen) |
| `API_KEY_GROQ` | valor del `.env` | Usada solo por Security-Audit-MCP para auditar entrada/salida |
| `BIBLIOTECA_MCP_COMMAND` | `python /app/workflow/mcp/biblioteca-mcp/server.py` | Comando stdio en-imagen |
| `OPEN_LIBRARY_MCP_COMMAND` | `python /app/workflow/mcp/open-library-mcp/server.py` | Comando stdio en-imagen |
| `SECURITY_AUDIT_MCP_COMMAND` | `python /app/workflow/mcp/security-audit-mcp/server.py` | Comando stdio en-imagen |

**Diferencia vs. ejecución local standalone:** localmente cada servidor se lanza con su propio intérprete Python (p. ej. `python workflow/mcp/biblioteca-mcp/server.py`) y `DATABASE_PATH` apunta a una ruta del repo (`./workflow/database/BibliotecaVirtual.db`); en Docker los servidores corren **dentro del contenedor del chatbot** leyendo el mismo archivo SQLite del volumen `database_data` que el backend. El layout `/app/workflow/mcp/<servidor>/server.py` preserva la estructura del monorepo, por lo que el bootstrap `sys.path` de `common/settings.py` (resolución vía `parents[3]`) sigue funcionando sin cambios en la imagen.

## Tests

```bash
python3 -m pytest workflow/mcp/biblioteca-mcp/tests
python3 -m pytest workflow/mcp/open-library-mcp/tests
```
