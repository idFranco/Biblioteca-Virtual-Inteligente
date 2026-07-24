# MCP Rules (Model Context Protocol Servers)

## Architecture Overview
The project must include at least three MCP servers:
1. Own domain MCP server: `Biblioteca-MCP`
2. Own security MCP server: `Security-Audit-MCP`
3. External MCP server: Open Library MCP

## Biblioteca-MCP Tools
`buscar_libros`, `verificar_disponibilidad`, `listar_recomendaciones_por_genero`, `consultar_alquileres_usuario`, `consultar_libro_en_curso`, `get_estado_lectura`, `registrar_feedback`, `obtener_preferencias`

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
