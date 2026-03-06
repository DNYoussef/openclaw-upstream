# Kill List Deep Dive -- Deferred Capabilities Explained

## March 5, 2026

Parent doc: `AI-NATIVE-TASK-BREAKDOWN.md` (v5, kill list section)

---

## PURPOSE OF THIS DOCUMENT

The v5 operating plan cut 20+ capabilities down to 3 business loops. This document explains each cut item in full: what it is, how it would work, why it was cut, and exactly when it comes back. This is the reference for the day someone says "should we build X?" -- look it up here first.

---

## 1. Memory-MCP on Railway

**What it is:**
A triple-layer retrieval-augmented memory system deployed as a Railway service. Currently exists as a working project at `D:\Projects\memory-mcp-triple-system` with 641 passing tests. Architecture: Vector RAG via ChromaDB (40% weight), HippoRAG via NetworkX knowledge graph (40%), and Bayesian inference via pgmpy (20%). Memory decays exponentially (`e^(-days/30)`) across three temporal tiers: short-term (24h), mid-term (7d), and long-term (30d+).

**How it would work when triggered:**

1. Deploy the existing `Dockerfile.railway` (Python 3.11-slim, spacy, torch) to Railway as a fourth service.
2. Configure it with a persistent volume for ChromaDB and SQLite storage.
3. Wire it into the Lead Loop: before OpenClaw drafts a follow-up, it queries Memory-MCP for prior interactions with that prospect.
4. Memory-MCP returns: last contact date, what was discussed, what the prospect responded, any commitments made.
5. The content drafter skill uses this context to avoid repeating itself and to reference prior conversations naturally.
6. After each outreach cycle, n8n stores the interaction back into Memory-MCP (who was contacted, what was said, what happened).

**Why it was cut:**
The image is large (~1.5GB with torch + spacy), the surface area is wide (3 retrieval backends, HTTP API, auth), and the immediate payoff is weak. At 5-10 prospects per night, David can remember who he contacted last week. Memory becomes valuable at scale -- when there are 50+ active prospects and 200+ historical interactions where human memory fails.

**Trigger to revisit:**

- David says "I already contacted them" 3+ times (pattern of duplicate outreach)
- OR: A/B test shows memory-augmented drafts measurably outperform non-memory drafts (higher response rate, better personalization scores)

**Estimated effort when triggered:** 4-6 hours (deploy existing code, wire into Lead Loop, test with real data).

---

## 2. Beads Integration

**What it is:**
Beads is a dependency-tracking and task-decomposition system that lives at `~/.beads/`. It models work as "beads" (atomic units of work) connected by dependency edges, forming a directed acyclic graph. Each bead has: an ID, description, status (pending/active/blocked/done), dependencies (other bead IDs), outputs, and metadata. The system can answer questions like "what is blocked and by what?" and "if I finish this bead, what unblocks?"

**How it would work when triggered:**

1. Each loop and sub-task gets modeled as a bead in the graph.
2. When the Ops Loop compiles the morning brief, it queries the beads graph: "What beads changed status overnight? What is now unblocked? What is still blocked and by whom?"
3. The morning brief includes a dependency-aware view: "Completing the Logan MOU countersign unblocks 3 downstream tasks: pilot onboarding, evidence schema design, and the first proof case."
4. Cross-function dependencies become visible: "The lead drafter skill needs the prospect research output from the browsing skill, which is blocked by SEC-3 (prompt injection defense)."

**Why it was cut:**
For a 2-person team running 3 loops, dependencies fit in a shared Slack channel and a morning conversation. Beads adds value when there are 10+ concurrent workstreams with non-obvious cross-dependencies -- when forgetting a dependency actually causes work to be wasted. Right now, David and Igor can hold the full dependency graph in their heads.

**Trigger to revisit:**

- Cross-function dependency tracking is a real daily problem (not theoretical). Specifically: work gets wasted because someone did not know it depended on something else, and this happens repeatedly.

**Estimated effort when triggered:** 2-3 hours (beads CLI already exists, wire into morning brief query).

---

## 3. Department Functions (Revenue, Product, Finance, CS)

**What it is:**
Organizational abstractions that map traditional company departments to agent-assisted workflows. Each "department" would have:

- **Revenue:** Pipeline tracking, lead scoring, win/loss analysis, forecast modeling. Agent assists with CRM updates, pipeline reports, competitive intel.
- **Product:** Feature prioritization, roadmap tracking, pilot feedback synthesis, bug triage. Agent assists with user story generation, sprint planning summaries.
- **Finance:** Burn rate tracking, runway calculations, invoice management, expense categorization. Agent assists with financial reports, scenario modeling.
- **CS (Customer Success):** Pilot health monitoring, usage analytics, renewal tracking, support ticket routing. Agent assists with health scores, churn risk alerts.

