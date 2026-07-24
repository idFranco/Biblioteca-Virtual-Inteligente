# Role and Skill Display Rule

For every non-trivial task, the agent must start the response with this exact scannable header block to log execution context:

```text
Role: <selected role>
Skills: <selected skills>
Active Story ID: <story_id from project_memory_get_context or 'None'>
Story Status: <current status from MCP context>
```

## Available Roles

- functional-analyst
- architect
- technical-lead
- backend-developer
- frontend-developer
- ai-engineer
- qa
- technical-writer

## Available Skills

- dotnet-clean-architecture
- auth-permissions
- react-permissions
- langgraph-chatbot
- mcp-tools
- mcp-security-audit
- testing-qa
- documentation
