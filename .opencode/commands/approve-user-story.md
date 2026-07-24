# SOP: approve-user-story

Ejecuta ESTRICTAMENTE los siguientes pasos en orden:

1. Verifica que la historia `$ARGUMENTS` existe y está en estado 'Planned' usando `project_memory_get_context`. Si no existe o no está en 'Planned', DETENTE y reporta el estado actual.
2. Si el estado es correcto, invoca OBLIGATORIAMENTE la herramienta `project_memory_advance_status` para cambiar el estado a 'Approved'.
3. **EDICIÓN OBLIGATORIA:** Lee el archivo `.md` de la historia en `workflow/opencode/user-stories/$ARGUMENTS.md`. Verifica si la sección `## Implementation Approval` ya contiene "Approved by user." — si ya lo contiene, omite la edición y continúa al paso 4. Si contiene cualquier otro valor, usa `edit` para reemplazarlo exactamente por "Approved by user." sin modificar ninguna otra sección del archivo.
4. Confirma al usuario con exactamente este bloque: "US-$ARGUMENTS has been approved for implementation. To start the development phase, you MUST execute the following command: implement-user-story $ARGUMENTS"
