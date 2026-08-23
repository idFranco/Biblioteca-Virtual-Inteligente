# SOP: create-user-story-audit

## Purpose

Execute a complete read-only technical audit of the current project.
This command is NOT a User Story creation command.
It is a project diagnostic command.

---

## Execution Rules

Execute STRICTLY in the following order.

### 1. Initialize Context

Invoke:
`project-lifecycle_project_memory_get_context`

This is mandatory.

---

### 2. Load Auditor Role Context

The command is executed by the `auditor` agent.

The Auditor MUST read:
`.opencode/roles/auditor/ROLE.md`
before performing any audit analysis.

The Auditor MUST follow all mandatory instructions defined in that role.

---

### 3. Determine Audit Scope

If `$ARGUMENTS` is provided, treat it as additional audit scope.

Examples:
`project-audit architecture`
`project-audit security`
`project-audit backend`
`project-audit full`

If `$ARGUMENTS` is empty, perform the FULL PROJECT AUDIT.

A full audit must cover:
- Clean Architecture
- SOLID
- Layer Separation
- Dependencies
- Backend
- Frontend
- API
- Security
- Authentication
- Authorization
- Database
- Validation
- Error Handling
- Testing
- AI
- LangChain
- LangGraph
- MCP
- Observability
- Performance
- Configuration
- Documentation
- Maintainability
- Technical Debt

---

### 4. Initialize Repository Understanding

Invoke:
`codebase-memory_get_architecture`

Then use:
- `codebase-memory_search_code`
- `codebase-memory_search_graph`

to understand the repository.

Do not read source files directly before using the codebase-memory architecture/search capabilities.

---

### 5. Security Audit

Perform a dedicated security audit.

When available and applicable, use:
`security-audit-mcp_*`

The audit must verify:
- authentication
- authorization
- permissions
- claims
- input validation
- secrets handling
- sensitive data exposure
- API security
- MCP security
- prompt injection
- AI tool abuse
- output sanitization

Never expose secrets or sensitive values in the final report.

---

### 6. Role Analysis

The Auditor must analyze the repository considering the responsibilities of:
- Functional Analyst
- Architect
- Backend Developer
- Frontend Developer
- AI Engineer
- QA
- Technical Writer

The Auditor must only use the roles that are relevant to the evidence found.

---

### 7. Read-Only Enforcement

During the entire audit:

DO NOT:
- edit files
- create files
- delete files
- modify configuration
- modify project memory
- create User Stories
- modify Git
- create branches
- commit
- push
- install dependencies
- modify databases

The audit must not change the repository.

---

### 8. Evidence Requirement

Every finding must contain concrete evidence.
Do not report assumptions as facts.

If insufficient evidence exists, report:
`Insufficient evidence`
instead of inventing a finding.

---

### 9. Findings

Assign every finding:
- ID: AUD-XXX
- Severity
- Category
- Location
- Evidence
- Explanation
- Impact
- Recommendation

Severity:
- CRITICAL
- HIGH
- MEDIUM
- LOW
- INFO

---

### 10. Scoring

Score each applicable category from 0 to 100.
Do not score categories that are not applicable.
Provide a justified overall assessment.

---

### 11. Consolidation

Produce ONE consolidated report.
Do not return independent reports from each role.
The Auditor is responsible for consolidating all evidence.

---

### 12. Candidate User Stories

At the end of the report, identify the findings that should become future User Stories.

Use:
`US-AUD-001`
`US-AUD-002`
`US-AUD-003`
as recommendation identifiers only.

Do NOT invoke:
`project-lifecycle_project_memory_create_story`

The user must explicitly decide which audit recommendations become User Stories.

---

### 13. Final Response

The response MUST start with the standard role header:

```text
Role: auditor
Skills: <skills actually used>
Active Story ID: <story_id from project-lifecycle_project_memory_get_context or 'None'>
Story Status: <status from MCP context>
```

Then produce:

PROJECT AUDIT REPORT
Executive Summary
Project Overview
Architecture Assessment
Clean Architecture
SOLID
Layer Separation
Dependency Analysis
Backend
Frontend
API
Security
Authentication & Authorization
Database
Testing
AI / LangChain / LangGraph
MCP
Documentation
Maintainability
Technical Debt
Performance
Findings
Priority Matrix
Recommended Improvements
Candidate User Stories
Final Assessment

---

## Final Constraint

After completing the audit, STOP.
Do not automatically create User Stories.
Do not implement fixes.
Do not modify the repository.

The command exists exclusively to diagnose the current project and provide evidence-based recommendations.
