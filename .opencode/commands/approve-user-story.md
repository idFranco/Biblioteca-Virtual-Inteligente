# SOP: approve-user-story

Execute the following steps STRICTLY in order:

1. Verify that story `$ARGUMENTS` exists and is in 'Planned' status using `project_memory_get_context`. If it does not exist or is not in 'Planned', STOP and report the current status.
2. If the status is correct, MANDATORILY invoke the `project_memory_advance_status` tool to change the status to 'Approved'.
3. **MANDATORY EDIT:** Read the story `.md` file at `workflow/opencode/user-stories/$ARGUMENTS.md`. Check if the `## Implementation Approval` section already contains "Approved by user." — if it already does, skip the edit and continue to step 4. If it contains any other value, use `edit` to replace it exactly with "Approved by user." without modifying any other section of the file.
4. Confirm to the user with exactly this block: "$ARGUMENTS has been approved for implementation. To start the development phase, you MUST execute the following command: implement-user-story $ARGUMENTS"
