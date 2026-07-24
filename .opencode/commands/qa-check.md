# SOP: qa-check

Ejecuta ESTRICTAMENTE los siguientes pasos en orden para la historia proporcionada. Si alguna herramienta falla, detente inmediatamente.

1. **MANDATORIO:** Invoca `index_repository` con el path `.`.
2. Revisa cambios y valida todos los criterios de aceptación de la historia.
3. **OBTENER RAMA:** Ejecuta `git branch --show-current` y guarda el nombre exacto.
4. **BIFURCACIÓN DE ESTADO:** Si algún criterio falla, invoca `project_memory_advance_status` a 'Rejected', documenta el fallo en el `.md` de la historia y DETENTE. Emite exactamente: *"QA validation failed for US-$ARGUMENTS. Story set to Rejected. To fix and retry, execute: implement-user-story $ARGUMENTS"*.
5. **DOCUMENTACIÓN ESTRICTA:** Reemplaza explícitamente el texto 'Pending' en las secciones 'Implementation Notes' y 'QA Result' del archivo `.md` de la historia con los resultados reales. OBLIGATORIO: Crea la bitácora de iteración directamente en la raíz de `workflow/opencode/ai-engineering/`. Para el nombre del archivo, reemplaza las barras `/` de la rama por guiones `-` (ej. `feature-US-001-base-setup.md`). TIENES PROHIBIDO crear subcarpetas.
6. **PUSH PREVIO VÍA MCP:** Utiliza `push_files` para subir las documentaciones Y el archivo `project-memory-mcp/project_state.json` a la rama remota. Luego ejecuta `git fetch origin` y `git reset --hard origin/<nombre-de-la-rama>` (reemplazando con el nombre exacto).
7. **CREAR PR (PR GATE):** Utiliza EXCLUSIVAMENTE la herramienta `create_pull_request` del MCP de GitHub. Si la herramienta falla o retorna un error, DETENTE INMEDIATAMENTE. No avances el estado. Emite exactamente: *"PR creation failed. Story NOT marked as Validated. Fix the GitHub MCP error and re-run qa-check $ARGUMENTS"*.
8. **AVANCE DE ESTADO:** SOLO SI el PR fue creado exitosamente en el paso 7, invoca OBLIGATORIAMENTE la herramienta `project_memory_advance_status` para cambiar el estado a 'Validated'.
9. **PUSH FINAL VÍA MCP:** Como el paso anterior modificó los archivos locales de memoria e historia, invoca OBLIGATORIAMENTE una segunda vez la herramienta `push_files` para subir todos los archivos modificados o sin seguimiento en el árbol de trabajo (working directory) a la rama remota del PR.
10. **SINCRONIZACIÓN DE ÁRBOL LOCAL:** Ejecuta en la terminal `git fetch origin` y luego `git reset --hard origin/<nombre-de-la-rama>` para que tu árbol de trabajo local quede exactamente idéntico al remoto.
11. **CIERRE Y NOTIFICACIÓN:** Emite EXACTAMENTE este bloque final: *"The QA phase for US-$ARGUMENTS is complete and the PR has been created. To merge and close this story, review and merge the Pull Request on GitHub."*
