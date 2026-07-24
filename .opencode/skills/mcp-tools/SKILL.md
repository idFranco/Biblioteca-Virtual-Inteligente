# Skill MCP Tools

## Purpose

Use this skill for implementing and integrating MCP servers.

## Own MCP Server

Name:

Biblioteca-MCP

## Tools

buscar_libros
verificar_disponibilidad
listar_recomendaciones_por_genero
consultar_alquileres_usuario
consultar_libro_en_curso
get_estado_lectura
registrar_feedback
obtener_preferencias

## Rules

- Tools must have typed inputs.
- Tools must return structured outputs.
- Tools must handle empty results.
- Tools must handle DB errors.
- Do not expose secrets.
- Do not allow arbitrary SQL.
- Do not trust user-provided IDs without validation.

## Checklist

1. Define schemas.
2. Implement DB access.
3. Implement tools.
4. Test tools manually.
5. Document inputs and outputs.
6. Integrate with chatbot.
