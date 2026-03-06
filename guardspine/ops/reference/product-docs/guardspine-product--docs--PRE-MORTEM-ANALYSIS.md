# Pre-Mortem Analysis

Five failure scenarios analyzed before they occur. Each includes detection, mitigation, and prevention strategies.

---

## GS-RISK-1: Backend Not Running

### Scenario

The GuardSpine backend process crashes or fails to start. Users see connection errors. Evidence collection stops silently. Compliance gaps accumulate without alerting.

### Detection

| Signal                  | Method                                | Latency               |
| ----------------------- | ------------------------------------- | --------------------- |
| Process exit            | Systemd/Docker restart policy         | < 5s                  |
| Health endpoint failure | `/health` returns non-200             | Polling: 10s interval |
| Evidence gap            | No new evidence bundles for > 5 min   | Watchdog timer        |
| Queue backlog           | Message queue depth exceeds threshold | Metric alert          |

### Health Check Design

```
GET /health -> 200 OK
{
  "status": "healthy",
  "uptime_seconds": 43200,
  "checks": {
    "database": "ok",
    "redis": "ok",
    "evidence_chain": "ok",
    "connectors_healthy": 8,
    "connectors_unhealthy": 0
  }
}
```

### Mitigation

1. **Immediate**: Docker restart policy `unless-stopped` with max 5 retries
2. **Short-term**: Systemd watchdog with 30s timeout; auto-restart on failure
3. **Medium-term**: Kubernetes liveness + readiness probes (10s interval, 3 failure threshold)
4. **Alerting**: PagerDuty integration on 2 consecutive health check failures

### Prevention

- Graceful shutdown handlers for SIGTERM/SIGINT
- Startup self-test: verify DB, Redis, and at least 1 connector before accepting traffic
- Pre-deploy smoke test in CI pipeline

---

## GS-RISK-2: OpenRouter Key Missing

### Scenario

The OpenRouter API key (used for multi-model council) is missing, expired, or rate-limited. Council deliberations fail. Policy evaluations that depend on AI analysis return errors.

### Detection

| Signal                  | Method                                    | Latency    |
| ----------------------- | ----------------------------------------- | ---------- |
| 401/403 from OpenRouter | HTTP response code check                  | Immediate  |
| Key env var missing     | Startup validation                        | Boot time  |
| Rate limit (429)        | Response header parsing                   | Immediate  |
| Key expiry approaching  | TTL check against known rotation schedule | Daily cron |

### Mitigation

1. **Fallback to local model**: If OpenRouter is unavailable, route to Ollama local council (degraded: single-model, no Byzantine consensus)
2. **Key rotation**: Store keys in vault (HashiCorp Vault / AWS Secrets Manager) with 90-day rotation
3. **Multi-key pool**: Maintain 2+ OpenRouter keys; round-robin with automatic failover
4. **Graceful degradation**: Mark council responses as `"confidence": "degraded"` when running on fallback

### Fallback Decision Tree

```
OpenRouter request fails
  |
  +-- 401/403 (auth error)
  |     +-- Try backup key
  |     +-- If no backup: fallback to Ollama local
  |     +-- Alert: KEY_ROTATION_NEEDED (P2)
  |
  +-- 429 (rate limit)
  |     +-- Exponential backoff (1s, 2s, 4s, max 30s)
  |     +-- After 3 retries: fallback to Ollama local
  |     +-- Alert: RATE_LIMIT_HIT (P3)
  |
  +-- 5xx (server error)
        +-- Retry once after 2s
        +-- Fallback to Ollama local
        +-- Alert: OPENROUTER_DOWN (P2)
```

### Prevention

- Startup validation: fail-fast if no API key and no local model available
- Key health check: test API key validity on boot and every 6 hours
- Budget alerts: OpenRouter spending threshold notifications

---

## GS-RISK-3: Approval Timeout Hangs Workflow

### Scenario

A Nomotic governance workflow requires human approval (e.g., policy exception). The approver is on vacation, sick, or ignores the notification. The workflow hangs indefinitely, blocking evidence collection or remediation actions.

### Detection

| Signal                 | Method                 | Latency |
| ---------------------- | ---------------------- | ------- |
| Approval pending > 4h  | Workflow state monitor | 4h      |
| Approval pending > 24h | Escalation trigger     | 24h     |
| Approval pending > 72h | Circuit breaker        | 72h     |

### Mitigation: Circuit Breaker + Escalation Timer

```
Approval requested (T=0)
  |
  T+4h   -> Reminder notification to approver
  |
  T+24h  -> Escalation to approver's manager
  |         + Slack/email with context summary
  |
  T+48h  -> Second escalation to department head
  |         + Mark workflow as "escalated" in dashboard
  |
  T+72h  -> Circuit breaker OPENS
            + Auto-action based on policy:
              - If policy says "fail-safe": approve with audit flag
              - If policy says "fail-secure": deny with audit flag
            + Alert: APPROVAL_TIMEOUT_CIRCUIT_BREAK (P1)
            + Evidence bundle captures timeout + auto-decision
```

