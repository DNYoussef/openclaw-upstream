# GuardSpine event schema & Beads adapter

This document captures the GuardSpine event schema (code/PDF/XLSX) and the minimal adapter
layer for integrating with Beads without changing its core architecture (JSONL in git +
SQLite cache + CLI/`--json`).

## Design principles

- Append-only events (never mutate history; corrections are new events).
- Stable IDs for artifact/version/diff/run/approval.
- Deterministic hashing of artifacts and event payloads.
- Separation of duties: models emit review artifacts only (annotations/tags/suggestions).
- Evidence Bundles are reproducible from the event log.

---

## Core objects

### ArtifactRef

```json
{
  "artifact_id": "art_01J... (ulid)",
  "kind": "code|pdf|xlsx",
  "locator": {
    "scheme": "git|file|s3|sharepoint|gdrive|box|url",
    "ref": "..."
  },
  "title": "Optional human label",
  "owner": "optional team/user",
  "labels": ["policy", "sox", "customer-facing"]
}
```

### VersionRef

```json
{
  "version_id": "ver_01J... (ulid)",
  "artifact_id": "art_01J...",
  "content_hash": "sha256:...",
  "created_at": "2026-01-19T00:00:00Z",
  "created_by": { "actor_type": "human|service", "actor_id": "..." },
  "metadata": { "mime": "application/pdf", "size_bytes": 123456 }
}
```

### DiffRef

```json
{
  "diff_id": "dif_01J...",
  "from_version_id": "ver_...",
  "to_version_id": "ver_...",
  "diff_hash": "sha256:...",
  "summary": { "severity": "low|med|high", "changed_units": 42 }
}
```

---

## GuardEvent envelope

Every JSONL line is one `GuardEvent`.

```json
{
  "event_id": "evt_01J... (ulid)",
  "event_type": "ARTIFACT_VERSION_ADDED",
  "occurred_at": "2026-01-19T00:00:00Z",
  "actor": {
    "actor_type": "human|service|model",
    "actor_id": "user:alice|svc:pdfguard|model:claude-...",
    "display": "Alice"
  },
  "tenant": { "tenant_id": "tnt_acme", "workspace_id": "wsp_policy" },
  "bead": { "bead_id": "bead_01J..." },
  "refs": {
    "artifact_id": "art_...",
    "version_id": "ver_...",
    "diff_id": "dif_..."
  },
  "payload": {},
  "integrity": {
    "payload_canonical_sha256": "sha256:...",
    "prev_event_id": "evt_... (optional hash-chain)",
    "event_sha256": "sha256:..."
  },
  "policy": {
    "policy_pack_ids": ["pack_nomotic@1.2.0", "pack_sox@2026.01"],
    "policy_mode": "advisory|enforced",
    "risk_tier": "L0|L1|L2|L3|L4"
  },
  "links": {
    "correlation_id": "cor_01J...",
    "run_id": "run_01J...",
    "evidence_bundle_id": "evb_01J..."
  }
}
```

Notes:

- `bead_id` is the Beads work unit.
- `integrity.prev_event_id` optionally creates a simple per-bead hash chain.

---

## MVP event types

### Artifact lifecycle

- `ARTIFACT_REGISTERED`
- `ARTIFACT_VERSION_ADDED`
- `ARTIFACT_DIFF_COMPUTED`

**`ARTIFACT_VERSION_ADDED` payload**

```json
{
  "payload": {
    "version": {
      "version_id": "ver_...",
      "content_hash": "sha256:...",
      "metadata": { "mime": "application/pdf" }
    }
  }
}
```

**`ARTIFACT_DIFF_COMPUTED` payload**

```json
{
  "payload": {
    "diff": {
      "diff_id": "dif_...",
      "diff_kind": "pdf|xlsx|git",
      "metrics": { "changed_units": 42, "changed_pages": 3 }
    },
    "diff_artifacts": [
      { "kind": "text-diff", "ref": "s3://.../diff.txt", "hash": "sha256:..." },
      { "kind": "visual-diff", "ref": "s3://.../diff_pages.zip", "hash": "sha256:..." }
    ]
  }
}
```

### AI review (read-only)

- `MODEL_REVIEW_STARTED`
- `MODEL_REVIEW_COMPLETED`
- `ANNOTATION_ADDED`
- `RISK_FLAG_RAISED`

**`MODEL_REVIEW_COMPLETED` payload**

```json
{
  "payload": {
    "model": {
      "provider": "openrouter",
      "name": "anthropic/claude-...",
      "parameters": { "temperature": 0.2 }
    },
    "inputs": {
      "diff_id": "dif_...",
      "prompt_hash": "sha256:...",
      "context_pack_ids": ["pack_nomotic@1.2.0"]
    },
    "outputs": {
      "review_hash": "sha256:...",
      "summary": { "overall_risk": "med", "key_issues": 5 }
    }
  }
}
```

**`ANNOTATION_ADDED` payload**

