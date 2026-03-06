# GuardSpine Architecture One-Pager

## What Is GuardSpine?

GuardSpine is an open-core compliance infrastructure platform that replaces manual audit trails with cryptographically verifiable evidence bundles. It compresses regulatory proof artifacts 100:1 and delivers sub-second verification of compliance state across frameworks.

---

## MECE 7-Layer Architecture

```
+---------------------------------------------------------------+
|  Layer 7: PRESENTATION                                        |
|  Dashboard, CLI, API Gateway, Webhook Endpoints               |
+---------------------------------------------------------------+
|  Layer 6: GOVERNANCE (Nomotic Engine)                         |
|  Policy-as-Code, Rule Evaluation, Approval Workflows          |
+---------------------------------------------------------------+
|  Layer 5: COUNCIL (Multi-Model Deliberation)                  |
|  Byzantine Consensus, Outlier Detection, Department Routing   |
+---------------------------------------------------------------+
|  Layer 4: EVIDENCE CHAIN                                      |
|  SHA-256 Hash Chains, Cryptographic Signing, Tamper Detection  |
+---------------------------------------------------------------+
|  Layer 3: COMPRESSION ENGINE                                  |
|  100:1 Artifact Compression, Semantic Deduplication           |
+---------------------------------------------------------------+
|  Layer 2: CONNECTORS                                          |
|  DocuSign, Jira, GitHub, Slack, AWS, GCP, Azure, n8n          |
+---------------------------------------------------------------+
|  Layer 1: DATA PLANE                                          |
|  PostgreSQL, Redis, Object Storage, Event Bus                 |
+---------------------------------------------------------------+
```

Each layer is mutually exclusive and collectively exhaustive (MECE). No cross-layer leakage; all communication flows through defined interfaces.

---

## Key Metrics

| Metric                     | Value                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------ |
| Evidence compression ratio | 100:1                                                                                            |
| Verification latency       | < 1 second                                                                                       |
| Evidence chain integrity   | Cryptographic (SHA-256 hash chains)                                                              |
| Supported frameworks       | Framework-agnostic evidence model; compliance mapping in development                             |
| Connector ecosystem        | Connector framework with webhook adapter (GitHub, GitLab) shipped; additional connectors planned |
| Council consensus protocol | Soft Byzantine (3+ models)                                                                       |

---

## Competitive Positioning

| Capability                   | GuardSpine | Drata   | Vanta   | Onspring |
| ---------------------------- | ---------- | ------- | ------- | -------- |
| Open-core (self-host)        | Yes        | No      | No      | No       |
| Cryptographic evidence chain | Yes        | No      | No      | No       |
| 100:1 compression            | Yes        | No      | No      | No       |
| Multi-model AI council       | Yes        | No      | Partial | No       |
| Policy-as-code (Nomotic)     | Yes        | Partial | Partial | Yes      |
| Sub-second verification      | Yes        | Minutes | Minutes | Hours    |
| On-prem deployment           | Yes        | No      | No      | Yes      |

**Positioning**: GuardSpine sits where DevSecOps meets GRC. Drata and Vanta automate evidence collection but lack cryptographic proof and on-prem options. Onspring offers flexibility but no AI layer. GuardSpine is the only platform combining all four: open-core, cryptographic evidence, AI council, and policy-as-code.

---

## Market Sizing

| Segment                                      | Estimate       | Basis                                                             |
| -------------------------------------------- | -------------- | ----------------------------------------------------------------- |
| **TAM** (Global GRC Software)                | $15.5B by 2028 | Grand View Research CAGR 13.8%                                    |
| **SAM** (Cloud-native compliance automation) | $3.2B          | Mid-market + enterprise, SOC 2/ISO focus                          |
| **SOM** (Year 3 target)                      | $29.4M ARR     | 1,350 paid accounts (see COUNCIL-PREMIUM-MATRIX.md for breakdown) |

Primary beachhead: Series A-C startups needing SOC 2 Type II who want self-hostable, developer-friendly tooling.

---

## Team Background

- **Founder**: David Youssef -- AI infrastructure engineer. Built Context Cascade (713-component cognitive architecture), Memory MCP (triple-layer persistence), Connascence Analyzer (7-analyzer quality suite with 98.5% accuracy). Deep expertise in multi-model orchestration, epistemic systems, and production deployment.
- **Architecture lineage**: GuardSpine inherits production-tested components from the AI Exoskeleton ecosystem (260 agents, 196 skills, 4-loop self-improvement).

---

## Call to Action

GuardSpine transforms compliance from a periodic checkbox exercise into a continuous, cryptographically verifiable state. The 100:1 compression engine and sub-second verification create a step-function improvement over incumbents.
