# Council Premium Feature Matrix

## OSS Local Council vs Premium Cloud Council

| Feature                        | OSS (Local Council)                | Premium (Cloud Council)                                         |
| ------------------------------ | ---------------------------------- | --------------------------------------------------------------- |
| **Model Support**              | Single model (Ollama local)        | Multi-provider (Claude, Gemini, GPT, Mistral)                   |
| **Consensus Protocol**         | Simple majority vote               | Soft Byzantine Consensus with quorum                            |
| **Outlier Detection**          | None                               | Statistical outlier flagging + reasoning audit                  |
| **Department Routing**         | None (all queries to single model) | Domain-aware routing (Legal, Security, Finance, HR)             |
| **SLA Guarantee**              | None (best-effort local)           | 99.9% uptime, < 2s response P95                                 |
| **Concurrent Deliberations**   | 1 (sequential)                     | 50+ parallel sessions                                           |
| **Model Fallback**             | None (single model)                | Auto-failover across providers                                  |
| **Deliberation Logs**          | Local file (JSON)                  | Cloud-stored, searchable, auditable                             |
| **Confidence Scoring**         | Binary (agree/disagree)            | Continuous 0.0-1.0 with calibration                             |
| **Provider Outage Resilience** | No (single point of failure)       | Yes (3+ providers, quorum-based)                                |
| **Custom Model Fine-tuning**   | No                                 | Enterprise tier: domain-specific fine-tuning                    |
| **Bias Cancellation**          | No (single model bias)             | Cross-family bias mitigation                                    |
| **Evidence Integration**       | Basic (text output)                | Full evidence bundle generation with SHA-256 hash chain signing |
| **API Rate Limits**            | N/A (local)                        | Team: 1K/day, Business: 10K/day, Enterprise: Unlimited          |
| **Support**                    | Community (GitHub issues)          | Team: Email, Business: Slack, Enterprise: Dedicated CSM         |

---

## Pricing Tiers

### Free (OSS)

- **Price**: $0/month
- **Target**: Individual developers, small teams evaluating
- **Includes**:
  - Local council (Ollama, single model)
  - 5 basic connectors (GitHub, Jira, Slack, AWS, GCP)
  - Local evidence chain (no cloud sync)
  - Community support
  - Nomotic engine (basic policies)

### Team

- **Price**: $499/month (up to 10 users)
- **Target**: Startups preparing for SOC 2 Type II
- **Includes everything in Free, plus**:
  - Cloud council (2 models: Claude + GPT)
  - Simple majority consensus
  - 1,000 council deliberations/day
  - Cloud dashboard
  - 10 connectors
  - Email support (48h SLA)
  - Evidence compression (10:1)

### Business

- **Price**: $1,999/month (up to 50 users)
- **Target**: Mid-market companies with multiple frameworks
- **Includes everything in Team, plus**:
  - Full multi-model council (3+ providers)
  - Soft Byzantine Consensus
  - Outlier detection
  - Department routing (4 departments)
  - 10,000 council deliberations/day
  - 20+ connectors (including DocuSign)
  - Slack support (24h SLA)
  - Evidence compression (100:1)
  - Custom policy templates
  - SSO (SAML/OIDC)

### Enterprise

- **Price**: Custom (contact sales)
- **Target**: Large organizations, regulated industries
- **Includes everything in Business, plus**:
  - Unlimited council deliberations
  - Custom model fine-tuning
  - Unlimited connectors + custom connector SDK
  - Dedicated CSM + Slack channel
  - On-prem deployment option (hybrid cloud)
  - Custom SLA (up to 99.99%)
  - Advanced audit reporting
  - Multi-tenant support
  - SOC 2 Type II report for GuardSpine itself

---

## Feature Unlock Path

```
Free (OSS)          Team ($499/mo)       Business ($1,999/mo)     Enterprise (Custom)
+-----------+       +-----------+        +-----------+            +-----------+
| 1 model   |  -->  | 2 models  |  -->   | 3+ models |   -->     | Custom    |
| Local     |       | Cloud     |        | Byzantine |           | Fine-tuned|
| No SLA    |       | Email 48h |        | Slack 24h |           | Dedicated |
| 5 conn.   |       | 10 conn.  |        | 20+ conn. |           | Unlimited |
| No compr. |       | 10:1      |        | 100:1     |           | 100:1+    |
+-----------+       +-----------+        +-----------+            +-----------+
```

---

## Revenue Model

| Tier             | ACV       | Target Accounts (Year 3) | Revenue        |
| ---------------- | --------- | ------------------------ | -------------- |
| Free             | $0        | 5,000+ (funnel)          | $0             |
| Team             | $5,988    | 800                      | $4.8M          |
| Business         | $23,988   | 400                      | $9.6M          |
| Enterprise       | ~$100,000 | 150                      | $15.0M         |
| **Total Year 3** |           | **1,350 paid**           | **$29.4M ARR** |