### Prevention

- Configurable timeout per approval type (default: 72h)
- Delegation rules: if primary approver unavailable, route to delegate
- Bulk approval UI for low-risk items
- Mobile push notifications for approvals

---

## GS-RISK-4: Mock API Diverges from Real API

### Scenario

During development and testing, mock APIs are used for connectors (DocuSign, Jira, etc.). Over time, the real API changes (new fields, deprecated endpoints, changed behavior). Tests pass against mocks but fail in production.

### Detection

| Signal                            | Method                        | Latency    |
| --------------------------------- | ----------------------------- | ---------- |
| Schema mismatch                   | Contract test failure         | CI run     |
| New fields in production response | Response schema validation    | Runtime    |
| Deprecated endpoint 410           | HTTP status monitoring        | Runtime    |
| Changelog published               | Vendor RSS/webhook monitoring | Hours-days |

### Mitigation: Contract Testing + Schema Validation

**Contract Testing Pipeline**:

```
1. Record real API responses (sanitized) -> golden fixtures
2. Generate JSON Schema from golden fixtures
3. Validate mocks against schema on every CI run
4. Monthly: re-record golden fixtures from real API
5. Diff detection: alert on schema changes
```

**Runtime Schema Validation**:

```python
# Every connector response passes through schema validation
response = connector.call_api(endpoint)
validated = schema_validator.validate(response, expected_schema)
if not validated:
    log.warning("Schema drift detected", extra={
        "connector": connector.name,
        "endpoint": endpoint,
        "diff": validated.diff,
    })
    emit_evidence("schema_drift", validated.diff)
```

### Prevention

- Pin connector SDK versions; upgrade intentionally with schema diff review
- Subscribe to vendor changelogs (DocuSign, Jira, GitHub API announcements)
- Quarterly integration test runs against real sandbox APIs
- Schema version field in all mock fixtures

---

## GS-RISK-5: Redundant n8n Nodes

### Scenario

As GuardSpine workflows grow in complexity, n8n automation nodes proliferate. Duplicate nodes perform the same function (e.g., three different "send Slack notification" nodes with slightly different configs). This creates maintenance burden, inconsistent behavior, and wasted execution time.

### Detection

| Signal                      | Method                                     | Latency          |
| --------------------------- | ------------------------------------------ | ---------------- |
| Duplicate node types        | Node registry audit                        | Weekly cron      |
| Same input/output signature | Signature hashing                          | On workflow save |
| Unused nodes                | Execution log analysis (0 runs in 30 days) | Monthly          |
| Config drift                | Diff between nodes of same type            | On workflow save |

### Mitigation: Deduplication Strategy + Node Registry

**Node Registry**:

```json
{
  "nodes": {
    "slack-notify": {
      "canonical_id": "slack-notify-v2",
      "instances": ["workflow-1:node-3", "workflow-4:node-7"],
      "config_hash": "a1b2c3",
      "last_used": "2026-01-28T10:00:00Z"
    }
  },
  "duplicates_detected": 3,
  "unused_nodes": 1
}
```

**Deduplication Process**:

1. **Inventory**: Scan all workflows, extract node type + config hash
2. **Group**: Cluster nodes by (type, input_schema, output_schema)
3. **Identify canonical**: Pick the most-used or most-recently-updated as canonical
4. **Propose merge**: Generate diff showing what would change
5. **Execute**: Replace duplicates with references to canonical (requires human approval)

**Node Hygiene Rules**:

- Every new node must register in the node registry
- Duplicate type + similar config triggers a warning on workflow save
- Unused nodes (0 executions in 30 days) are flagged for removal
- Maximum 1 instance of each notification node per workflow (enforced by linter)

### Prevention

- Node registry as source of truth; new nodes check for existing equivalents
- Workflow linter runs on save: flags duplicates, unused nodes, config drift
- Shared node library: reusable node templates that workflows reference (not copy)
- Quarterly workflow audit: identify and consolidate redundant paths

---

## Risk Summary Matrix

| ID        | Risk                   | Severity | Likelihood | Detection                  | Mitigation Quality               |
| --------- | ---------------------- | -------- | ---------- | -------------------------- | -------------------------------- |
| GS-RISK-1 | Backend not running    | Critical | Medium     | Strong (health checks)     | Strong (auto-restart + alerting) |
| GS-RISK-2 | OpenRouter key missing | High     | Medium     | Strong (startup + runtime) | Strong (fallback + rotation)     |
| GS-RISK-3 | Approval timeout       | High     | High       | Moderate (timer-based)     | Strong (circuit breaker)         |
| GS-RISK-4 | Mock API divergence    | Medium   | High       | Moderate (contract tests)  | Moderate (requires discipline)   |
| GS-RISK-5 | Redundant n8n nodes    | Low      | High       | Moderate (registry audit)  | Moderate (manual merge step)     |
