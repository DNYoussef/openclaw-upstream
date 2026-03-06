# n8n-nodes-guardspine - Linus Audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 4
- Boundary hygiene: 6
- Test quality: 5
- Operational safety: 5
- Complexity / maintainability: 6

## P0 Findings (Must Fix)

1. ImageGuard / PDFGuard / SheetGuard send wrong request field
   - These nodes POST `artifact_kind`, but the backend expects `artifact_type` (required). The request will 422 and the nodes will fail in real use.
   - Fix: change `artifact_kind` to `artifact_type` in all three nodes.
   - Files: `D:\Projects\n8n-nodes-guardspine\nodes\GuardSpineImageGuard\GuardSpineImageGuard.node.ts`, `D:\Projects\n8n-nodes-guardspine\nodes\GuardSpinePDFGuard\GuardSpinePDFGuard.node.ts`, `D:\Projects\n8n-nodes-guardspine\nodes\GuardSpineSheetGuard\GuardSpineSheetGuard.node.ts`

## P1 Findings (Should Fix)

1. Evidence hashes are not verifiable evidence bundles
   - Nodes surface `evidence_hash` and `bundle_hash` strings but do not provide or import a v0.2.0 evidence bundle. The values are opaque and cannot be verified offline.
   - Impact: workflows appear to have evidence but lack the canonical artifacts; audit trail is brittle.
   - Fix: add a node (or option) that imports/exports real bundles via `/api/v1/bundles/import` and links `bundle_id` to the workflow.
   - Files: `D:\Projects\n8n-nodes-guardspine\nodes\GuardGate\GuardGate.node.ts`, `D:\Projects\n8n-nodes-guardspine\nodes\CodeGuard\CodeGuard.node.ts`, `D:\Projects\n8n-nodes-guardspine\nodes\EvidenceSeal\EvidenceSeal.node.ts`, `D:\Projects\n8n-nodes-guardspine\nodes\CouncilVote\CouncilVote.node.ts`

2. ApprovalWait fallback webhook URL is unsafe
   - If `getNodeWebhookUrl` is unavailable, the node falls back to `${credentials.baseUrl}/webhook-waiting/...` which points at GuardSpine, not n8n.
   - Impact: approvals never resume; workflows hang.
   - Fix: require `getNodeWebhookUrl` or accept a user-specified n8n base URL. Do not default to GuardSpine base URL.
   - File: `D:\Projects\n8n-nodes-guardspine\nodes\ApprovalWait\ApprovalWait.node.ts`

3. CouncilVote relies on demo-only backend
   - The backend endpoint returns 501 unless demo mode is enabled.
   - Impact: node fails silently in real environments; error handling does not inform the operator.
   - Fix: detect 501 and raise a clear “demo-only” error; document it in README.
   - File: `D:\Projects\n8n-nodes-guardspine\nodes\CouncilVote\CouncilVote.node.ts`

## P2 Findings (Cleanup / Consistency)

1. README is incomplete and out of date
   - It lists only two nodes and omits the majority of implemented nodes and their required inputs.
   - Fix: document all nodes and their API endpoints, especially EvidenceSeal and ApprovalWait.
   - File: `D:\Projects\n8n-nodes-guardspine\README.md`

2. Tests are structural only
   - Tests mock httpRequest but do not verify request payload shape against the actual backend schema; this allowed the P0 artifact_kind bug.
   - Fix: add contract tests with fixture payloads that match backend models.
   - File: `D:\Projects\n8n-nodes-guardspine\__tests__\nodes.test.ts`

## Concrete Fixes (High-Leverage)

1. Fix `artifact_type` fields in Image/PDF/Sheet guards.
2. Add a “Bundle Import” node or option to pass v0.2.0 bundles into `/bundles/import`.
3. Require a valid n8n callback URL for ApprovalWait.
4. Add demo-mode detection for CouncilVote.
5. Update README and add contract tests.

## Interop Risk Statement

These nodes are currently generating hashes and “evidence” values that are not backed by canonical v0.2.0 bundles. Without a bundle import/export path, workflows cannot be verified offline. Additionally, three guard nodes are broken due to request schema mismatch.

## Skeptical Annex (Assumptions / Edge Cases / Evidence)

- Assumptions:
  - GuardSpine backend `guard/evaluate` requires `artifact_type` (no alias for `artifact_kind`).
  - Evidence hashes are not sufficient for evidence verification without bundles.
- Edge cases not directly tested here:
  - Large payloads in `artifact_data` and timeouts on GuardGate/CodeGuard.
  - n8n webhook URL resolution in different deployment modes.
- Possible false positives/negatives:
  - If backend accepts `artifact_kind` as an alias, P0 #1 is downgraded; current backend schema suggests it does not.
- Evidence reviewed:
  - `nodes/*` (GuardGate, CodeGuard, EvidenceSeal, ApprovalWait, GuardSpineImageGuard, GuardSpinePDFGuard, GuardSpineSheetGuard)
  - `nodes/types.ts`
  - `__tests__/nodes.test.ts`
  - Backend `app/routers/guard.py`, `app/routers/council.py`
