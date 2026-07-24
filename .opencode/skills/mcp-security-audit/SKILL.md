# Skill MCP Security Audit

## Purpose

Use this skill for implementing and integrating `Security-Audit-MCP`, the MCP server that audits chatbot input and output.

## Own MCP Server

Name:

Security-Audit-MCP

## Tools

```text
audit_user_input
audit_model_output
detect_prompt_injection
detect_sensitive_data
sanitize_text
register_audit_event
```

## Risk Levels

```text
low
medium
high
critical
```

## Categories

prompt_injection
malicious_request
sensitive_data
secret_leak
credential_request
unauthorized_data_access
system_instruction_request
xss_attempt
sql_injection_attempt

## Actions

allow
sanitize
block
review

## Rules

- audit_user_input runs before the graph processes a user message.
- audit_model_output runs before the graph returns a response.
- Tools must classify risk level and category.
- Tools must have typed inputs and structured outputs.
- Tools must not persist raw secrets, tokens, passwords or API keys.
- Tools must fail safely: if the audit tool errors, use the safer fallback.
- Unsafe input must not reach business tools.
- Unsafe output must be sanitized or replaced.
- register_audit_event must log direction, risk level, category and action, without storing raw sensitive payloads.
- This MCP complements backend security; it does not replace authentication, authorization or backend validation.

## Checklist

1. Define audit schemas.
2. Implement prompt injection detection.
3. Implement sensitive data detection.
4. Implement text sanitization.
5. Implement audit event logging.
6. Test benign inputs.
7. Test malicious inputs.
8. Test unsafe model outputs.
9. Integrate as first and last nodes of the chatbot graph.
10. Document detection categories and fallback behavior.

## Expected Audit Result

```json
{
  "allowed": true,
  "risk_level": "low",
  "categories": [],
  "action": "allow",
  "reason": "No risk detected.",
  "sanitized_text": null
}
```
