## Access Receipt Logging Specification v1.0

### Purpose

Every RLM (Recursive Language Model) environment tool call must emit an access receipt. These receipts form the proof trail in Evidence Bundles -- the audit moat. Without receipts, AI inspection is opaque. With receipts, every conclusion is traceable.

### Three Receipt Types

#### 1. Access Receipt

Emitted when the RLM reads/queries any artifact.

```json
{
  "receipt_type": "access",
  "receipt_id": "uuid",
  "timestamp": "ISO8601",
  "artifact_id": "string (file path or resource ID)",
  "snippet_hash": "sha256:hex (hash of content accessed)",
  "range": {
    "start_line": "int | null",
    "end_line": "int | null",
    "start_offset": "int | null",
    "end_offset": "int | null"
  },
  "tool_name": "string (grep | read_file | ast_query | callers | callees)",
  "query": "string (the query/pattern used)",
  "purpose_tag": "string (claim_verification | impact_analysis | test_discovery | dependency_trace)",
  "parent_receipt_id": "uuid | null (if this access was triggered by another)"
}
```

#### 2. Rule Receipt

Emitted when a policy rule is evaluated against evidence.

```json
{
  "receipt_type": "rule",
  "receipt_id": "uuid",
  "timestamp": "ISO8601",
  "rule_id": "string (e.g. NOM-CORE-002)",
  "rule_version": "string",
  "severity": "critical | high | medium | low | info",
  "triggered": "boolean",
  "triggered_on_hashes": ["sha256:hex (hashes of evidence that triggered)"],
  "result": "pass | fail | warning | skip",
  "details": "string"
}
```

#### 3. Decision Receipt

Emitted when a proposed action is generated.

```json
{
  "receipt_type": "decision",
  "receipt_id": "uuid",
  "timestamp": "ISO8601",
  "proposed_action": "doc_update | spec_violation | test_required | no_action",
  "proposed_action_hash": "sha256:hex (hash of proposed change)",
  "diff_hash": "sha256:hex | null (hash of diff if applicable)",
  "risk_tier": "L0 | L1 | L2 | L3 | L4",
  "supporting_receipts": ["uuid (access and rule receipt IDs that support this)"],
  "approver": "string | null (required approver if L2+)",
  "outcome": "pending | approved | rejected | auto_applied"
}
```

### Receipt Chain

Receipts reference each other via parent_receipt_id and supporting_receipts. This creates a DAG (directed acyclic graph) from initial file access through rule evaluation to final decision.

### Integration with Evidence Bundles

Access receipts become evidence items (evidence_type: "access_receipt") in the Evidence Bundle. The inspection_trace_digest in a Doc Evidence Pack is the SHA-256 of all receipt IDs concatenated in order.

### Budget Tracking

Each access receipt increments counters: files_accessed, steps_taken, tokens_consumed. When budget caps are reached, no more access receipts can be emitted and the inspection must conclude.

### Storage

Receipts are stored in a local SQLite database during inspection runs, then serialized into the Evidence Pack.
