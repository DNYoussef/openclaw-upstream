# globalMOO Optimization Specification

Complete formal model for weekly planning. From the MOO+GT strategy sessions.

## Decision Vector (16 elements)

```
x = [h_s, h_m, h_p, h_f, b_a, b_c, q_o, q_e, a_l, a_m, a_h, r_t, r_a, g_1, g_2, g_3]
```

| Variable | Description                               | Bounds                    |
| -------- | ----------------------------------------- | ------------------------- |
| h_s      | Founder hours to sales                    | [0, 25]                   |
| h_m      | Founder hours to marketing/content        | [0, 15]                   |
| h_p      | Founder hours to product/GuardSpine       | [10, 25]                  |
| h_f      | Founder hours to fundraising/partnerships | [0, 15]                   |
| b_a      | Acquisition/tooling/enrichment spend      | [0, 2000]                 |
| b_c      | Content/media/contractor spend            | [0, 1000]                 |
| q_o      | Outbound volume (messages/week)           | [0, 50]                   |
| q_e      | GTM experiments launched                  | [0, 5]                    |
| a_l      | Low-risk automated actions                | [0, 200]                  |
| a_m      | Medium-risk automated actions             | [0, 50]                   |
| a_h      | High-risk automated actions               | 0 (unless human override) |
| r_t      | GuardSpine approval threshold strictness  | [1, 4]                    |
| r_a      | Proportion escalated to human review      | [0.1, 1.0]                |
| g_1      | Fintech wedge priority                    | [0, 1]                    |
| g_2      | Healthcare/regulated SaaS priority        | [0, 1]                    |
| g_3      | Generalist/non-core priority              | [0, 0.15]                 |

## Seven Objective Functions

### f_pipeline: Maximize qualified pipeline

```
f_pipeline(x) = SUM_i g_i * (alpha_i * Meetings_i(x) + beta_i * QualifiedOpps_i(x))
  where Meetings_i = c_oi * q_o + c_mi * h_m + c_si * h_s
  and QualifiedOpps_i = rho_i * Meetings_i
```

Counter-KPI: qualified_meeting_rate (prevents spam outreach)

### f_revenue: Maximize expected weighted revenue

```
f_revenue(x) = SUM_i g_i * (ACV_i * CloseProb_i(x) * QualifiedOpps_i(x)) * FitScore_i
```

Counter-KPI: churn_rate (prevents bad-fit customers)

### f_learning: Maximize useful information from experiments

```
f_learning(x) = lambda_1 * q_e * ExperimentYield(x) + lambda_2 * ForecastImprovement(x)
```

Counter-KPI: experiment_yield (prevents random testing)

### f_trust: Maximize long-term market trust

```
f_trust(x) = mu_1 * PositiveReplyQuality(x) + mu_2 * NarrativeCoherence(x) + mu_3 * ImplementationSuccess(x)
```

Counter-KPI: negative_reply_rate (prevents brand damage)

### f_risk: Minimize policy/legal/execution risk

```
f_risk(x) = nu_1 * PolicyViolations(x) + nu_2 * BrandIncidents(x) + nu_3 * AutomationErrors(x) + nu_4 * ContractRisk(x)
```

Counter-KPI: policy_violation_rate

### f_burn: Minimize founder overload

```
f_burn(x) = phi_1 * ContextSwitching(x) + phi_2 * MeetingLoad(x) + phi_3 * AfterHoursWork(x) - phi_4 * DeepWorkPreserved(x)
```

Counter-KPI: deep_work_hours (prevents consuming the founder)

### f_friction: Minimize operational drag

```
f_friction(x) = psi_1 * ManualOverrides(x) + psi_2 * ApprovalLatency(x) + psi_3 * WorkflowFailures(x)
```

Counter-KPI: manual_override_rate

## Weight Vector (initial)

```
w = [0.24, 0.24, 0.14, 0.16, 0.10, 0.07, 0.05]
    pipeline  revenue  learning  trust   risk   burn  friction
```

Frontier mode preferred over weighted sum when available.

## Constraints

### Constitutional (hard stops, never violated)

- h_s + h_m + h_p + h_f <= 50 (founder hours)
- b_a + b_c <= B_max ($2000/week)
- PolicyViolations(x) <= 0
- NegativeReplyRate(x) <= 0.05
- a_h = 0 (no high-risk autonomous actions)
- g_3 <= 0.15 (non-core segment cap)
- RunwayMonths(x) >= R_min

### Strategic

- g_1 + g_2 + g_3 = 1 (segment weights sum to 1)
- h_p >= 10 (product work never starved)
- q_o <= 50 (brand safety on outbound)

### Operational

- ManualOverrideRate(x) <= 0.25
- AutomationErrorRate(x) <= 0.05

## Three Solver Modes (run in parallel)

### Mode A: Growth Frontier

Emphasis: pipeline, revenue, learning
Trigger: runway healthy, trust stable, override rate low

### Mode B: Balanced Frontier (default)

Emphasis: pipeline, revenue, trust, risk

### Mode C: Defensive Frontier

Emphasis: trust, risk, burn, runway preservation
Trigger: override rate spikes, policy violations rise, negative sentiment rise, founder overload rise

## Four Autonomy Tiers

| Tier                 | Actions                                                                  | Governance       |
| -------------------- | ------------------------------------------------------------------------ | ---------------- |
| 0: Autonomous        | Content gen, lead scoring, internal analysis, low-risk workflow          | None             |
| 1: Conditional       | Pricing suggestions, outbound messaging, automation scaling, experiments | GuardSpine L1-L2 |
| 2: Approval Required | Pricing commitments, contracts, external claims, strategic pivots        | GuardSpine L3-L4 |
| 3: Human Required    | Irreversible decisions, legal exposure, high-risk financial actions      | Human only       |

## Four Structural Guardrail Metrics

1. Human override rate (detects optimizer failure)
2. Policy violation rate (detects safety failure)
3. Rollback frequency (detects system instability)
4. Trust score (detects hidden system drift)

## Pareto Quality Metrics

- Hypervolume: dominated volume of objective space (higher = better)
- Spread: diversity across tradeoff regions
- Generational distance: distance from estimated to true Pareto front

## 12-Role Agent Blueprint

| Role                        | Budget/mo     | Heartbeat               |
| --------------------------- | ------------- | ----------------------- |
| Chief of Staff              | $100          | 15min + daily           |
| CEO Strategy Cell           | $150          | weekly + daily          |
| CRO Revenue Commander       | $250          | hourly + daily          |
| CMO Demand Engine           | $250          | hourly + daily + weekly |
| Research & Intelligence     | $150          | hourly + daily + weekly |
| BizDev Scout                | $200          | hourly                  |
| Proposal/Solutions Engineer | $100          | daily + event           |
| COO Workflow Reliability    | $250          | 15min + hourly          |
| CFO Finance Steward         | analysis only | daily + weekly          |
| Governance/GS Marshal       | $0            | 15min + hourly          |
| Memory/Knowledge Curator    | $100          | daily + weekly          |
| Model Improvement Lab       | $250 sandbox  | daily + weekly          |
