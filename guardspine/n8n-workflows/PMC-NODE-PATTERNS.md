# PMC Node Patterns: Atomic Cognitive Moves as n8n Nodes

Reference guide for decomposing any n8n workflow using the 6 atomic cognitive
moves from Psychological Motion Capture (PMC). Each move maps to a specific
node type, naming convention, and I/O contract.

Source framework: David Youssef, "Psychological Motion Capture: The Missing
Framework for AI-Ready Knowledge Work" (2025).

---

## Why This Matters

Most n8n workflows are built by function ("send email", "query database").
PMC decomposes by _cognitive intent_ -- what the expert's mind is actually
doing at each step. This produces workflows that are:

- **Auditable** by domain experts who don't read code
- **Recomposable** -- swap one Classify node for another without rewiring
- **Debuggable** -- when output is wrong, you know which _type of thinking_ failed

The 6 atomic moves cover every knowledge-work micro-decision. A workflow is
a sequence of these moves connected by decision logic.

---

## The 6 Atomic Moves

### 1. RETRIEVE

**What the expert is doing:** Pulling information from a source -- a database,
an API, a document, memory. "Find the prospect list." "Get the PR diff."

**n8n node types:**

- `HTTP Request` -- external API calls
- `Postgres` / `MySQL` -- database queries
- `Read Binary File` -- local file reads
- `RSS Feed Read` -- feed ingestion
- `GitHub` / `Slack` / `Gmail` -- platform-specific fetches

**Naming convention:**

```
Retrieve: {What} from {Where}
```

Examples:

- `Retrieve: Backlog Issues from Paperclip`
- `Retrieve: PR Diff from GitHub`
- `Retrieve: Health Metrics from Telemetry DB`

**Input:** Trigger event or upstream decision output (query parameters, filters).

**Output:** Raw data array. Each item is one record/document/entity. No
transformation -- that belongs to downstream moves.

**Contract:**

```
IN:  { trigger_context, query_params }
OUT: { raw_items: Array<Record>, source, retrieved_at, count }
```

**CMO Pipeline example:**
The node `Fetch CMO Backlog Issues` is a Retrieve. It hits the Paperclip API
with `assigneeAgentId` and `status=backlog` filters, returning raw issue
objects. No parsing, no filtering -- just fetching.

```
Node:  HTTP Request
Name:  "Retrieve: CMO Backlog from Paperclip"
URL:   /api/companies/{id}/issues?assigneeAgentId={cmo}&status=backlog
Out:   Array of issue JSON objects
```

**Design rules:**

- One Retrieve per data source. Don't merge two API calls into one node.
- Never filter or transform inside a Retrieve. That's a downstream Classify or Compare.
- If the Retrieve can fail (network, auth), add an error output branch. R8: every error path is a code path.

---

### 2. COMPARE

**What the expert is doing:** Evaluating something against a known criterion.
"Is this within the normal range?" "Has this been contacted before?"
"Does the word count exceed the limit?"

**n8n node types:**

- `IF` -- binary comparison (true/false)
- `Code` -- multi-field threshold checks
- `Compare Datasets` -- diff two data sets

**Naming convention:**

```
Compare: {Subject} against {Criterion}
```

Examples:

- `Compare: Followup Count against Max (2)`
- `Compare: Word Count against Limit (150)`
- `Compare: Response Rate against SLO (5%)`

**Input:** A single item or batch with the field(s) to evaluate, plus the
threshold/criterion (hardcoded or from config).

**Output:** The same item, enriched with a boolean or numeric comparison
result. Items that fail can be routed to a separate branch.

**Contract:**

```
IN:  { item, criterion_name, criterion_value }
OUT: { item, comparison_result: bool|number, criterion_met: bool }
```

**CMO Pipeline example:**
Inside the `Parse & Filter Prospects` Code node, there's a hidden Compare:
`if ((prospect.followup_count || 0) >= 2) continue;`. This checks whether
a prospect has already been contacted twice. In a PMC-decomposed workflow,
this would be its own IF node:

```
Node:  IF
Name:  "Compare: Followup Count against Max (2)"
Cond:  {{ $json.followup_count }} >= 2
True:  -> (skip / dead-letter)
False: -> next move
```

**Design rules:**

