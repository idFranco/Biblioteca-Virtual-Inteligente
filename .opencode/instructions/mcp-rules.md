# MCP Rules (Model Context Protocol Servers)

## Architecture Overview
The project must include at least three MCP servers:
1. Own domain MCP server: `Biblioteca-MCP`
2. Own security MCP server: `Security-Audit-MCP`
3. External MCP server: Open Library MCP

## Biblioteca-MCP Tools
`buscar_libros`, `verificar_disponibilidad`, `listar_recomendaciones_por_genero`, `consultar_alquileres_usuario`, `consultar_libro_en_curso`, `get_estado_lectura`, `registrar_feedback`, `obtener_preferencias`

### Contratos de las herramientas de Biblioteca-MCP (US-012)

**`consultar_alquileres_usuario(user_id: str) -> list[dict]`**
- Entrada: `user_id`.
- Salida: lista de alquileres con `id`, `book_id`, `title`, `rented_at`, `due_date`, `returned_at`, `status` (JOIN con catálogo). Lista vacía si no hay historial o la base no está disponible.

**`consultar_libro_en_curso(user_id: str) -> dict | None`**
- Entrada: `user_id`.
- Salida: `dict` con `id`, `book_id`, `title`, `due_date`, `status` del alquiler activo (`Status = 'Active'`), o `None`.

**`obtener_preferencias(user_id: str) -> list[dict]`**
- Entrada: `user_id`.
- Salida: lista con `id`, `genre`, `created_at`. Lista vacía si no hay preferencias.

**`listar_recomendaciones_por_genero(user_id: str, limit: int = 5) -> list[dict]`**
- Entrada: `user_id`, `limit` (1-20, clamp).
- Salida: lista de libros **disponibles** (`AvailableCopies > 0`) de los géneros del historial de alquileres y preferencias, con `id`, `title`, `author`, `genre`, `available_copies` y `reason` (`coincide con tus preferencias` / `coincide con tu historial de lectura`).

**`registrar_feedback(user_id: str, book_id: str, rating: int, comment: str | None = None) -> dict`**
- Entrada: `user_id`, `book_id`, `rating` (1-5, clamp), `comment` opcional.
- Escritura: inserta en la tabla `Feedbacks`. **Única herramienta de escritura** de Biblioteca-MCP.
- Salida: `{"success": true, "id": <id>, "message": "Gracias por tu valoración."}` o `{"success": false, "reason": "..."}` si el libro no existe o la base no está disponible.

## Security-Audit-MCP Tools
`audit_user_input`, `audit_model_output`, `detect_prompt_injection`, `detect_sensitive_data`, `sanitize_text`, `register_audit_event`

## Constraints
- The frontend must never call MCP directly.
- MCP tools are used by chatbot or opencode agents.
- Tools must have clear input and output schemas.
- Tools must not expose secrets.
- Tools must validate user identifiers.
- Tools must return structured errors.
- `Security-Audit-MCP` must run before the graph processes user input and before the graph returns a response.
- `Security-Audit-MCP` must not store raw secrets, tokens or passwords in audit logs.
- `Security-Audit-MCP` complements backend security; it does not replace it.

## Testing Rules
- Test every tool input/output.
- Test unavailable database scenario.
- Test empty results.
- Test `Security-Audit-MCP` against prompt injection attempts.
- Test `Security-Audit-MCP` against sensitive data exposure attempts.

## Forbidden Actions
- Do not read, search, or modify MCP log files directly.
- Do not store raw secrets, tokens or passwords in audit logs.