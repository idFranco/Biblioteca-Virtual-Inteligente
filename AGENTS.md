## Project Goal
Develop a fullstack intelligent virtual library system with:
- User registration and login.
- JWT authentication.
- Roles and permissions.
- Book catalog.
- Book rentals with due dates.
- Return flow.
- Due-date notifications.
- Integrated chatbot.
- LangChain + LangGraph.
- Persistent memory.
- Internal domain MCP server (`Biblioteca-MCP`).
- Internal security MCP server (`Security-Audit-MCP`) that audits chatbot input and output.
- External MCP server based on Open Library.
- AI Engineering workflow using opencode.
- External LLM provider via API.

## CRITICAL BEHAVIORAL OVERRIDES (READ FIRST)
The following constraints override any natural tendency, internal checklist, or workflow:
1. **ERROR HALTING:** If any terminal command (especially `git pull`, `git fetch`, or `dotnet`) returns a `fatal:`, `error:`, or fails authentication, YOU MUST HALT IMMEDIATELY. Do not attempt workarounds. Do not continue to the next step.
2. **NO LOCAL BRANCH CREATION:** You lack authorization to create local branches via Bash. The commands `git checkout -b` and `git branch` are BLACKLISTED. You must use the `create_branch` MCP tool.
3. **NO CLI PULL REQUESTS:** `gh pr create` and `curl` for Pull Requests are BLACKLISTED. You must use the `create_pull_request` MCP tool.
4. **NO PLACEHOLDERS OR STUBS:** You are STRICTLY FORBIDDEN from writing incomplete code. Do not use `// TODO`, `throw new NotImplementedException()`, or hardcoded mock data unless explicitly requested. You must write the complete, production-ready logic for every file you touch.
5. **ZERO TOLERANCE FOR BROKEN BUILDS:** Before ANY `git commit`, you MUST ensure the project compiles successfully (`dotnet build` / `npm run build`). If there are compilation errors or validation failures, YOU MUST FIX THEM. You are forbidden from committing broken or non-compiling code.
6. **STRICT ARCHITECTURAL ADHERENCE:** You cannot bypass the Clean Architecture or CQRS rules to save time. Controllers MUST remain empty except for dispatching to the Mediator. All business logic MUST reside in Handlers, and all input MUST be validated by FluentValidation before processing.
7. **CIRCUIT BREAKER (NO INFINITE LOOPS):** If you encounter an error (compilation, test failure, or terminal error) and fail to fix it after THREE (3) consecutive attempts, YOU MUST STOP. Do not continue guessing. Halt execution, explain the deadlock, and ask the user for guidance to prevent token waste.
8. **ZERO HARDCODED SECRETS:** You are STRICTLY FORBIDDEN from hardcoding sensitive data (passwords, JWT secrets, connection strings, API keys) in the source code. You must use environment variables, `.env` files (which must be in `.gitignore`), or ASP.NET User Secrets.
9. **NO DESTRUCTIVE ACTIONS:** You are STRICTLY FORBIDDEN from executing destructive bash commands such as `rm -rf /`, `rm -rf *`, dropping databases, or running `git push --force`. Always ask for explicit human permission before deleting significant amounts of files or altering remote Git history.
10. **CONVENTIONAL COMMITS REQUIRED:** Every Git commit message MUST follow the Conventional Commits specification and include the User Story ID. Example: `feat(US-001): initialize ASP.NET Core and Clean Architecture`. Do not use generic messages like "update files".
11. **NO RULE NEGOTIATION OR WORKAROUND SUGGESTIONS:** You are STRICTLY FORBIDDEN from asking the user for permission to bypass any constraints (e.g., never ask "Would you like me to proceed with local git operations?"). Rules are absolute. If a required tool (like GitHub MCP) is missing or fails, you must report the failure and STOP. Do not offer alternative paths that violate your established Hard Constraints.

## Session Recovery Rule
If an agent resumes after a session interruption (restart, logout, or context loss),
before executing any command it must:

1. Invoke `project_memory_get_context` to read the current story status.
2. Execute `git branch --show-current` to verify the active branch.
3. Cross-reference: if the story is `Approved` or `In Progress` but the active 
   branch is `main`, the session was interrupted during branch creation.
4. In that case, execute the Branch Creation SOP from git-rules.md before 
   proceeding with any implementation command.
5. Never assume that a story in `Approved` state implies a feature branch exists.
6. If the story is `In Progress` and a valid branch exists, verify that implementation files were actually created before proceeding to push. Invoke `index_repository` with path '.' (current repository root) to confirm the codebase state matches the story scope. If implementation appears incomplete or no new files exist for this story, resume from step 5 of `implement-user-story` before attempting any push.

