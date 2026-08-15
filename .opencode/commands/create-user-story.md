# SOP: create-user-story

**Planning mode.** From the requirement provided in `$ARGUMENTS`, execute the following actions STRICTLY in order:

1. **CREATION:** Invoke the `project_memory_create_story` tool, passing an incremental `story_id` (e.g., US-001, US-002), title, and description in As a / I want / So that format.
2. **STOP:** You are STRICTLY PROHIBITED from asking the user questions, guessing intentions, automatically advancing phases, or executing additional tools.
3. **CLOSURE AND DYNAMIC GUIDE:** Inform the user that the story was successfully registered in 'Draft' status and close your response by emitting EXACTLY this block without modifications (replacing `US-XXX` with the actual newly generated ID): "The story US-XXX has been created in Draft status. To authorize the planning phase, you MUST execute the following command in your terminal: plan-user-story US-XXX"
