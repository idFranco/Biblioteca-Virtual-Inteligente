# SOP: qa-check

Ejecuta ESTRICTAMENTE los siguientes pasos en orden para esta historia. Si alguna herramienta falla, detente inmediatamente.

1. **MANDATORIO:** Invoca `index_repository` con path `.`.
2. Revisa cambios y valida todos los criterios de aceptación de la historia.
3. **OBTENER RAMA:** Ejecuta `git branch --show-current` y guarda el nombre exacto.
4. **BIFURCACIÓN DE ESTADO:** Si algún criterio falla, invoca `project_memory_advance_status` a 'Rejected', documenta el fallo en el `.md` de la historia y DETENTE. Emite exactamente: "QA validation failed for US-$ARGUMENTS. Story set to Rejected. To fix and retry, execute implement-user-story $ARGUMENTS".
5. **DOCUMENTACIÓN ESTRICTA:** Reemplaza explícitamente el texto 'Pending' en las secciones 'Implementation Notes' y 'QA Result' del `.md` de la historia con resultados reales. OBLIGATORIO: Crea la bitácora de iteración directamente en la raíz de `workflow/opencode/ai-engineering/`. Para el nombre del archivo, reemplaza las barras `/` de la rama por guiones `-` (ej. `feature-US-001-base-setup.md`). TIENES PROHIBIDO crear subcarpetas.
6. **PUSH PREVIO VÍA MCP:** Ejecuta `git status --porcelain` para identificar TODOS los archivos modificados o sin seguimiento (documentación, `project_state.json`, y cualquier otro archivo tocado por MCPs laterales). Invoca `push_files` con esa lista completa. Luego ejecuta `git fetch origin` y `git reset --hard origin/<nombre-de-la-rama>`.
7. **CREAR PR (PR GATE):** Utiliza EXCLUSIVAMENTE la .md `create_pull_request` del MCP de GitHub. Si las herramientas falla o retorna un error, DETENTE INMEDIATAMENTE. No avances el estado. Emite exactamente: "PR creation failed. Story NOT marked as Validated. Fix the GitHub MCP error and re-run qa-check $ARGUMENTS".
8. **VERIFICACIÓN DE MERGEABILIDAD (PRERP):** Al crear el PR en el paso 7 mediante MCP, verificar el estado "mergeable"/conflictos en la respuesta.
   - **Si es mergeable:** continúa al paso 9.
   - **Si NO es mergeable (conflictos con main):** DETENTE INMEDIATAMENTE. No intentes resolver conflictos localmente. Emite: "Pull Request created but has conflicts with main." No avances hasta que sea mergeable.
9. **AVANCE DE ESTADO:** SOLO tras éxito del paso 7 y mergery en 8, invoca `project_memory_advance_status` a 'Validated'.
10. **PUSH FINAL VÍA MCP:** El paso anterior modificó los archivos locales, invoca una segunda vez `push_files` para subir TODOS los archivos del árbol de trabajo a la rama.
11. **SINCRONIZACIÓN DE ÁRBOL LOCAL:** Ejecuta `git fetch origin` y luego `git reset --hard origin/<nombre-de-la-rama>`.
12. **CIERRE Y NOTIFICACIÓN:** Emite exactamente: "The QA phase for US-$ARGUMENTS is complete and the PR has been created. To merge and close this story, review and merge the Pull Request on GitHub."
