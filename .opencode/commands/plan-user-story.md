# SOP: plan-user-story

Execute STRICTLY:

1. Read User Story with `project_memory_get_context`.
2. Ask user for branch name: *"What name for branch of $ARGUMENTS? (Format: type/US-XXX-description in kebab-case)"*. Validate starts with `feature/`, `bugfix/` or `hotfix/`, includes story ID, uses kebab-case.
   *(Alternative Spanish prompt: "¿Qué nombre deseas usar para la rama de $ARGUMENTS? (Formato requerido: tipo/US-XXX-descripción en kebab-case)")*
3. **PREPARATION:** `git checkout main` then `git pull origin main`. If error → STOP.
4. **CREATION:** Use GitHub MCP `create_branch` (PROHIBITED: `git checkout -b` or `git branch`). If MCP fails → STOP.
5. **SYNCHRONIZATION:** `git fetch origin` and `git checkout <name>`.

6. **INVOKE ALL ROLES (MANDATORY):**
   a. @functional-analyst — Scope and acceptance criteria
   b. @architect — Architecture, modules, data flow, ADRs, security
   c. @backend-developer — Entities, DTOs, services, endpoints, migrations, validations, permissions
   d. @frontend-developer — Pages, components, routes, guards, API integration, UI/UX decisions (APPLY frontend-ui-ux). Document aesthetic direction.
   e. @ai-engineer — Chatbot, LangGraph, MCP servers (Biblioteca-MCP, Security-Audit-MCP), Open Library
   f. @qa — Validation plan: functional, integration, permission, security tests
   g. @technical-writer — Documentation plan: README, architecture, prompts, MCP, LangGraph, logs

7. **CONSOLIDATE** all plans into single coherent technical plan.

8. **VALIDATE WITH FEEDBACK LOOP (max 5 iterations):**
   a. Coherence between roles → If conflict, return to conflicting roles
   b. Completeness → If placeholders, return to specific role
   c. Dependencies → If uncovered, return to involved roles
   d. Acceptance criteria → If not covered, return to corresponding role
   e. Risks → If HIGH, return to responsible role for mitigation
   f. Standards → If not met, return to specific role
   g. Document ALL iterations

9. **RISKS TABLE** (evaluate High/Medium/Low):
   | Risk Type | Evaluation | Responsible Role | Mitigation Strategy |
   |-----------|------------|------------------|---------------------|
   | Technical | | | |
   | Architectural | | | |
   | Security | | | |
   | Performance | | | |
   | Integration | | | |
   | Database | | | |
   | UI/UX | | | |
   | Compliance | | | |

   - **HIGH risks:** Must be mitigated to MEDIUM or LOW before proceeding.
   - **MEDIUM risks:** Must be documented with mitigation strategy.

10. **UPDATE STATUS** to 'Planned' with `project_memory_advance_status`.

11. **UPDATE STORY FILE** (`workflow/opencode/user-stories/$ARGUMENTS.md`):
    - `## Technical Plan` → Consolidated plan
    - `## Role Planning` → Detail per role (Frontend applies frontend-ui-ux)
    - `## Validation Plan` → QA plan
    - `## Documentation Plan` → Technical Writer plan
    - `## Risks` → Risks with mitigation
    - `## Validation Checklist` → Validation executed
    - `## Validation Iterations` → All feedback iterations

12. **PUSH:** `git status --porcelain` → `push_files` with full list.

13. **SYNCHRONIZE:** `git fetch origin` && `git reset --hard origin/<branch-name>`

14. **STOP** and emit exactly:
Planning for US-$ARGUMENTS complete. VALIDATED with all roles.

✅ Coherence: VERIFIED (X iterations) | ✅ Dependencies: DOCUMENTED | ✅ Criteria: VERIFIED ✅ No placeholders: CONFIRMED | ✅ Standards: MET | ✅ Risks: ANALYZED

Feedback iterations: [X] total

[Role] → [issue] → [correction]

Risks: High: [0] | Medium: [X] | Low: [X]

To authorize implementation: approve-user-story $ARGUMENTS
