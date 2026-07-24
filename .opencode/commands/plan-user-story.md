# SOP: plan-user-story

Ejecuta ESTRICTAMENTE los siguientes pasos en orden:

1. Lee la User Story actual con su ID (`$ARGUMENTS`) usando `project_memory_get_context`.
2. Solicita al usuario el nombre de la nueva rama en este formato exacto: *"¿Qué nombre deseas usar para la rama de $ARGUMENTS? (Formato requerido: tipo/US-XXX-descripción en kebab-case. Ejemplos válidos: feature/US-001-auth-setup, bugfix/US-002-login-fix)"*. Valida que comience con `feature/`, `bugfix/` o `hotfix/`, incluya el ID de la historia y use kebab-case. Si no cumple el formato, rechaza y vuelve a preguntar.
3. **PREPARACIÓN:** Ejecuta `git checkout main` y luego `git pull origin main`. **REGLA DE PARADA:** Si la terminal devuelve un error (ej. fatal, could not read Username, conflictos), ESTÁ ESTRICTAMENTE PROHIBIDO AVANZAR. Detente y notifica al usuario.
4. **CREACIÓN (MANDATORIO):** Tienes PROHIBIDO usar comandos de terminal como `git checkout -b` o `git branch`. Utiliza EXCLUSIVAMENTE la herramienta del MCP de GitHub `create_branch` para crear la rama en el remoto. Si el MCP falla, DETENTE.
5. **SINCRONIZACIÓN:** Solo si el paso anterior fue exitoso, ejecuta `git fetch origin` y `git checkout <nombre>`.
6. Elabora el plan técnico completo para la historia: análisis funcional, impacto arquitectónico, plan por roles, criterios de validación y documentación.
7. **MANDATORIO:** Actualiza el estado a 'Planned' utilizando exclusivamente la herramienta `project_memory_advance_status`.
8. **DETENTE:** No preguntes nada. No ofrezcas continuar. Emite EXACTAMENTE este bloque sin modificaciones: "The Planning phase for $ARGUMENTS is complete. To authorize the next phase, you MUST execute the following command in your terminal: approve-user-story $ARGUMENTS"