- One comparison per IF node. Don't chain `&&` conditions -- use sequential IF nodes so each comparison is independently visible and debuggable.
- Name the criterion explicitly. `"Compare: X against Y"` not `"Check X"`.
- When comparing against a configurable threshold, pull the value from an environment variable or a Set node at the top of the workflow. Don't bury magic numbers in expressions.

---

### 3. CLASSIFY

**What the expert is doing:** Assigning something to a category. "This is a
safety signal." "This prospect's pain is regulatory readiness." "This PR
is risk tier L3."

**n8n node types:**

- `Switch` -- route by category (discrete values)
- `Code` -- rule-based multi-signal classification
- `AI Agent` / `HTTP Request` to LLM -- when classification requires judgment

**Naming convention:**

```
Classify: {Subject} into {Category Set}
```

Examples:

- `Classify: Prospect into Pain Bucket`
- `Classify: PR into Risk Tier (L0-L4)`
- `Classify: Alert into Severity (critical/high/medium/low)`

**Input:** An item with the raw fields needed for classification (title,
signals, industry, content patterns).

**Output:** The same item with a `category` field added. The category value
comes from a closed set defined in the node's logic.

**Contract:**

```
IN:  { item_with_classification_fields }
OUT: { item, category: string, classification_confidence?: number, classification_method: "rule"|"llm" }
```

**CMO Pipeline example:**
The node `Classify Pain Bucket (Rule-Based)` is a textbook Classify. It
reads `title`, `signal_notes`, and `industry`, matches against keyword
lists (complianceSignals, governanceSignals, etc.), and assigns one of
four pain buckets: `regulatory_readiness_gap`, `evidence_chain_gap`,
`semantic_governance_gap`, `review_velocity_gap`.

It also performs a second classification: `angle` (direct, consultant,
platform, compliance) based on persona and lane.

```
Node:  Code
Name:  "Classify: Prospect into Pain Bucket"
In:    { title, signal_notes, industry, persona, lane }
Out:   { ...prospect, pain_bucket, angle }
```

In a stricter PMC decomposition, the pain bucket and the angle would be
two separate Classify nodes. One classification per node keeps each move
independently testable.

**Design rules:**

- Define the category set explicitly in the node name or a comment. No open-ended classification.
- Rule-based first (Code node with keyword matching). Only escalate to LLM classification when rules can't cover the space. R4: no premature abstraction.
- When using LLM classification, constrain the output to the valid category set (JSON schema, enum in prompt). Don't let the model invent categories.
- Log `classification_method` so you can audit how many items needed LLM vs. rules.

---

### 4. INFER

**What the expert is doing:** Drawing a conclusion from evidence. "Given the
pain bucket and the persona, the best template is X." "Given three failing
health checks, the service is degraded." "Given the signal density, this
prospect is high-priority."

**n8n node types:**

- `Code` -- deterministic inference (template selection, score computation)
- `AI Agent` / `HTTP Request` to LLM -- probabilistic inference requiring judgment
- `Merge` + `Code` -- combining multiple data streams into a conclusion

**Naming convention:**

```
Infer: {Conclusion} from {Evidence}
```

Examples:

- `Infer: Message Template from Pain Bucket + Angle`
- `Infer: Service Status from Health Check Results`
- `Infer: Investment Score from Signal + Engagement Data`

**Input:** One or more classified/compared items, possibly merged from
multiple branches.

**Output:** A conclusion object -- the inferred result plus the evidence
that supports it.

**Contract:**

```
IN:  { classified_items, comparison_results, context }
OUT: { conclusion, evidence_used: Array<string>, confidence?: number, needs_human_review: bool }
```

**CMO Pipeline example:**
The `Fill Message Template` node is an Infer. It takes the pain bucket and
angle (outputs of Classify) and infers which template to use, then fills
it with prospect data. It also runs a slop check -- a secondary Compare
embedded in the inference. Decomposed:

```
Node:  Code
Name:  "Infer: Draft Message from Pain Bucket + Angle"
In:    { pain_bucket, angle, name, company, signal_notes }
Out:   { draft, template_match: bool, word_count, slop_pass }
```

The `needs_llm` flag is itself an inference: "Given that no template matched,
infer that this prospect needs LLM-generated content." That boolean drives
the downstream IF node.

