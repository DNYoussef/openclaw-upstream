## Doc Evidence Pack Specification v1.0

### Purpose

A Doc Evidence Pack is produced by each DocSync run. It extends the standard Evidence Pack with doc-specific fields, proving what the AI inspected, what it found, and what it proposes.

### Schema

```json
{
  "doc_evidence_pack_version": "DOC_EVIDENCE_PACK/1.0",
  "pack_id": "uuid",
  "doc_id": "string (from guardspine.docs.yaml)",
  "doc_version_hash": "sha256:hex (hash of doc at time of inspection)",
  "mode": "spec | reality",
  "run_id": "uuid (unique per DocSync run)",
  "run_timestamp": "ISO8601",
  "claim_results": [
    {
      "claim_id": "string (stable ID for this claim)",
      "claim_text": "string (the assertion extracted from the doc)",
      "claim_type": "api_contract | invariant | workflow | config_default | security_policy",
      "status": "supported | violated | ambiguous | untestable",
      "evidence_refs": [
        {
          "artifact_id": "string (file path)",
          "snippet_hash": "sha256:hex",
          "range": { "start_line": "int", "end_line": "int" },
          "relationship": "supports | contradicts | partial"
        }
      ],
      "proposed_patch_ref": "string | null (reference to proposed change)",
      "risk_tier": "L0 | L1 | L2 | L3 | L4",
      "confidence": "float 0.0-1.0"
    }
  ],
  "tests": [
    {
      "test_id": "uuid",
      "command": "string",
      "exit_code": "int",
      "log_hash": "sha256:hex (hash of stdout+stderr)",
      "duration_ms": "int",
      "artifacts": ["string (paths to test output files)"]
    }
  ],
  "inspection_trace_digest": "sha256:hex (hash of all receipt IDs in order)",
  "budget_usage": {
    "files_accessed": "int",
    "steps_taken": "int",
    "tokens_consumed": "int",
    "budget_limit": {
      "max_files": "int",
      "max_steps": "int",
      "max_tokens": "int"
    }
  },
  "summary": {
    "total_claims": "int",
    "supported": "int",
    "violated": "int",
    "ambiguous": "int",
    "untestable": "int",
    "tests_passed": "int",
    "tests_failed": "int"
  },
  "integrity": {
    "hash_algorithm": "sha256",
    "pack_root_hash": "sha256:hex",
    "signatures": []
  }
}
```

### Claim Types

| Type            | Description           | Example                                   |
| --------------- | --------------------- | ----------------------------------------- |
| api_contract    | API endpoint behavior | "POST /users returns 201"                 |
| invariant       | Code invariant        | "Passwords are always hashed with bcrypt" |
| workflow        | Process flow          | "PR requires 2 approvers for L3+"         |
| config_default  | Configuration default | "Rate limit defaults to 100/min"          |
| security_policy | Security requirement  | "All endpoints require authentication"    |

### Status Values

| Status     | Meaning                                     | Mode Behavior                        |
| ---------- | ------------------------------------------- | ------------------------------------ |
| supported  | Evidence confirms claim                     | Both: no action                      |
| violated   | Evidence contradicts claim                  | spec: alert; reality: propose doc PR |
| ambiguous  | Insufficient evidence                       | Both: flag for human review          |
| untestable | Claim cannot be verified by code inspection | Both: skip, log                      |

### Integration

- Signs and seals as standard Evidence Bundle extension
- Claim results become evidence items in the bundle
- Test results attach as test receipts
- The inspection_trace_digest links to access receipts from GS-S14
