# GuardSpine Governance Extension

Deny-by-default governance layer for OpenClaw. Gates dangerous tool calls through
L0-L4 risk tiers with evidence packs, multi-model council review, and remote approval.

## Risk Tiers

| Tier | Action             | Examples                          |
| ---- | ------------------ | --------------------------------- |
| L0   | No-op              | sequentialthinking, memory_search |
| L1   | Log only           | rlm_read, web_search              |
| L2   | Evidence pack      | bash, apply_patch                 |
| L3   | 3-model council    | rm -rf, curl, npm install         |
| L4   | Council + approval | credential_access, chmod 777      |

Bash commands are dynamically escalated based on content (e.g. `rm -rf` escalates
from L2 to L3, credential patterns escalate to L4).

## Configuration

Add to your `openclaw.json`:

```json
{
  "plugins": {
    "guardspine-governance": {
      "enforcement_mode": "enforce",
      "council_endpoint": "http://localhost:11434"
    }
  }
}
```

### Modes

- **enforce**: Block unauthorized actions (production)
- **shadow**: Evaluate and log without blocking (rollout)
- **audit**: Development-only pass-through (requires GUARDSPINE_ALLOW_AUDIT_MODE=1)
- **disabled**: No checks

### Council Models (L3)

Sequential evaluation via Ollama (VRAM-safe, one model at a time):

1. qwen3:8b (weight 0.40) - primary evaluator
2. qwen3-coder:30b (weight 0.35) - technical verifier
3. gpt-oss:20b (weight 0.25) - code auditor

On deadlock (1-1-1 split), escalates to L3.5 Claude Opus tie-breaker via OpenRouter
($5/day budget cap).

### L4 Approval

Discord reaction-based (thumbs up/down) with 5-minute timeout.
Falls back to file-based approval if Discord is not configured.

## Components

- `plugin.js` - Core governance plugin (1,252 lines)
- `evidence-evaluator/` - L3 council rubric and evaluation
- `redteam/` - Adversarial testing harness (Promptfoo)
- `rlm-docsync/` - Proof-carrying cognition tools
- `scripts/` - Weekly failure log auditor
- `config/` - Allowlist and pending pattern files

## Tools Provided

- `guardspine_status` - Query mode, evidence summary, classify tool risk
- `guardspine_audit_log` - Read recent governance decisions
- `memory_status` - Context window utilization gauge

## License

Apache-2.0
