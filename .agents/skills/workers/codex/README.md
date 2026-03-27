# Codex Specialists

Narrow worker agents from VoltAgent/awesome-codex-subagents.
Invoked on demand by CTO, Staff Engineer, or QA Engineer. Never self-dispatch.

## Dispatch Rules

| Specialist       | Trigger                                                | Who May Invoke              | Must Never Override                                                  |
| ---------------- | ------------------------------------------------------ | --------------------------- | -------------------------------------------------------------------- |
| python-pro       | Python backend task, runtime bug, packaging issue      | CTO, Staff Engineer         | Architecture decisions, API contracts                                |
| typescript-pro   | Frontend/API TypeScript work, type errors              | CTO, Staff Engineer         | Design system choices, component hierarchy                           |
| docker-expert    | Container optimization, multi-stage builds, image size | CTO, Release Engineer       | Railway deployment config, service networking                        |
| postgres-pro     | Schema design, query optimization, index tuning        | CTO, CFO (financial models) | Data ownership, retention policy, access control                     |
| security-auditor | Auth review, credential handling, OWASP check          | CTO, Chief of Staff         | GuardSpine L0-L4 risk classification (that is governance, not audit) |

## Selection Criteria (from upgrade plan)

- Matches actual repo language/runtime (Python, TypeScript, Docker, PostgreSQL)
- Fills a real gap not covered by gstack or superpowers skills
- Narrow worker role, not leadership
- Clear dispatch condition
- No role duplication with existing reviewer/release owners
