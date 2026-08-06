# SOP: implement-user-story

Ejecuta ESTRICTAMENTE los siguientes pasos en orden:

1. Verifica el contexto llamando a `project_memory_get_context`. Si la historia `$ARGUMENTS` no está en estado 'Approved' ni en estado 'Rejected', DETENTE. Emite exactamente: *"Action rejected: US-$ARGUMENTS is in status <status>. To authorize implementation, you MUST execute: approve-user-story $ARGUMENTS"*.
2. **VERIFICACIÓN DE RAMA OBLIGATORIA:** Ejecuta `git branch --show-current`. Si el resultado es 'main' o no coincide con el patrón `feature/US-XXX-*`, `bugfix/US-XXX-*` o `hotfix/US-XXX-*`, DETENTE. No escribas ningún archivo. Emite exactamente: *"Implementation cannot proceed. The current branch is <branch>, which is not a valid feature branch. Execute the Branch Creation SOP from git-rules.md before continuing."* y ejecuta el Branch Creation SOP desde el paso 1.
3. Solo después de confirmar la rama válida: cambia el estado a 'In Progress' con `project_memory_advance_status`.
4. **MANDATORIO:** Invoca la herramienta MCP `index_repository` con el path `.` para tener el mapa técnico actualizado.
5. Implementa el código del incremento solicitado.
6. Al finalizar la codificación, invoca de nuevo `index_repository` con el path `.` para guardar los cambios en tu memoria.
7. **EXTRACCIÓN DE RAMA:** Ejecuta `git branch --show-current` para obtener el nombre exacto de tu rama local.
8. **PUSH VÍA MCP:** Utiliza la herramienta del MCP de GitHub `push_files` para hacer commit y push de todos los archivos creados o modificados directamente a la rama detectada en el paso anterior.
9. **SINCRONIZACIÓN FORZADA:** Para solucionar la desincronización de tu árbol local causada por el MCP, ejecuta `git fetch origin` y luego `git reset --hard origin/<nombre-de-la-rama>` (reemplazando con el nombre exacto).
10. Finalmente, mueve la historia a 'Implemented' con el MCP de ciclo de vida. Emite exactamente: "The Implementation phase for US-$ARGUMENTS is complete. To validate, you MUST execute: qa-check $ARGUMENTS"
11. **PUSH FINAL VÍA MCP:** El paso anterior modificó localmente el archivo `.md` de la historia (status → Implemented). Ejecuta `git status --porcelain` para detectar TODOS los archivos modificados o sin seguimiento, e invoca OBLIGATORIAMENTE `push_files` con esa lista completa antes de emitir el mensaje de cierre.
