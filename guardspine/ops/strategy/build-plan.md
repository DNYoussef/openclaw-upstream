# GuardSpine Build Plan -- Dependency Graph + Timeline

## Date: 2026-02-12

---

## Dependency Graph

```
WEEK 0 (can start NOW -- no blockers):
  T3:  Slack QA (1-2 days)
  T4:  Teams "View in Dashboard" link (3 days)
  T12: Real PDF export / weasyprint (3-5 days)
  T21: SLA document + support portal (1 week, ops)
  T22: Certification program (2-4 weeks, content)

WEEK 1-2 (THE FOUNDATION -- everything depends on this):
  T1:  Postgres persistence layer (1.5 weeks) <<<< CRITICAL PATH
       |
       +---> T2: Org tenant isolation (2 weeks)
       |      |
       |      +---> T11: Custom rubric builder (2-3 weeks)
       |      +---> T13: Escalation policy UI (1.5 weeks)
       |      +---> T14: Risk threshold UI (1 week)
       |      +---> T16: SSO/SAML hardening (1-2 weeks)
       |      +---> T20: Compliance mapping (2 weeks)
       |
       +---> T5: Auto-escalation daemon (2 weeks)
       |      |
       |      +---> T13: Escalation policy UI (1.5 weeks)
       |
       +---> T6: Cognitive probe MVP (2-3 weeks) [also BLOCKED on Logan API]
       |
       +---> T7: Dashboard polish (2-3 weeks)
       |      |
       |      +---> T9: Guard lane dashboard pages (1 week)
       |
       +---> T8: Multi-lane guard routes (1.5 weeks)
       |      |
       |      +---> T9: Guard lane dashboard pages (1 week)
       |
       +---> T15: Bulk export UI (3-5 days) [also needs T12]
       +---> T17: Jira connector (1.5 weeks)
       |      |
       |      +---> T18: ServiceNow connector (2 weeks)
       |
       +---> T19: On-prem docker-compose (2-3 weeks)

  T4 ---> T10: Teams Adaptive Cards (1-2 weeks)
```

---

## Execution Phases

### Phase 0: Quick Wins (Week 1, parallel with T1)

No blockers. Start immediately.

| Task                          | Effort   | Owner  | Notes                                |
| ----------------------------- | -------- | ------ | ------------------------------------ |
| T3: Slack QA                  | 1-2 days | Anyone | Deploy to real workspace, smoke test |
| T4: Teams "View in Dashboard" | 3 days   | Anyone | Add OpenUri to MessageCard           |
| T12: Real PDF export          | 3-5 days | Anyone | weasyprint + Jinja2 template         |
| T21: SLA docs                 | 1 week   | David  | Non-code, can parallelize            |

### Phase 1: Foundation (Weeks 1-2)

The single most critical task. Everything blocks on this.

| Task                     | Effort  | Owner       | Notes                                                                                    |
| ------------------------ | ------- | ----------- | ---------------------------------------------------------------------------------------- |
| T1: Postgres persistence | 2 weeks | Backend dev | SQLAlchemy + alembic. Kill in-memory path entirely. Seed demo data via migration script. |

### Phase 2: TEAM Tier (Weeks 3-5)

After T1 ships, these can run in parallel with 2-3 devs.

| Task                              | Effort    | Owner       | Depends On |
| --------------------------------- | --------- | ----------- | ---------- |
| T2: Org tenant isolation          | 2 weeks   | Backend dev | T1         |
| T5: Auto-escalation daemon        | 2 weeks   | Backend dev | T1         |
| T6: Cognitive probe MVP (Phase 1) | 2 weeks   | Backend dev | T1         |
| T7: Dashboard polish              | 2-3 weeks | Igor        | T1         |

**TEAM TIER GATE**: T1 + T2 + T3 + T4 + T5 + T6(Phase1) + T7 = ship $2K/mo

### Phase 3: ORG Tier (Weeks 5-8)

After T2 ships, these unlock.