```json
{
  "payload": {
    "anchor": {
      "kind": "pdf_bbox|pdf_textspan|xlsx_cell|xlsx_range|git_hunk",
      "ref": "page:4 bbox:[120,220,480,260]"
    },
    "annotation": {
      "severity": "low|med|high",
      "tags": ["policy-contradiction", "pii-risk"],
      "comment": "This change conflicts with the retention policy section...",
      "suggested_text": "Consider changing to: ...",
      "citations": [{ "pack_id": "pack_nomotic@1.2.0", "source_ref": "nomotic:sec3:p2" }]
    }
  }
}
```

### Human decisions & gates

- `REVIEW_ASSIGNED`
- `APPROVAL_REQUESTED`
- `APPROVAL_GRANTED`
- `APPROVAL_REJECTED`
- `RISK_TIER_SET`
- `PUBLICATION_BLOCKED` / `PUBLICATION_ALLOWED`

**`APPROVAL_GRANTED` payload**

```json
{
  "payload": {
    "decision": {
      "decision_id": "dec_01J...",
      "result": "approved",
      "rationale": "Reviewed changes; acceptable risk with mitigations.",
      "conditions": ["Add redline note to section 2.1"]
    }
  }
}
```

### Evidence bundle outputs

- `EVIDENCE_BUNDLE_GENERATED`
- `EVIDENCE_BUNDLE_EXPORTED`

**`EVIDENCE_BUNDLE_GENERATED` payload**

```json
{
  "payload": {
    "bundle": {
      "evidence_bundle_id": "evb_01J...",
      "bundle_hash": "sha256:...",
      "artifacts": [
        { "kind": "bundle_pdf", "ref": "s3://.../evidence.pdf", "hash": "sha256:..." },
        { "kind": "bundle_json", "ref": "s3://.../evidence.json", "hash": "sha256:..." }
      ],
      "covers": {
        "artifact_id": "art_...",
        "from_version_id": "ver_...",
        "to_version_id": "ver_..."
      }
    }
  }
}
```

---

## Anchor conventions (cross-artifact)

- Code: `git_hunk` with `path:src/foo.py@hunk:17-29`.
- PDF: `pdf_bbox` for highlights, `pdf_textspan` for text spans.
- XLSX: `xlsx_cell` and `xlsx_range` for sheet references.

---

## Evidence bundle JSON (minimal)

```json
{
  "bundle_id": "evb_...",
  "generated_at": "...",
  "tenant_id": "tnt_acme",
  "bead_id": "bead_...",
  "artifact": { "artifact_id": "art_...", "kind": "pdf" },
  "versions": { "from": "ver_...", "to": "ver_..." },
  "diff": { "diff_id": "dif_...", "metrics": {} },
  "policy": { "risk_tier": "L4", "packs": ["pack_nomotic@1.2.0"] },
  "ai_reviews": [{ "run_id": "run_...", "review_hash": "sha256:..." }],
  "annotations": [{ "anchor": {}, "tags": [], "severity": "high", "comment": "..." }],
  "decisions": [{ "decision_id": "dec_...", "result": "approved", "by": "user:alice" }],
  "integrity": { "event_chain_head": "evt_...", "bundle_hash": "sha256:..." }
}
```

---

## Minimal adapter layer for Beads

### GuardSpine log layout

```
.beads/
  beads.jsonl              (existing)
  guard/
    events/
      guard_events.jsonl   <- append-only GuardSpine log
    artifacts/
      manifests/
    bundles/
  cache/
    guard.sqlite           <- local cache (gitignored)
```

### GuardAdapter responsibilities

1. `register_artifact(bead_id, kind, locator, labels) -> artifact_id`
2. `add_version(artifact_id, content_ref) -> version_id + hash`
3. `compute_diff(from_version, to_version) -> diff_id`
4. `emit_event(event_type, refs, payload, policy) -> event_id`
5. `generate_bundle(bead_id, artifact_id, from_version, to_version) -> evidence_bundle_id`

Implementation details:

- Append one JSON line to `guard_events.jsonl`.
- Update `guard.sqlite` for fast query.
- Optionally update Beads status (blocked/unblocked) based on policy.

### CLI surface (minimal)

- `beads guard register ...`
- `beads guard version add ...`
- `beads guard diff ...`
- `beads guard review ...`
- `beads guard approve ...`
- `beads guard bundle ...`
- `beads guard export ...`

### Regulated mode enforcement

If `risk_tier >= L3`, block publication unless an `APPROVAL_GRANTED` event exists for
that diff/version pair. This maps to Beads statuses (blocked/unblocked).

---

## CodeGuard mapping (translation-first)

CodeGuard can translate existing outputs into GuardSpine events without refactoring:

- `ARTIFACT_VERSION_ADDED` (for git commit/ref)
- `ARTIFACT_DIFF_COMPUTED` (commit diff)
- `MODEL_REVIEW_COMPLETED` (one or more model runs)
- `RISK_TIER_SET`
- `APPROVAL_REQUESTED` / `APPROVAL_GRANTED`
- `EVIDENCE_BUNDLE_GENERATED`

This keeps Beads as the spine and CodeGuard as the audit plane.