**Design rules:**

- Separate deterministic inference (template lookup, score formula) from probabilistic inference (LLM judgment). Different node types, different cost profiles, different error modes.
- Always output `evidence_used` -- the list of fields/facts that drove the conclusion. This makes the inference auditable.
- When inference fails (no template match, insufficient data), output a `needs_human_review` or `needs_llm` flag rather than guessing. R8: handle the error path.

---

### 5. FLAG

**What the expert is doing:** Marking something for attention. "This needs
specialist review." "This slop check failed." "This prospect responded --
escalate." Flags don't resolve anything; they create a signal for a
downstream human or system.

**n8n node types:**

- `IF` -- binary flag (flagged / not flagged)
- `Code` -- multi-condition flagging with severity
- `Slack` / `Email` / `HTTP Request` -- flag delivery (notification)

**Naming convention:**

```
Flag: {What} for {Reason}
```

Examples:

- `Flag: Draft for Slop Violation`
- `Flag: PR for Human Approval (L4)`
- `Flag: Prospect for Do-Not-Contact`
- `Flag: Service for Degraded Health`

**Input:** An item that has been through Compare, Classify, or Infer, with
the relevant result fields.

**Output:** The same item with a `flagged` boolean, `flag_reason`, and
`flag_severity`. Plus a side-effect: the notification or issue creation
that makes the flag visible.

**Contract:**

```
IN:  { item_with_assessment_results }
OUT: { item, flagged: bool, flag_reason: string, flag_severity: "info"|"warning"|"critical", flag_delivered_to: string }
```

**CMO Pipeline example:**
The IF node `Template Match?` is a Flag in disguise. When `needs_llm` is
true, the prospect is being flagged: "this one couldn't be handled by
templates, route it differently." In a PMC decomposition:

```
Node:  IF
Name:  "Flag: Prospect for LLM Fallback"
Cond:  {{ $json.needs_llm }} == true
True:  -> LLM generation branch (or manual review queue)
False: -> template-based draft posting
```

The `Post Draft as Comment` node also contains implicit flagging -- the
comment body includes `Slop audit: PASS/FAIL`. Decomposed, this would be
an explicit Flag node before the post:

```
Node:  IF
Name:  "Flag: Draft for Slop Violation"
Cond:  {{ $json.slop_pass }} == false
True:  -> quarantine / manual edit queue
False: -> auto-post
```

**Design rules:**

- Flags are cheap. When in doubt, flag it. A false positive flag costs a human 10 seconds to dismiss. A missed flag costs a bad outreach or a compliance gap.
- Always include `flag_reason` in the output. "Flagged" alone is useless; the reviewer needs to know why.
- Separate the flag decision (IF/Code node) from the flag delivery (Slack/Email/HTTP). The decision is domain logic; the delivery is infrastructure. Different owners, different change rates.

---

### 6. PRIORITIZE

**What the expert is doing:** Ordering things by importance. "Check dosing
before labeling." "Contact high-signal prospects first." "Fix critical
alerts before medium ones."

**n8n node types:**

- `Sort` -- single-field ordering
- `Code` -- weighted multi-factor scoring and ranking
- `Limit` -- take top N after sorting
- `Split In Batches` -- process highest-priority batch first

**Naming convention:**

```
Prioritize: {Items} by {Criteria}
```

Examples:

- `Prioritize: Prospects by Signal Strength`
- `Prioritize: Alerts by Severity + Recency`
- `Prioritize: PRs by Risk Tier`

**Input:** An array of items, each with the fields needed for scoring.

**Output:** The same array, sorted by priority score (descending). Each item
gets a `priority_rank` and `priority_score` field.

**Contract:**

```
IN:  { items: Array<Record>, scoring_weights?: Record<string, number> }
OUT: { items_sorted: Array<Record & { priority_rank: number, priority_score: number }>, total_count: number }
```

**CMO Pipeline example:**
The current CMO pipeline doesn't have an explicit Prioritize node -- it
processes all prospects in arrival order. This is a gap. A PMC-decomposed
version would add:

