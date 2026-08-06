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

- **Interactive Branch Naming:** When a new User Story is being planned, the agent is strictly forbidden from auto-generating or creating the Git branch autonomously.
- The agent MUST explicitly ask: "What name would you like to use for this branch? (Format required: type/US-XXX-description)"

## Explicit File Discovery Before Every MCP Push
Before invoking `push_files`, the agent MUST NEVER hardcode or assume a fixed list of files to upload. Instead:
1. Run `git status --porcelain` to get the real, current list of modified/untracked files.
2. Pass that full list to `push_files`.

## Forbidden Git Actions (Hard Constraints)
- **NO LOCAL BRANCH CREATION:** Use the GitHub MCP tool `create_branch` only.
- **NO CLI OR CURL FOR PULL REQUESTS:** Use the GitHub MCP server tool `create_pull_request` only.
- **No Human Intervention:** Never ask the user to manually create a Pull Request or to install tools. If an MCP tool fails, halt execution, report the specific JSON-RPC error, and wait for human instructions.

## Merge Conflict Detection (MCP-Only)
All conflict detection with `main` must happen exclusively through the GitHub MCP server by inspecting the mergeable status of the Pull Request. If GitHub reports the branch is not mergeable, HALT and report to the user.