| Task                        | Effort    | Owner       | Depends On |
| --------------------------- | --------- | ----------- | ---------- |
| T8: Multi-lane guard routes | 1.5 weeks | Backend dev | T1         |
| T9: Guard lane dashboard    | 1 week    | Igor        | T7, T8     |
| T10: Teams Adaptive Cards   | 1-2 weeks | Backend dev | T4         |
| T11: Custom rubric builder  | 2-3 weeks | Full-stack  | T1, T2     |
| T13: Escalation policy UI   | 1.5 weeks | Frontend    | T2, T5     |
| T14: Risk threshold UI      | 1 week    | Frontend    | T2         |
| T15: Bulk export UI         | 3-5 days  | Frontend    | T1, T12    |

**ORG TIER GATE**: All TEAM tasks + T8-T15 = ship $5K/mo

### Phase 4: Enterprise (Weeks 8-16+)

Longer-lead items. Start selling before fully built -- R4: build what customers demand.

| Task                        | Effort    | Owner       | Depends On |
| --------------------------- | --------- | ----------- | ---------- |
| T16: SSO/SAML hardening     | 1-2 weeks | Backend dev | T1, T2     |
| T17: Jira connector         | 1.5 weeks | Backend dev | T1         |
| T18: ServiceNow connector   | 2 weeks   | Backend dev | T1, T17    |
| T19: On-prem docker-compose | 2-3 weeks | DevOps      | T1         |
| T20: Compliance mapping     | 2 weeks   | Full-stack  | T1, T2     |
| T22: Certification program  | 2-4 weeks | David       | None       |

**ENTERPRISE TIER GATE**: All ORG tasks + T16-T22 = ship $12K/mo

---

## Parallel Swim Lanes (2-dev scenario)

```
         Week 1    Week 2    Week 3    Week 4    Week 5    Week 6    Week 7    Week 8    Week 9
Dev A:   [-----T1: Postgres------][---T2: Org/RBAC---][---T5: Escalation--][--T8: Guards--]
Dev B:   [T3][T4][--T12--]        [---T7: Dashboard (Igor)------------------][--T9: UI--]
                                   [---T6: Probe MVP--]                       [--T11: Rubric--]
                                                                              [T14][T15]
Logan:                             [~~~~ API design ~~~~][--- T6 Phase 2: Proprioceptive ---]
David:   [---T21: SLA docs---]                                               [---T22: Certs---]
```

**TEAM MVP ships end of Week 6.**
**ORG MVP ships end of Week 9.**

---

## External Blockers

| Blocker                | Affects                             | Mitigation                                                      |
| ---------------------- | ----------------------------------- | --------------------------------------------------------------- |
| Logan API availability | T6 Phase 2 (proprioceptive probing) | Ship Phase 1 (plain Ollama) without Logan. Phase 2 is additive. |
| Real Slack workspace   | T3                                  | Create workspace today. Zero cost.                              |
| Okta dev tenant        | T16                                 | Free Okta developer account. Sign up today.                     |
| ServiceNow PDI         | T18                                 | Free Personal Developer Instance. Apply now (takes 1-2 days).   |
| Jira Cloud free        | T17                                 | Free Atlassian account. Instant.                                |

---

## Risk Register

| Risk                                                       | Probability | Impact                    | Mitigation                                                                                                     |
| ---------------------------------------------------------- | ----------- | ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| T1 (Postgres) takes longer than 2 weeks                    | Medium      | HIGH -- blocks everything | Timebox to 2.5 weeks. If hitting edge cases, ship with SQLite first (same SQLAlchemy code, swap engine later). |
| Logan API never materializes                               | Low         | Medium                    | Phase 1 probe (plain Ollama) is still valuable. Proprioceptive layer is the moat but not the MVP.              |
| weasyprint install issues on prod                          | Low         | Low                       | Fallback: use fpdf2 (pure Python, no system deps).                                                             |
| Teams Bot Framework registration rejected                  | Medium      | Low                       | Teams webhook MessageCard (T4) is sufficient for TEAM tier. Interactive is ORG tier.                           |
| First Enterprise customer needs connector we haven't built | High        | Medium                    | Generic ConnectorClient base class (T17) makes new connectors ~200 LOC each. 1-week turnaround.                |
