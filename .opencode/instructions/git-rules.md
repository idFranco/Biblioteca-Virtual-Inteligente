# Git & Branching Rules

## Branch Verification Before Implementation

Before writing any code, the agent must verify the feature branch exists and is active:

```bash
git branch --show-current
```

If the result is `main` or any branch that does not match the patterns
`feature/US-XXX-*`, `bugfix/US-XXX-*`, or `hotfix/US-XXX-*`:

1. HALT immediately.
2. Report: "Implementation cannot proceed. The current branch is '<branch>', which is not a valid feature branch for this User Story."
3. Execute the Branch Creation SOP from the beginning.
4. Do NOT write, edit, or create any application file until a valid branch is active.

## Strict Branch Creation SOP (Standard Operating Procedure)
Whenever you need to create a new branch for a User Story, you MUST follow this exact 7-step sequence without skipping:
1. Switch to main locally: `git checkout main`
2. Fetch remote changes: `git fetch origin`
3. Conflict Check: If the tree is dirty or `main` has conflicts, HALT immediately and ask the user to resolve them.
4. Pull changes: `git pull origin main`
5. Ask the user for the new branch name.
6. Create on Remote: Use the GitHub MCP tool `create_branch` (Forbidden to use local `git branch` or `git checkout -b`).
7. Checkout locally: Run `git fetch origin` followed by `git checkout <new_branch_name>`.

- **Interactive Branch Naming:** When a new User Story is being planned (during the `plan-user-story` phase), the agent is strictly forbidden from auto-generating or creating the Git branch autonomously. 
- The agent MUST explicitly ask the human user: *"What name would you like to use for this branch? (Format required: type/US-XXX-description)"*
- **Format Validation:** The agent MUST validate the user's input against this standard:
  - Must start with `feature/`, `bugfix/`, or `hotfix/`.
  - Must include the User Story ID (e.g., `US-001`).
  - Must use kebab-case for the description (e.g., `feature/US-001-auth-setup`).
- If the user provides a name that does not match this format, the agent MUST reject it, explain the format error, and ask again. It cannot proceed with `git checkout -b` until a valid name is provided.

## Explicit File Discovery Before Every MCP Push
Before invoking `push_files`, the agent MUST NEVER hardcode or assume a fixed list of files to upload. Instead:
1. Run `git status --porcelain` to get the real, current list of modified/untracked files.
2. Pass that full list to `push_files`.
3. This guarantees that side-effect writes from any MCP tool (lifecycle state files, audit logs, indexing caches, etc.) are captured, regardless of which tool produced them.

## Forbidden Git Actions (Hard Constraints)
- **NO LOCAL BRANCH CREATION:** You are STRICTLY FORBIDDEN from using local bash commands like `git checkout -b <branch>` or `git branch`. You MUST exclusively use the GitHub MCP tool `create_branch`.
- **NO CLI OR CURL FOR PULL REQUESTS:** You are STRICTLY FORBIDDEN from using `gh`, `git push` shortcuts, or `curl` to create Pull Requests. You MUST exclusively use the GitHub MCP server tool `create_pull_request`.
- **No Human Intervention:** Never ask the user to manually create a Pull Request or to install tools. If an MCP tool fails, halt execution, report the specific JSON-RPC error, and wait for human instructions.

## Merge Conflict Detection (MCP-Only)
The agent must NEVER run `git merge`, `git rebase`, or `git pull` against `main` locally to sync a feature branch. All conflict detection with `main` must happen exclusively through the GitHub MCP server, by inspecting the mergeable status returned when creating (or querying) the Pull Request.
If GitHub reports the branch is not mergeable, HALT and report it to the user — conflict resolution is a human action performed on GitHub, not an autonomous local git operation.