**How it would work when triggered:**

1. Each department gets its own n8n pipeline with department-specific quality gates.
2. Revenue pipeline: prospect data in -> scoring model -> pipeline stage update -> forecast recalculation -> weekly revenue report to Slack.
3. Product pipeline: pilot feedback in -> categorization -> priority scoring -> roadmap update suggestion -> sprint planning brief.
4. Finance pipeline: transaction data in -> categorization -> burn rate update -> runway recalculation -> monthly financial summary.
5. CS pipeline: usage telemetry in -> health score calculation -> churn risk flag -> renewal reminder -> escalation if health drops.
6. Each department has its own Slack channel (#revenue, #product, #finance, #cs) and its own evidence trail.

**Why it was cut:**
This is org-chart cosplay for 2 people. David does all four "departments" in his head. Creating formal department abstractions before there are department owners creates busywork: maintaining 4 pipelines, reading 4 channels, managing 4 evidence trails -- all for work that currently takes one Slack message. Departments make sense when there are people to own them.

**Trigger to revisit:**

- Team grows to 5+ people with actual department owners who need their own operational cadence.

**Estimated effort when triggered:** 2-4 hours per department (n8n pipeline + Slack channel + evidence schema + quality gates).

---

## 4. Executive Synthesis

**What it is:**
A meta-loop that sits above department functions. It aggregates outputs from all departments into a unified executive view: "Here is the state of the company across all functions." Think of it as a weekly board packet assembled by machine: revenue trends, product velocity, financial health, customer satisfaction -- all in one summary with cross-cutting insights ("Revenue is up but CS health scores are dropping, suggesting we are selling faster than we can support").

**How it would work when triggered:**

1. Each department pipeline produces a structured weekly summary (JSON).
2. A synthesis cron (weekly, Sunday evening) collects all department summaries.
3. An LLM synthesizes cross-cutting insights: correlations, tensions, risks, opportunities.
4. Quality gates check for: internal consistency (do the numbers add up?), completeness (did every department report?), staleness (is any data >7 days old?).
5. Output: a formatted executive brief posted to Slack #exec or emailed to founders.

**Why it was cut:**
There are no departments to synthesize across. This is second-order machinery built on top of first-order machinery that does not exist yet. Executive synthesis without departments is just... reading your own Slack channels.

**Trigger to revisit:**

- Department functions exist and are producing structured output. This literally cannot work until item #3 (departments) is built.

**Estimated effort when triggered:** 3-4 hours (aggregation pipeline + synthesis prompt + quality gates).

---

## 5. Board Meeting Protocol

**What it is:**
A structured decision-making process for when multiple AI agents produce conflicting recommendations. Inspired by corporate board governance: when Agent A says "contact this prospect now" and Agent B says "wait, they just got bad press -- hold off," someone needs to adjudicate. The Board Meeting Protocol would:

- Collect all agent recommendations on a given topic.
- Identify conflicts (mutually exclusive recommendations).
- Present each agent's reasoning and evidence.
- Apply a decision framework (majority vote, weighted by agent confidence, or escalate to human).
- Log the decision and rationale for audit trail.

**How it would work when triggered:**

1. When n8n detects conflicting signals (e.g., Lead Loop says "send" but a risk check says "hold"), it triggers a Board Meeting flow.
2. Each conflicting agent's output is formatted as a "position paper": recommendation, evidence, confidence score, risk assessment.
3. A synthesis LLM evaluates all positions against a decision rubric (e.g., "when in doubt, do not contact real humans").
4. The decision is logged with full provenance: who recommended what, what evidence supported each position, what the final decision was and why.
5. If no consensus is reached above a confidence threshold, the decision escalates to David via Slack with a structured summary.

**Why it was cut:**
There are not 3+ agents making conflicting recommendations. There is one content drafter and one pipeline. Conflicts do not arise because there is only one voice. This solves a coordination problem that does not exist yet.

**Trigger to revisit:**

- 3+ agents are actually producing conflicting recommendations on the same topic, and manual resolution is taking meaningful time.

**Estimated effort when triggered:** 4-6 hours (conflict detection logic + synthesis prompt + decision logging + escalation flow).

---

## 6. Critic Function

**What it is:**
A dedicated adversarial agent that reviews every output before it reaches a human or the outside world. The Critic does not create -- it only evaluates. For every draft, evidence bundle, or recommendation, the Critic asks: "What is wrong with this? What is missing? What could go wrong if we act on this?" It catches:

- Factual errors (wrong company name, outdated info)
- Tone violations (too aggressive, too casual, inappropriate for the recipient)
- Logic gaps (recommendation does not follow from evidence)
- Risk blind spots (sending to a competitor's employee, referencing sensitive topics)

**How it would work when triggered:**

1. Insert a Critic node into every n8n pipeline, between the LLM output and the human review queue.
2. The Critic receives the draft + context and runs an adversarial evaluation prompt.
3. Output: a list of issues found (with severity: blocker/warning/note) and a pass/fail verdict.
4. Blockers prevent the item from reaching the human review queue -- they go back to the drafter for revision.
5. Warnings are surfaced alongside the draft so David can factor them into his review.
6. All Critic evaluations are logged for later analysis of false positive rates.

**Why it was cut:**
This is second-order quality control before first-order quality control (the quality gates in n8n) is proven. The existing gates -- word count, banned terms, swap test -- catch the mechanical errors. The Critic catches semantic errors, but those are exactly what David's morning review catches. Adding a Critic before knowing the escaped-error rate is premature optimization.

**Trigger to revisit:**

- Escaped-error count rises above 0. Specifically: a message with wrong information gets sent to a real person, a follow-up gets missed, or a commitment gets broken.

**Estimated effort when triggered:** 2-3 hours (adversarial prompt + n8n node + logging).

---

## 7. Tool Registry

**What it is:**
A centralized catalog of all tools, skills, and capabilities available to the AI agents. Each entry includes: tool name, description, input/output schema, permission level required, cost per invocation, last used date, and an approval status. The registry answers: "What can our agents do? What are they allowed to do? What does each capability cost?"

**How it would work when triggered:**

1. Create `TOOL-REGISTRY.md` (or a YAML/JSON file) listing every skill, n8n flow, and external API integration.
2. Each entry has: name, description, inputs, outputs, risk level (low/medium/high), approval status (approved/experimental/deprecated), cost (tokens/API calls per invocation).
3. Before deploying a new skill or flow, it must be added to the registry with an explicit approval.
4. The Ops Loop morning brief includes: "Tools used overnight: content_drafter (5 invocations, $0.12), prospect_research (10 invocations, $0.45)."
5. Monthly review: which tools are unused? Which cost more than expected? Which should be deprecated?

**Why it was cut:**
With <10 tools, you can list them in your head. A registry is overhead that pays off at scale. Right now the "registry" is: content drafter skill, n8n lead pipeline, n8n pilot pipeline, n8n morning brief. Four things. You do not need a catalog for four things.

**Trigger to revisit:**

- More than 20 tools/skills in production and losing track of what exists, what is approved, and what costs what.

**Estimated effort when triggered:** 1-2 hours (create registry file + add entries + integrate into morning brief).

---

## 8. Scoped Context Rules

**What it is:**
Access control for what information each agent can see. Right now, every agent sees everything -- the full prospect database, all Slack history, all evidence bundles. Scoped Context Rules would limit each agent's view to only what it needs:

- Content drafter sees: prospect data, prior interactions, company research. Does NOT see: financial data, internal strategy docs, other prospects' data.
- Pilot monitor sees: PR data, codeguard results, pilot repo metadata. Does NOT see: prospect data, outreach history.
- Morning brief sees: Slack summaries, calendar, blocked items. Does NOT see: raw prospect data, financial details.

**How it would work when triggered:**

1. Define context scopes as named permission sets (e.g., `scope:lead_ops`, `scope:pilot_ops`, `scope:daily_ops`).
2. Each OpenClaw skill declares which scope it needs.
3. The OpenClaw -> n8n integration enforces scope: when a skill requests data outside its scope, the request is denied and logged.
4. Scoped contexts reduce prompt injection risk (a compromised skill cannot access data it should not see) and reduce token costs (smaller context = fewer tokens).
5. Scope violations appear in Slack #alerts.

**Why it was cut:**
With one skill (content drafter) and three pipelines, there is nothing to scope. Context rules matter when agents see irrelevant information that causes confusion, hallucination, or security risk. That requires multiple agents with distinct purposes operating on distinct data sets.

**Trigger to revisit:**

- Agents are demonstrably seeing irrelevant context that causes bad outputs (e.g., the lead drafter references pilot data in a prospect email).

**Estimated effort when triggered:** 3-5 hours (scope definitions + enforcement in OpenClaw skill runner + logging).

---

## 9. Cross-Agent Invocation

**What it is:**
The ability for one agent to call another agent as a subroutine. Example: the content drafter needs prospect research, so it invokes the research agent, waits for results, and uses them in the draft. Without cross-agent invocation, each agent is standalone -- it gets input, produces output, and has no way to request work from another agent mid-execution.

**How it would work when triggered:**

1. Define an invocation protocol: Agent A sends a structured request (target agent, input payload, timeout, callback URL) to a central dispatcher.
2. The dispatcher (likely an n8n flow) routes the request to the target agent, monitors execution, and returns the result to Agent A.
3. Invocations are logged: who called whom, with what input, what was returned, how long it took.
4. Recursion limits prevent infinite loops (Agent A calls Agent B calls Agent A).
5. Cost accounting: the invoking agent's budget is charged for the invoked agent's token usage.

**Why it was cut:**
Agents do not need to call each other yet. The architecture is sequential: OpenClaw runs a skill -> posts to n8n -> n8n runs gates -> posts to Slack. There is no mid-execution "I need help from another agent" scenario. Cross-agent invocation is valuable when skills become composable building blocks rather than standalone pipelines.

**Trigger to revisit:**

- A concrete case where one agent needs to invoke another mid-execution, and the workaround (running them sequentially via n8n) is too slow or too complex.

**Estimated effort when triggered:** 6-10 hours (dispatcher flow + invocation protocol + recursion protection + cost accounting + logging).

---

## 10. Meta-Governance

**What it is:**
Governance of the governance system itself. When the quality gates, approval flows, and evidence trails become complex enough, they themselves need oversight: Are the gates too strict (blocking good work)? Too loose (letting bad work through)? Are approval queues backing up? Is the evidence trail complete? Meta-governance monitors the governance layer and flags when it is not working.

**How it would work when triggered:**

1. A weekly meta-governance cron collects metrics on all governance components: gate pass/fail rates, approval queue depths, average time-to-approval, evidence bundle completeness, false positive rates.
2. Anomaly detection flags: gate pass rate dropped from 80% to 40% this week (gate may be miscalibrated), approval queue depth >20 items (human bottleneck), evidence bundles missing required fields.
3. Recommendations: "The banned-terms gate rejected 15 drafts this week for the word 'synergy' -- consider removing it from the banned list" or "Approval queue averaged 12 items -- consider raising the auto-approve threshold for low-risk items."
4. Meta-governance output goes to Slack #ops as a weekly digest.

**Why it was cut:**
There is no governance to govern yet. The quality gates do not exist until the Lead Loop is built (Day 3-4). Meta-governance before governance is like building a fire department before building any houses.

**Trigger to revisit:**

- Governance volume makes manual review of governance effectiveness impossible. Specifically: there are enough gates, flows, and evidence trails that you cannot tell by inspection whether they are working.

**Estimated effort when triggered:** 4-6 hours (metrics collection + anomaly thresholds + recommendation prompts + weekly digest flow).

---

## 11. Ideal State Document

**What it is:**
A formal specification of "what good looks like" for the entire system. For each loop, metric, and component, the Ideal State Document defines: target value, acceptable range, degradation threshold, and failure threshold. Example: "Lead Loop draft quality: target 85% approval rate, acceptable 70-95%, degraded below 60%, failed below 40%." This becomes the foundation for automated monitoring, alerting, and self-healing.

**How it would work when triggered:**

1. Create `IDEAL-STATE.yaml` with sections for each loop, metric, and infrastructure component.
2. Each entry: `metric`, `target`, `acceptable_range`, `degraded_threshold`, `failed_threshold`, `measurement_method`, `remediation_action`.
3. Automated checks compare actual values against ideal state at regular intervals.
4. Deviations generate alerts: "Lead Loop approval rate at 55% (degraded, target 85%). Possible causes: prompt drift, prospect quality change, gate miscalibration."
5. The Ideal State Document evolves: after 2 weeks of data, initial targets are calibrated against reality.

**Why it was cut:**
You need telemetry before you can define "good." The loops have not run once. There is no data on approval rates, response latencies, or evidence quality. Writing an Ideal State Document now would be fiction -- invented targets with no empirical basis. Wait for 2+ weeks of operational data, then define targets based on observed baselines.

**Trigger to revisit:**

- Enough telemetry (2+ weeks of 3 loops running) to define empirically-grounded targets.

**Estimated effort when triggered:** 3-4 hours (analyze 2 weeks of data + define targets + create YAML + wire into monitoring).

---

## 12. Skill Factory + Quarantine

**What it is:**
Two related concepts:

**Skill Factory:** A structured process for creating, testing, and deploying new OpenClaw skills. Includes: skill template generator, automated testing harness, documentation generator, and a review/approval workflow. Instead of ad-hoc skill creation, every new skill goes through: design -> implement -> test (unit + integration) -> review -> stage -> deploy.

**Quarantine:** An isolation environment for new or untrusted skills. Before a skill is approved for production, it runs in quarantine: limited permissions, no access to real data, monitored execution, and automatic rollback if it behaves unexpectedly. Think of it as a sandbox with exit criteria.

**How it would work when triggered:**

1. **Skill Factory pipeline:**
   - Developer describes intended skill behavior.
   - Factory generates skill scaffold (OpenClaw skill format + test harness).
   - Developer implements the skill logic.
   - Automated tests run: does it produce valid output? Does it stay within its declared scope? Does it handle edge cases?
   - Code review (human or codeguard).
   - If approved: promote to staging. If not: back to development.

2. **Quarantine environment:**
   - New skills deploy to a quarantine namespace (separate n8n flow, separate Slack channel #quarantine).
   - Quarantined skills run against synthetic data, not real prospects.
   - Execution is monitored: token usage, output quality scores, error rates, scope violations.
   - After N successful runs (configurable, default 10) with zero critical issues, the skill is eligible for production promotion.
   - Promotion requires explicit human approval.

**Why it was cut:**
Building a skill factory before you have 3 working skills is infrastructure for infrastructure's sake. The content drafter is the only skill. There is nothing to quarantine and nothing to mass-produce. The factory and quarantine add value when you are creating skills frequently (monthly+) or accepting community-contributed skills that need vetting.

**Trigger to revisit:**

- More than 10 custom skills in production AND community skill installs are needed (accepting skills from outside the core team).

**Estimated effort when triggered:** 8-12 hours (skill template + test harness + quarantine namespace + monitoring + promotion flow).

---

## 13. DSPy Self-Improvement

**What it is:**
DSPy is a framework for programmatically optimizing LLM prompts. Instead of manually tweaking prompts ("add more context here," "make the tone warmer"), DSPy treats prompt optimization as a machine learning problem: define an objective function (e.g., draft approval rate), collect scored examples (approved drafts = positive, rejected drafts = negative), and let DSPy automatically find the prompt that maximizes the objective.

**How it would work when triggered:**

1. Collect 200+ scored examples from the Lead Loop: each draft paired with its outcome (approved/rejected/edited, response rate if sent).
2. Define the optimization objective: maximize approval rate while maintaining response quality.
3. DSPy runs prompt optimization: systematic variation of prompt structure, examples, instructions, and formatting.
4. A/B test the optimized prompt against the current prompt over 2 weeks.
5. If the optimized prompt wins: promote it. If not: keep the manual prompt and collect more data.
6. Re-run optimization monthly as the data set grows.

**Why it was cut:**
You need 200+ scored examples before DSPy optimization is statistically meaningful. At 5-10 prospects per night, that is 20-40 nights of data. And manual A/B testing (trying different prompt approaches and tracking which ones get approved more) should be exhausted first -- it is simpler, requires no infrastructure, and often captures 80% of the improvement. DSPy is for squeezing out the remaining 20% after manual optimization plateaus.

**Trigger to revisit:**

- 200+ scored examples collected AND manual A/B testing has plateaued (no improvement in approval rate for 2+ weeks despite prompt changes).

**Estimated effort when triggered:** 6-10 hours (DSPy setup + data pipeline + optimization runs + A/B test framework).

---

## 14. SOC 2 Evidence Automation

**What it is:**
Automated generation of evidence artifacts that satisfy SOC 2 Type II audit requirements. SOC 2 requires demonstrating that security controls are in place and operating effectively over time. Evidence includes: access logs, change management records, incident response documentation, risk assessments, and control monitoring results.

**How it would work when triggered:**

1. Define evidence bundle schema: what fields are required for each SOC 2 control (CC6.1 logical access, CC7.2 system monitoring, CC8.1 change management, etc.).
2. Codeguard-action already generates evidence bundles per PR (risk tier, findings, remediation). Extend the schema to map each finding to a SOC 2 control.
3. n8n pipeline collects evidence from all sources: codeguard bundles, deployment logs, access logs, incident tickets.
4. Weekly evidence compilation: aggregate all evidence into a structured report per control.
5. Gap detection: "Control CC6.1 has 47 evidence artifacts this month. Control CC7.2 has 0 -- gap."
6. Evidence stored in Cloudflare R2 (immutable, timestamped, content-addressed).

**Why it was cut:**
No customer has asked for SOC 2 compliance yet. Building SOC 2 evidence automation for an audience of zero is compliance theater. When a real pilot customer or enterprise prospect says "we need SOC 2 evidence to proceed," that is when this becomes a business priority.

**Trigger to revisit:**

- A live customer or serious prospect explicitly requires SOC 2 evidence as a condition of doing business.

**Estimated effort when triggered:** 10-15 hours (evidence schema + collection pipelines + storage setup + gap detection + reporting).

---

## 15. SOC 2 Control Documentation

**What it is:**
The written policies, procedures, and control descriptions that form the "paper" side of SOC 2. Distinct from evidence automation (#14), which is the "proof" side. Control documentation includes: information security policy, access control policy, change management procedure, incident response plan, risk assessment methodology, vendor management policy, and data classification scheme.

**How it would work when triggered:**

1. Start with templates (Vanta, Drata, or open-source SOC 2 templates).
2. Customize each policy to reflect GuardSpine's actual practices (not aspirational -- what you actually do).
3. Map each policy to SOC 2 Trust Service Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy).
4. Store in a private git repo (`guardspine-compliance`) with version history as its own evidence trail.
5. Annual review cycle: revisit each policy, update for actual practice changes, log the review.

**Why it was cut:**
Same as #14. No customer requires it. Writing 15 pages of security policies for a 2-person pre-revenue startup is a displacement activity that feels productive but produces zero revenue.

**Trigger to revisit:**

- Same as #14: a real customer requires it.

**Estimated effort when triggered:** 15-25 hours (policy writing is labor-intensive even with templates, because each policy must reflect actual practice).

---

## 16. Observability Dashboards

**What it is:**
Visual dashboards showing system health, loop performance, and business metrics in real time. Think Grafana or Logfire dashboards with panels for: loop execution success/failure rates, token usage over time, gate pass/fail rates, approval queue depth, response latency trends, cost per loop run, and the 7 north star business metrics.

**How it would work when triggered:**

1. Instrument all loops with structured logging (already partially done via n8n execution logs).
2. Ship logs to Logfire (free tier) or a self-hosted observability stack.
3. Build dashboards for: loop health (did each loop run? did it succeed?), quality (gate pass rates, approval rates), cost (tokens consumed, API spend), and business metrics.
4. Alerting rules: if a loop fails 3 times consecutively, post to Slack #alerts. If cost exceeds daily budget, pause and alert.

**Why it was cut:**
Nobody looks at dashboards when there is nothing to look at. The loops have not run once. Dashboards are useful after 2+ weeks of operation when you need to spot trends, detect degradation, and optimize. Before that, reading the Slack #ops channel and checking n8n execution logs is sufficient.

**Trigger to revisit:**

- 3+ loops running for 2+ weeks, and the volume of data makes Slack + manual log checking insufficient.

**Estimated effort when triggered:** 4-8 hours (Logfire setup + dashboard creation + alerting rules).

---

## 17. Cloudflare D1 Migration

**What it is:**
Moving the outreach database from local SQLite (`~/.claude/outreach/outreach.db`, currently 358 prospects) to Cloudflare D1, a serverless SQLite-compatible database at the edge. D1 provides: automatic replication, REST API access, no server management, and scales without hitting single-file SQLite limits.

**How it would work when triggered:**

1. Export current SQLite database schema and data.
2. Create D1 database via Cloudflare dashboard or Wrangler CLI.
3. Import schema + data into D1.
4. Update the outreach pipeline scripts (`scripts/content-pipeline/`) to use the D1 REST API instead of direct SQLite file access.
5. Update the Lead Loop to query D1 for prospect data instead of the local file.
6. Keep the local SQLite as a backup/fallback during migration.

**Why it was cut:**
SQLite handles millions of rows. With 358 prospects, even at 10x growth, the local file is fine for years. D1 migration solves a scaling problem that does not exist. It also introduces a new dependency (Cloudflare account, API tokens, network latency) for zero current benefit.

**Trigger to revisit:**

- Outreach DB size exceeds practical local SQLite limits (typically >1GB or concurrent write contention from multiple services).

**Estimated effort when triggered:** 3-5 hours (export + D1 setup + schema migration + script updates + testing).

---

## 18. Cloudflare R2 Evidence Storage

**What it is:**
Moving evidence bundles (codeguard review results, proof cases, compliance artifacts) from local storage to Cloudflare R2, an S3-compatible object store. R2 provides: immutable storage (write-once, read-many), content-addressed naming (hash-based), global availability, and no egress fees. This creates a tamper-evident evidence trail -- once written, bundles cannot be modified without detection.

**How it would work when triggered:**

1. Create R2 bucket (`guardspine-evidence`).
2. Define naming convention: `{date}/{loop}/{run-id}/{artifact-type}.json`.
3. After each pipeline run, n8n uploads evidence bundles to R2 with content-hash verification.
4. Create a simple evidence index (D1 or local SQLite) mapping: customer, date range, bundle R2 keys.
5. For customer-facing proof cases: generate a signed URL to the specific evidence bundle.

**Why it was cut:**
No customer has asked for an immutable evidence trail. The evidence bundles are currently uploaded as GitHub Actions artifacts (codeguard.yml already does this). For a pre-revenue startup, that is sufficient. R2 becomes necessary when a customer requires tamper-evident storage as part of a compliance or procurement requirement.

**Trigger to revisit:**

- A customer explicitly requires an immutable evidence trail, or evidence bundles need to persist beyond GitHub's 90-day artifact retention.

**Estimated effort when triggered:** 3-4 hours (R2 bucket + upload integration in n8n + evidence index).

---

## 19. Railway Service Hardening (SEC-9)

**What it is:**
Production-grade security hardening for all Railway services. Goes beyond the Day 1 security measures (webhook auth, credential isolation, cost ceiling) to include:

- Non-root containers (already done for OpenClaw, needs verification for n8n/LiteLLM)
- Read-only filesystem where possible
- Network policies: restrict which services can talk to which
- Secret rotation schedule (API keys, webhook secrets, gateway tokens)
- Rate limiting on all public endpoints
- Health check endpoints with uptime monitoring
- Automated vulnerability scanning of Docker images
- Log retention and audit trail
- Backup and restore procedures tested
- Incident response runbook

**How it would work when triggered:**

1. Audit each service against a hardening checklist.
2. Implement container security: non-root, read-only FS, minimal base images, no unnecessary packages.
3. Configure Railway's internal networking to enforce least-privilege communication.
4. Set up secret rotation: quarterly for API keys, monthly for webhook secrets.
5. Add rate limiting via Cloudflare or application-level middleware.
6. Document incident response: "If service X goes down, here is the runbook."
7. Test backup/restore: can you rebuild from scratch in <2 hours?

**Why it was cut:**
The Day 1 security measures (SEC-1 through SEC-7) cover the critical attack vectors: credential isolation, webhook auth, cost ceiling, code review, Cloudflare Access. SEC-9 hardening is the difference between "secure enough for internal use" and "secure enough for a paying customer's data." It belongs right before the first customer, not before the first loop run.

**Trigger to revisit:**

- Before the first paying customer. Not "when we start talking to prospects" -- when someone is about to give you money and trust you with their code.

**Estimated effort when triggered:** 8-15 hours (audit + implementation + testing + documentation).

---

## 20. Out-of-Loop Ratio Metric

**What it is:**
A metric that measures what percentage of system actions complete without human intervention. Formula: `(total actions - human interventions) / total actions`. An out-of-loop ratio of 0.8 means 80% of actions required no human involvement. Originally proposed as the primary metric for measuring AI autonomy.

**How it would work when triggered:**

1. Every action in the system is tagged: `human_involved: true/false`.
2. n8n tracks: total pipeline executions, human approvals required, human edits made, human rejections.
3. Weekly calculation: out-of-loop ratio = 1 - (human_touches / total_actions).
4. Trend tracking: is the ratio increasing over time? (More autonomous.) Decreasing? (Humans intervening more.)
5. Breakdown by loop: Lead Loop might be 0.6 (lots of editing), Pilot Loop might be 0.9 (mostly automated), Ops Loop might be 0.95 (read-only).

**Why it was cut:**
This metric rewards autonomy theater. A high out-of-loop ratio means the machine is doing a lot without humans -- but it says nothing about whether the machine's output is good, whether it is saving time, or whether it is producing business results. You could achieve a 0.99 ratio by having the machine send garbage emails that nobody reads. The 7 business metrics (response latency, time saved, pilot activation, proof-case turnaround, hours reclaimed, conversion rate, escaped errors) directly measure what matters.

**Trigger to revisit:**

- All 7 business metrics are green (targets met), and you want a secondary efficiency metric to optimize internal operations.

**Estimated effort when triggered:** 2-3 hours (action tagging + calculation + trend tracking).

---

## 21. GlobalMOO (Multi-Objective Optimization)

**What it is:**
A formal optimization framework for balancing competing objectives across the system. When you want to simultaneously maximize draft quality AND minimize token cost AND minimize response latency, these objectives conflict. GlobalMOO uses multi-objective optimization (Pareto frontier analysis) to find the best tradeoffs. Think of it as: "Given these 5 things we care about, here is the set of configurations where improving one thing necessarily worsens another."

**How it would work when triggered:**

1. Define optimization targets formally: quality (approval rate), cost (tokens/dollar), speed (latency), coverage (prospects/day), safety (escaped-error rate).
2. Parameterize the system: model choice, prompt length, gate thresholds, batch size, cron frequency.
3. Run experiments: vary parameters, measure all objectives, plot Pareto frontiers.
4. Identify the current operating point on the frontier. Is it where you want to be?
5. Make informed tradeoff decisions: "We can improve quality by 10% if we accept 15% higher cost."

**Why it was cut:**
This is optimization without targets. You need to know what the targets are before you can optimize toward them. The targets come from operational data (2+ weeks of loops running). And manual tuning ("try a different model," "adjust this prompt," "change the batch size") captures 90% of the optimization value. GlobalMOO is for squeezing out the last 10% across multiple competing objectives simultaneously.

**Trigger to revisit:**

- Optimization targets are formally defined (based on real data) AND manual tuning has plateaued.

**Estimated effort when triggered:** 10-20 hours (formalization + experiment framework + analysis tooling).

---

## 22. Comprehension Lock-In

**What it is:**
A system that ensures institutional knowledge is captured and retained even as the team changes. Every decision, rationale, and learned lesson is stored in a structured format that new team members (human or AI) can query. It prevents the "why did we do it this way?" problem that hits growing teams. Named "lock-in" because it locks comprehension into the system rather than keeping it in individual heads.

**How it would work when triggered:**

1. Every significant decision gets a Decision Record: what was decided, why, what alternatives were considered, what evidence supported the decision.
2. Decision Records are stored in a searchable format (git repo, or Memory-MCP if deployed).
3. New team members (or new AI agent instances) query the comprehension store before making decisions in the same domain.
4. The system detects when a new decision contradicts a prior decision and surfaces the conflict: "This contradicts Decision #47 from February. Here is why that decision was made."
5. Monthly review: are decision records still accurate? Have circumstances changed?

**Why it was cut:**
This requires 30+ days of operational history AND Memory-MCP proven useful. You cannot lock in comprehension that does not exist yet. And the mechanism (Memory-MCP) is itself on the kill list. This is third-order machinery: it depends on Memory-MCP (#1), which depends on the loops running (#v5 Phase 2), which depends on infrastructure (#v5 Phase 1).

**Trigger to revisit:**

- 30+ days of operational history AND Memory-MCP is deployed and proven useful.

**Estimated effort when triggered:** 6-10 hours (decision record schema + storage integration + conflict detection + query interface).

---

## 23. Silent Drift Detection

**What it is:**
Automated detection of when system behavior changes without an explicit code change. "Silent drift" happens when: an external API changes its response format, a model update changes output characteristics, data quality degrades over time, or a configuration change has unintended downstream effects. The system output looks different, but nobody changed anything -- hence "silent."

**How it would work when triggered:**

1. Pin evidence bundle versions: each bundle has a schema version, and the system validates against the pinned schema.
2. Baseline output characteristics: average draft length, vocabulary distribution, gate pass rates, token usage per run.
3. Statistical monitoring: detect when output characteristics drift beyond normal variance (>2 standard deviations from baseline over a rolling window).
4. Alert on drift: "Content drafter average output length increased 40% this week with no code changes. Possible cause: model update, prompt caching behavior change, or input data quality shift."
5. Remediation suggestions: "Rerun baseline with current model. If output has genuinely changed, update gates and thresholds."

**Why it was cut:**
You need pinned baselines before you can detect drift from them. Baselines require 2+ weeks of stable operation. And the most impactful drifts (wrong information sent to real people) are caught by the quality gates and human review. Silent drift detection is for catching subtle degradation that human reviewers might not notice over time.

**Trigger to revisit:**

- Evidence bundle versions are pinned AND 2+ weeks of stable baselines exist.

**Estimated effort when triggered:** 6-10 hours (baselining + statistical monitoring + alerting + remediation suggestions).

---

## PRIORITY ORDER WHEN TRIGGERS FIRE

If multiple triggers fire simultaneously, build in this order:

1. **Critic function** (#6) -- if escaped errors happen, stop the bleeding first
2. **Railway service hardening** (#19) -- if a customer is imminent, secure before onboarding
3. **SOC 2 evidence automation** (#14) + **documentation** (#15) -- if a customer requires compliance
4. **Memory-MCP** (#1) -- if duplicate contacts are a real problem
5. **Observability dashboards** (#16) -- if manual monitoring is insufficient
6. **Ideal State Document** (#11) -- once you have enough data to define targets
7. **Everything else** -- in order of business impact at the time

---

_v1 -- March 5, 2026. Reference document for the v5 operating plan kill list. Each item includes: what, how, why cut, trigger, and effort estimate. Update this document when triggers fire and items are built._
