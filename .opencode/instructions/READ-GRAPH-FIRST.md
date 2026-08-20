# READ-GRAPH-FIRST

## User Story Alignment Rule

Before planning or implementing any requirement, the agent must check whether there is an active User Story using the `project-lifecycle` MCP server tools.
If there is no active User Story, the Technical Lead must create one via `project-lifecycle_project_memory_create_story` and stop after planning. Implementation is not allowed until the user explicitly approves the User Story.
The agent must align every lifecycle advancement with the active User Story status.

Required checks via `project-lifecycle_project_memory_get_context`:

1. Which User Story is active?
2. Which use cases are impacted?
3. Which modules are impacted?
4. Which roles must participate?
5. Is the story only planned or approved for implementation?
6. Has the user explicitly approved implementation?

If implementation was not explicitly approved by the user, the agent must stop after planning.

---

## Lifecycle Automation Gate

During the planning phase, no application code or implementation files must be created or modified. 
Once the technical design is consolidated across all required roles, the Technical Lead must invoke the `project-lifecycle_project_memory_advance_status` tool to move the story to 'Planned' and explicitly halt to await user approval.

---

## Implementation Gate
The agent is strictly forbidden from editing application files if the user story status in the MCP context is not explicitly 'Approved' or 'Rejected'. 
Never ask the user if they want to implement.

---

## Progressive Development Rule

After reading the current project context through the MCP tools, the agent must determine the current project stage before acting.

The agent must answer these questions internally:

1. What already exists in the repository? (Use `codebase-memory` tools — `codebase-memory_get_architecture` first, then `codebase-memory_search_code`/`codebase-memory_search_graph` — to scan the workspace before falling back to `grep`/`read`/`bash`).
2. What is only designed but not implemented?
3. What is the user's requested increment?
4. Which modules are affected?
5. Which process state transition must be triggered via the `project-lifecycle` MCP server?

The agent must not implement future phases unless the user explicitly asks for them.

## Required behavior

The agent must:

1. Identify the impacted module.
2. Identify related use cases.
3. Identify relevant skills.
4. Identify the appropriate role.
5. Check previous decisions in `AGENTS.md`.
6. Avoid contradicting previous architecture decisions.
7. Advance the story status using the `project-lifecycle` MCP tools after completing the implementation or QA verification.

## Never skip this step

Do not implement, refactor, create files, or answer architecture questions before initializing the context via the `project-lifecycle_project_memory_get_context` tool.