## Technology Stack
| Component | Technology |
|---|---|
| Frontend | React + TypeScript |
| Frontend Routing | React Router |
| Frontend UI | Tailwind CSS + shadcn/ui |
| Frontend State | Context API or Zustand |
| Backend | ASP.NET Core Web API — .NET 9 |
| ORM | Entity Framework Core |
| Database | SQLite |
| Authentication | ASP.NET Core Identity + JWT |
| Authorization | Roles + Claims + Policies |
| Chatbot API | Python + FastAPI |
| AI Framework | LangChain |
| Conversation Graph | LangGraph |
| LLM | External provider via API |
| MCP Own Server | Python + FastMCP / MCP SDK — `Biblioteca-MCP` & `Security-Audit-MCP` |
| MCP External Server | Open Library MCP server |
| Containers | Docker Compose |

## Roles and Permissions
Base roles: Admin, Bibliotecario, Usuario
Permissions: books.read, books.create, books.update, books.delete, rentals.create, rentals.return, rentals.view_own, rentals.view_all, users.manage, roles.manage, notifications.read, chat.use

## Functional Use Cases
1. User registration
2. Login with JWT
3. Role and permission management
4. UI conditioned by role/permission
5. Book search and filtering
6. Book CRUD
7. Book rental with due date
8. Due-date notification
9. Book return
10. Chatbot with persistent memory and graph

## Mandatory Context Loading
Before answering, planning, editing, or creating files, every agent must:
1. Invoke the `project_memory_get_context` tool via the MCP `project-lifecycle` server to initialize the project context and read the active story status.
2. Use `codebase-memory` tools to map the current repository structure and architecture if needed.
3. Read `.opencode/instructions/READ-GRAPH-FIRST.md`
4. Read `.opencode/memory/DECISIONS.md`

If an agent needs to know its specific behavior, it must read its corresponding ROLE.md file.

## Strict Execution Rules (Hard Constraints)
### 1. Command-Driven Interaction Only
The human user is forbidden from entering loose requirements or free-form text. Every interaction MUST begin with `read-graph`, `create-user-story`, `plan-user-story`, `approve-user-story`, `implement-user-story`, or `qa-check`.
* **Enforcement:** It is STRICTLY PROHIBITED to infer the user's intent if the rule is not followed. You MUST stop immediately, refuse to execute any tool, and respond exactly as follows: *"Action rejected: Strict interaction rule. You must use the corresponding command to proceed (e.g., approve-user-story US-XXX)."*

### 2. Phase Transitions & Handoffs (NO QUESTIONS ALLOWED)
When an agent finishes its required tasks for a specific phase (e.g., Planning is complete, Implementation is complete, or QA is complete), you are STRICTLY FORBIDDEN from asking the user if they want to proceed, approve, or continue (e.g., never ask "Do you want to proceed?", "¿Apruebas la implementación?", "¿Deseas continuar?"). 
*   **Rule:** You MUST simply report the final status of the phase, halt all execution, and output a strict instructional block dictating the exact terminal command the user must run next.
*   **Format Example:** 
    "The Planning phase for US-XXX is complete. 
    To authorize the next phase, you MUST execute the following command in your terminal:
    `approve-user-story US-XXX`"

### 3. Plan-Before-Build Barrier
It is strictly forbidden to write, modify, or delete source code without explicit and visible prior planning. 
* **PLAN Phase:** Occurs exclusively via `plan-user-story`. NO CODE IS TOUCHED.
* **BUILD Phase:** Occurs exclusively via `implement-user-story`. The agent verifies with the MCP that the story is `Approved` or `Rejected`.

## Dynamic Context Routing (READ BEFORE ACTING)
Do NOT guess architectural rules or conventions. Based on the task, you MUST use your `read` tool to load the specific constraints from the `.opencode/instructions/` directory BEFORE writing code or planning:

- If touching **C#, API, or SQLite**: Read `.opencode/instructions/backend-rules.md`
- If touching **React or UI**: Read `.opencode/instructions/frontend-rules.md`
- If touching **Python or LangGraph**: Read `.opencode/instructions/chatbot-rules.md`
- If creating or modifying an **MCP Server**: Read `.opencode/instructions/mcp-rules.md`
- If using **git or branching**: Read `.opencode/instructions/git-rules.md`

