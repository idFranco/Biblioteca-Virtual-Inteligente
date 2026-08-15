# SOP: implement-user-story

Execute STRICTLY:

1. `project_memory_get_context`. If status not `Approved` or `Rejected` → STOP. Emit: *"Action rejected: US-$ARGUMENTS is in status <status>. Execute: approve-user-story $ARGUMENTS"*.

2. **BRANCH VERIFICATION:** `git branch --show-current`. If `main` or not `feature/US-XXX-*`, `bugfix/US-XXX-*`, `hotfix/US-XXX-*` → STOP. Execute Branch Creation SOP.

3. Change status to 'In Progress' with `project_memory_advance_status`.

4. `index_repository` with path `.`.

5. **IMPLEMENT BY ROLES (MANDATORY):**
   a. @backend-developer — Backend logic: entities, DTOs, services, endpoints, migrations, FluentValidation, permissions. Follow Clean Architecture + CQRS.
   b. @frontend-developer — Frontend (APPLY frontend-ui-ux): pages, components, routes, guards. Apply aesthetic guidelines. Document aesthetic direction.
   c. @ai-engineer — Chatbot, LangGraph, MCP servers.
   d. @technical-writer — Documentation in parallel.

   **Coordination:** If dependency exists, execute sequentially (backend → frontend).

6. **BUILD VERIFICATION:** `dotnet build` and `npm run build`. If errors → STOP and fix.

7. `index_repository` with path `.`.

8. **BRANCH:** `git branch --show-current`

9. **UPDATE STORY FILE:** Replace `## Implementation Notes` with summary per role.

10. **PUSH:** `git status --porcelain` → `push_files` with full list. Commit message: `feat(US-XXX): description`.

11. **SYNCHRONIZE:** `git fetch origin` && `git reset --hard origin/<branch-name>`

12. Move story to 'Implemented' with `project_memory_advance_status`.

13. **FINAL PUSH:** `git status --porcelain` → `push_files` with full list.

14. **FINAL SYNC:** `git fetch origin` && `git reset --hard origin/<branch-name>`

15. **CLOSE** and emit exactly:
Implementation for US-$ARGUMENTS complete.
Roles executed:
- Backend Developer: [summary]
- Frontend Developer (frontend-ui-ux): [summary + aesthetic decisions]
- AI Engineer: [summary]
- Technical Writer: [documentation updated]

To validate: qa-check $ARGUMENTS