```
Node:  Code
Name:  "Prioritize: Prospects by Signal + Lane Score"
In:    Array of classified prospects
Logic:
  score = 0
  if signal_type == "warm_intro":  score += 50
  if signal_type == "responded":   score += 40
  if signal_type == "viewed_post": score += 20
  if lane == "investor":           score += 30
  if lane == "buyer":              score += 20
  score += investor_score * 0.5    // if available
  sort descending by score
  assign priority_rank 1..N
Out:   Sorted array with priority_rank, priority_score
```

Then a Limit node: `Take Top 10 per Batch` to avoid flooding the outreach
queue.

**Design rules:**

- Make scoring weights explicit and configurable. Put them in a Set node or environment variable at the top of the workflow, not buried in Code logic.
- Always output the score, not just the rank. Scores are debuggable ("why is this #3?"). Ranks alone are opaque.
- Prioritize early in the workflow, right after Classify. Don't waste Infer/Flag compute on low-priority items that won't be acted on. R3 of the optimization loop: eliminate work.

---

## Composition Patterns

### Linear Chain

```
Retrieve -> Compare -> Classify -> Infer -> Flag -> Prioritize
```

Simplest pattern. Each move feeds the next. Good for single-source,
single-output workflows.

**Example:** Narrowcast Scanner reads RSS (Retrieve), checks recency
(Compare), tags by topic (Classify), scores relevance (Infer), flags
high-signal items (Flag), ranks for briefing (Prioritize).

### Fan-Out / Fan-In

```
Retrieve -----> Classify (Type A) --\
           \--> Classify (Type B) ---+--> Merge --> Infer
           \--> Classify (Type C) --/
```

Multiple classification dimensions applied in parallel, then merged for
inference. Good when a single item needs multi-axis categorization.

**Example:** Prospect gets classified by pain bucket AND by channel
preference AND by company size tier, then all three feed into template
selection (Infer).

### Guard Gate

```
Retrieve -> Compare -> [PASS] -> Classify -> Infer
                    -> [FAIL] -> Flag -> (dead letter / manual queue)
```

A Compare node acts as a gate. Items that don't meet the threshold are
flagged and routed out. Items that pass continue to more expensive
downstream moves.

**Example:** CMO pipeline checks followup_count < 2 (Compare). Prospects
over the limit are flagged for suppression. Under-limit prospects continue
to pain bucket classification.

### Escalation Ladder

```
Classify -> Infer (rule-based) -> [matched]   -> Flag (optional) -> output
                               -> [no match]  -> Infer (LLM) -> Flag -> output
                               -> [LLM fail]  -> Flag for human
```

Try the cheapest inference first. Escalate to LLM only when rules fail.
Escalate to human only when LLM fails. Each tier is an explicit node.

**Example:** CMO pipeline attempts template match (rule Infer). No match
triggers `needs_llm` flag, routing to LLM branch. LLM timeout/failure
routes to human review queue.

---

## Checklist: Decomposing a New Workflow

When building any n8n workflow, walk through these questions:

1. **What data am I fetching?** Each source = one Retrieve node.
2. **What thresholds or filters apply?** Each filter = one Compare node.
3. **What categories am I assigning?** Each taxonomy = one Classify node.
4. **What conclusions am I drawing?** Each conclusion = one Infer node.
5. **What needs human/system attention?** Each alert condition = one Flag node.
6. **What order should things be processed?** Each ranking = one Prioritize node.

If a Code node is doing more than one of these, split it. One cognitive
move per node. The node count goes up, but debuggability and auditability
go up faster.

---

## Quick Reference Table

| Atomic Move | Primary Node Type | Naming Pattern                            | Key Output Field                |
| ----------- | ----------------- | ----------------------------------------- | ------------------------------- |
| Retrieve    | HTTP Request / DB | `Retrieve: {What} from {Where}`           | `raw_items[]`                   |
| Compare     | IF / Code         | `Compare: {Subject} against {Criterion}`  | `criterion_met: bool`           |
| Classify    | Switch / Code     | `Classify: {Subject} into {Category Set}` | `category: string`              |
| Infer       | Code / AI Agent   | `Infer: {Conclusion} from {Evidence}`     | `conclusion, evidence_used[]`   |
| Flag        | IF + Slack/Email  | `Flag: {What} for {Reason}`               | `flagged: bool, flag_reason`    |
| Prioritize  | Code + Sort       | `Prioritize: {Items} by {Criteria}`       | `priority_rank, priority_score` |
