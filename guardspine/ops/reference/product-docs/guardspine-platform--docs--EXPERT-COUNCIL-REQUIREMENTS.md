# GuardSpine Expert Council Requirements

> "$1B hiring panel" - What world-class experts would demand

## The Council

| #   | Role                   | Key Question                                      | Week 1 Critique                                          |
| --- | ---------------------- | ------------------------------------------------- | -------------------------------------------------------- |
| 1   | **Enterprise CISO**    | "Will this reduce risk and unblock work?"         | Lead with throughput + evidence, not AI                  |
| 2   | **Head of Compliance** | "Can I hand this to an auditor?"                  | Add evidence scope, deterministic diffs, signer identity |
| 3   | **Product Counsel**    | "Who is liable? Is this subpoena-proof?"          | Need immutability, retention, "what is asserted" section |
| 4   | **Records Management** | "Artifacts are records. Records have lifecycles." | Become provenance layer, not file store                  |
| 5   | **ML Lead**            | "What is deterministic vs model-based?"           | Models suggest, never author truth                       |
| 6   | **Crypto Architect**   | "How do we prove no tampering?"                   | Signing + key rotation + offline verification            |
| 7   | **Workflow Architect** | "How does this land without revolt?"              | Pristine API, ServiceNow/Jira as downstream              |
| 8   | **VP Product**         | "What do we sell first?"                          | Sell approval inbox, evidence bundles as expansion       |
| 9   | **Enterprise Sales**   | "Who signs, blocks, champions?"                   | Champion = compliance ops, blocker = IT/change mgmt      |
| 10  | **UX Lead**            | "Can humans approve in 10 seconds?"               | Diff Postcard is the wedge                               |

## Unanimous Convergence Points

```
1. UI IS THE DIFFERENTIATOR
   - Approval throughput
   - Visual trust calibration
   - Diff Postcard as wedge feature

2. TRUTH MUST BE DETERMINISTIC
   - Models annotate/suggest
   - Models NEVER define ground truth
   - Deterministic diff algorithms
   - Verifiable hashes

3. WIN BY INTEGRATION
   - SharePoint/Drive (document universe)
   - ServiceNow/Jira (workflow anchor)
   - DLP feeds (signal sources)
   - SSO (identity foundation)

4. DEFENSIBILITY IS THE PRODUCT
   - Bundle verification
   - Retention semantics
   - Provenance clarity
   - Offline verification
```

## Implementation Checklist

### Evidence Bundle Requirements

- [ ] **Evidence Scope** - "What is asserted" section in every bundle
- [ ] **Deterministic Diff Metadata** - Algorithm ID, version, content hashes
- [ ] **Signer Identity Guarantees** - Verified identity from IdP
- [ ] **Immutability Semantics** - WORM storage support, tamper evidence
- [ ] **Retention Policies** - Configurable per artifact class
- [ ] **Export Formats** - "Boring and standard" (JSON, ZIP, PDF)
- [ ] **Offline Verification** - Works without network access

### Diff System Requirements

- [ ] **Deterministic Core** - Same input = same output, always
- [ ] **Model Annotation Layer** - Separate from ground truth
- [ ] **AI Suggestion Framing** - Never says "is", always "suggests"
- [ ] **Confidence Scores** - Visible to reviewer
- [ ] **Audit Trail** - Which model, which version, when

### API Requirements

- [ ] **Search** - Cross-entity, filterable, fast
- [ ] **Fetch Artifacts** - With versions, diffs, metadata
- [ ] **Approval Decisions** - Full audit trail, signed events
- [ ] **Export Bundles** - Multiple formats, verification included
- [ ] **Webhook Support** - For all integration targets

### UX Requirements

- [ ] **10-Second Approval** - Median time target
- [ ] **Diff Postcard** - Quick look, key changes highlighted
- [ ] **Work Graph** - Blocked beads visible at glance
- [ ] **Risk Tier Queue** - Executive dashboard view
- [ ] **Policy Checklist** - Rules evaluated, results shown

## Integration Priority

```
PHASE 1 - FOUNDATION:
  1. SSO + SCIM (Okta/Entra) - Non-negotiable
  2. ServiceNow or Jira - Workflow anchor
  3. Microsoft 365 or Google Drive - Document source
  4. GitHub - Code credibility

PHASE 2 - EXPANSION:
  5. Slack/Teams - Notification layer
  6. GRC export - Compliance completion
  7. DLP signals - Risk automation

PHASE 3 - PLATFORM:
  8. Additional doc systems
  9. Analytics export
  10. Vendor intake
```

## Champion/Blocker Analysis

| Stakeholder        | Role      | Strategy                                   |
| ------------------ | --------- | ------------------------------------------ |
| **Compliance Ops** | Champion  | Show audit prep time reduction             |
| **IT/Change Mgmt** | Blocker   | Incremental deployment, one artifact class |
| **CISO**           | Sponsor   | Risk reduction metrics                     |
| **Legal**          | Validator | Demonstrate defensibility                  |
| **End Users**      | Adopters  | Fast, frictionless approvals               |

## Adoption Strategy

```
1. Start with ONE artifact class (PDF or XLSX)
2. Deploy to ONE team first
3. Prove:
   - Approval throughput improvement
   - Audit evidence quality
   - No workflow disruption
4. Expand by artifact class, then by team
```

## Red Lines (Never Cross)

1. **Models never author truth** - Only annotate, suggest, highlight
2. **Verification must work offline** - No network dependency
3. **Evidence bundles are records** - Treat with legal seriousness
4. **API must be pristine** - No shortcuts, no tech debt
5. **Identity is verified** - SSO source of truth

---

_This document represents the consensus of 10 domain experts on what GuardSpine must deliver to succeed in enterprise markets._