## AI Engineering & Lifecycle Rules
- **User Story Driven:** No agent may implement code directly from a new requirement unless the User Story has been planned and the user explicitly approves implementation.
- **Evolutive Development:** Agents must not assume all modules exist. Read the project graph, detect current state, identify smallest increment, propose plan, implement, and update MCP context.
- **Validation Failure:** If QA validation fails, set status to `Rejected` via MCP. Do not revert code automatically.
- **PR Gate:** A User Story CANNOT be moved to `Validated` status without successfully executing the GitHub MCP tool `create_pull_request`. Do not simulate or skip this step.
- **Documentation Gate:** Before moving to `Validated`, the QA agent MUST physically update the corresponding file in `workflow/opencode/user-stories/` (adding executed Technical Plan and QA results) and log the iteration in a specific file inside `workflow/opencode/ai-engineering/`. The filename MUST be based on the active branch, but you MUST replace any slashes (`/`) with dashes (`-`) to avoid creating subdirectories (e.g., `workflow/opencode/ai-engineering/feature-US-001-ai-engineering.md`).

## Architecture & Data Flow

**1. Core Application Flow:**
* `[Frontend React]` --(HTTP + JWT)--> `[Backend ASP.NET Core Web API]`
* `[Backend ASP.NET Core Web API]` --(EF Core)--> `[SQLite Core Database]`

**2. AI & Chatbot Flow:**
* `[Frontend React]` --(HTTP)--> `[Chatbot FastAPI]`
* `[Chatbot FastAPI]` --(LangGraph + LangChain)--> `[LLM External API]`

**3. MCP Integrations (Tool Calls from LLM):**
* `[LLM]` --> `[Security-Audit-MCP]` --> Writes to `[Audit Logs SQLite]`
* `[LLM]` --> `[Biblioteca-MCP]` --> Reads/Writes to `[SQLite Core Database]`
* `[LLM]` --> `[Open Library MCP]` --> Fetches from `[External Open Library API]`

**Security Rule:** Every chatbot request is audited by `Security-Audit-MCP` before reaching the graph, and every response is audited before reaching the frontend.

## General Code Conventions
- English names for code.
- Spanish allowed only in user-facing text.
- Small files and functions. Avoid duplication.
- Do not introduce unrelated technologies or change the stack without asking.
- Always ensure architectural changes are reflected in the project state via MCP tools.
- **Version Control:** Ensure a comprehensive `.gitignore` file is created at the root of the repository during the initial architecture setup. It must strictly ignore Node.js (`node_modules/`), Python (`__pycache__/`, `.venv/`), .NET (`bin/`, `obj/`), SQLite databases (`*.db`, `*.sqlite`), IDE folders (`.vscode/`, `.idea/`), and environment configuration files (`.env`).

## Directory Structure & Module Mapping (Strict Rule)
All source code and project files MUST be created strictly inside their designated subdirectories within the `workflow/` folder. Do not create application folders in the root directory.

- **Frontend (React):** `workflow/frontend/`
- **Backend (.NET 9):** `workflow/backend/`
- **Chatbot (FastAPI / LangGraph):** `workflow/chatbot/`
- **Database (SQLite files):** `workflow/database/`
- **MCP Servers (Python):** `workflow/mcp/`
- **Documentation & Context:** `workflow/opencode/`

## Required User Story Flow
For every new requirement:
1. Read project context via MCP tools.
2. Create or update a User Story in `workflow/opencode/user-stories/`.
3. Ask the Functional Analyst to define functional scope and acceptance criteria.
4. Ask the Architect to analyze architectural impact.
5. Ask the Technical Lead to create the technical plan.
6. Ask impacted implementation roles to plan their work:
   - Backend Developer.
   - Frontend Developer.
   - AI Engineer.
7. Ask QA to define the validation plan.
8. Ask Technical Writer to define documentation impact.
9. Ensure the story status is advanced to 'Planned' using the `project-lifecycle` MCP tools.
10. The Technical Lead must update the User Story file to reflect the 'Approved' status
    before any implementation begins. This is done exclusively via the `approve-user-story` command.

The `implement-user-story` command must verify the context state is explicitly `Approved`
or `Rejected` before editing any code.

If the status is not `Approved` or `Rejected`, the agent must:
1. Stop immediately.
2. Show the user the current status from the MCP.
3. Output exactly: "Action rejected: $ARGUMENTS is in status '<status>'.
   To authorize implementation, you MUST execute: approve-user-story $ARGUMENTS"
4. Halt. Do not ask questions. Do not offer to approve on behalf of the user.

## AI Engineering Workflow
Every meaningful task must follow this loop:

1. Read project graph and memory.
2. Identify impacted modules.
3. Select role and skill.
4. Produce a plan.
5. Ask for confirmation if the change is large.
6. Implement minimal change.
7. Run or describe validation.
8. Update process state via MCP tools.
9. Update documentation if needed.

## Required Output Format for Agents

When completing a task, respond with:

Summary
Files changed
Reasoning
Validation performed
Risks
Next steps
