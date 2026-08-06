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
8. **ZERO HARDCODED SECRETS:** You are STRICTLY FORBIDDEN from hardcoding sensitive data (passwords, JWT secrets, connection strings, API keys) in the source code. You MUST use environment variables, `.env` files (which must be in `.gitignore`), or ASP.NET User Secrets.
9. **NO DESTRUCTIVE ACTIONS:** You are STRICTLY FORBIDDEN from executing destructive bash commands such as `rm -rf /`, `rm -rf *`, dropping databases, or running `git push --force`. Always ask for explicit human permission before deleting significant files or altering remote Git history.
10. **CONVENTIONAL COMMITS REQUIRED:** Every Git commit message MUST follow the Conventional Commits specification and include the User Story ID. Example: `feat(US-001): initialize ASP.NET Core and Clean Architecture`. Do not use generic messages like "update files".
11. **NO RULE NEGOTIATION:** You are STRICTLY FORBIDDEN from asking the user for permission to bypass any constraints (e.g., never ask "Would you like me to proceed with local git operations?"). Rules are absolute. If a required tool (like GitHub MCP) is missing or fails, you must report the failure and STOP.

## Session Recovery Rule
If an agent resumes after a session interruption (restart, logout, or context loss),
before executing any command it must:

1. Invoke `project_memory_get_context` to read the current story status.
2. Execute `git branch --show-current` to verify the active branch.
3. Cross-reference: if the story is `Approved` or `In Progress` but the active branch is `main`, the session was interrupted during branch creation.
4. In that case, execute the Branch Creation SOP from git-rules.md before proceeding with any implementation.
5. Never assume that a story in `Approved` state implies a feature branch exists.
6. If the story is `In Progress` and a valid branch exists, verify that implementation files were actually created before proceeding to push.

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

## Roles
Base roles: Admin, Bibliotecario, Usuario
Permissions: books.read, books.create, books.update, books.delete, rentals.create, rentals.return, rentals.view_own, rentals.view_all, users.manage, roles.manage, notifications.read, chat.use

## Functional Use Cases
1. User registration
2. Login with JWT
3. Role and permission management
4. UI by role/permission
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
3. Read `.code/instructions/READ-GRAPH-FIRST.md`
4. Read `.opencode/memory/DECISIONS.md`

## Strict Execution Rules (Hard Constraints)
### 1. Command-Driven Interaction Only
The human user is forbidden from entering loose requirements or free-form text. Interactions MUST begin with a user-story command.

### 2. Plan-Before-Build Barrier
- **PLAN Phase:** occurs exclusively via `plan-user-story`. NO CODE IS TOUCHED.
- **BUILD Phase:** occurs exclusively via `implement-user-story`, which verifies the story is `Approved` or `Rejected`.

### 3. Phase Transitions & Handoffs
Report final status, halt, and dictate the exact terminal command for the next phase.

## AI Engineering & Lifecycle Rules
- **User Story Driven:** No implementation without a planned and approved User Story.
- **Validation Failure:** If QA validation fails, set status to `Rejected` via MCP.
  - **Rework Transition:** A rejected story returns to `In Progress` on the SAME branch.
- **PR Gate:** Move to `Validated` ONLY after the GitHub MCP `create_pull_request` succeeds.
- **Documentation Gate:** QA must update the story file and write the iteration to `workflow/opencode/ai-engineering/feature-<branch>.md` (slashes → dashes).

## Architecture And Data Flow
* `[Frontend React]` --(HTTP+JWT)--> `[Backend ASP.NET Core Web API]` --(EF Core)--> `[SQLite]`
* `[Frontend]` --(HTTP)--> `[Chatbot FastAPI]` --(LangGraph+LangChain)--> `[LLM]`
* `[LLM]` --> `[Security-Audit-MCP]` --> `[Audit Logs SQLite]`
* `[LLM]` --> `[Biblioteca-MCP]` --> `[SQLite Core Database]`
* `[LLM]` --> `[Open Library MCP]` --> `[External API]`

**Security Rule:** Every chatbot request and response is audited by `Security-Audit-MCP`.

## General Conventions
- English names for code.
- Spanish allowed in user-facing text.
- Small files, no duplication.
- `.gitignore` must ignore node_modules/, __pycache__/, bin/, obj/, *.db, .vscode/, .env.
- Reflect architectural changes in the project state via MCP tools.

## Directory (workflow)
All source lives under `workflow/`:
- Frontend: `workflow/frontend/`
- Backend: `workflow/backend/`
- Chatbot: `workflow/chatbot/`
- Database: `workflow/database/`
- MCP: `workflow/mcp/`
- Docs: `workflow/opencode/`

## Required Output Format for Agents
Summary / Files changed / Reasoning / Validation performed / Risks / Next steps
