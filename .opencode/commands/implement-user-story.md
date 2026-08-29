# SOP: implement-user-story

Execute STRICTLY:

1. `project_memory_get_context`. If status is `Approved` → this is a new implementation; continue using the full role plan from `## Role Planning`. If status is `Rejected` → this is rework; continue, but in step 5 implement ONLY the roles/changes listed in the story's `## QA Result` rejection notes, on the existing branch — do not re-invoke roles unaffected by the rejection. If status is neither → STOP. Emit: *"Action rejected: $ARGUMENTS is in status <status>. Execute: approve-user-story $ARGUMENTS"*.

2. **BRANCH VERIFICATION:** `git branch --show-current`. If `main` or not `feature/US-XXX-*`, `bugfix/US-XXX-*`, `hotfix/US-XXX-*` → STOP. Execute Branch Creation SOP.

3. Change status to 'In Progress' with `project_memory_advance_status`.

4. `index_repository` with path `.`.

5. **IMPLEMENT BY ROLES:**
   - **If `Approved` (new implementation):** implement using exactly the roles invoked during planning, per the story's `## Role Planning` section.
   - **If `Rejected` (rework):** implement only the roles/changes needed to fix what's listed in `## QA Result`. Do not touch unrelated roles or areas.
   - Typical responsibilities when a role is invoked:
     - @backend-developer — Backend logic: entities, DTOs, services, endpoints, migrations, FluentValidation, permissions. Follow Clean Architecture + CQRS.
     - @frontend-developer — Frontend (APPLY frontend-ui-ux): pages, components, routes, guards. Apply aesthetic guidelines. Document aesthetic direction.
     - @ai-engineer — Chatbot, LangGraph, MCP servers.
     - @technical-writer — Documentation, when documentation impact was identified during planning.

   **Coordination:** If dependency exists, execute sequentially (backend → frontend).

6. **BUILD VERIFICATION:** Run `dotnet build` if backend code was touched in step 5 (@backend-developer or backend-adjacent changes from @architect/@ai-engineer); run `npm run build` if frontend code was touched (@frontend-developer). If the story touched both, or cross-module impact is uncertain, run both. If errors → STOP and fix (see AGENTS.md § Circuit Breaker for the retry limit).

7. `index_repository` with path `.`.

8. **BRANCH:** `git branch --show-current`

9. **UPDATE STORY FILE:** Replace `## Implementation Notes` with summary per role.

10. **PUSH:** `git status --porcelain` → `push_files` with full list. Commit message: `feat(US-XXX): description`.

11. **SYNCHRONIZE:** `git fetch origin` && `git reset --hard origin/<branch-name>`

12. Move story to 'Implemented' with `project_memory_advance_status`.

13. **FINAL PUSH:** `git status --porcelain` → `push_files` with full list.

14. **FINAL SYNC:** `git fetch origin` && `git reset --hard origin/<branch-name>`

15. **CLOSE** and emit exactly:
Implementation for $ARGUMENTS complete.
Roles executed: [list only the roles actually invoked in step 5, each with a one-line summary]

To validate: qa-check $ARGUMENTS
