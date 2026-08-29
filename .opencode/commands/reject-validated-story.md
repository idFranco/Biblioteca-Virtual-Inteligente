Read the story `.md` file for $ARGUMENTS. Confirm current status is 'Validated'.
Ask the user (via normal conversation, since this is a human-initiated override, not an agent decision) for the reason for rejection.
Invoke `project_memory_advance_status` with next_status='Rejected', and append the reason to '## QA Result' as a new dated entry, prefixed "POST-VALIDATION REJECTION (human review):".
Emit: "Story $ARGUMENTS moved back to Rejected. To rework, execute: implement-user-story $ARGUMENTS"