# GuardSpine OpenClaw Integration Audit (guardspine-openclaw)

Date: 2026-02-03
Repo: D:\Projects\guardspine-openclaw
Scope: plugin.js, rlm-docsync, evidence-evaluator, redteam provider, plugin manifest

Scorecard (0-10)

- Contract correctness: 2
- Boundary hygiene: 3
- Test quality: 2
- Operational safety: 4
- Complexity/maintainability: 4

P0 Findings (must fix)

1. Multiple custom canonicalization + chain implementations (contract drift from kernel/spec).
   - plugin EvidencePack uses custom canonicalJSON and custom chain/root logic, not the kernel or verifier.
     Path: `D:\Projects\guardspine-openclaw\plugin.js:106`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:113`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:158`
   - rlm-docsync EvidencePack uses schema_version "1.0" and its own hash_chain format and stable_json.
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:73`
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:75`
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:132`
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:459`
   - redteam provider writes its own evidence bundle with a single hash field and no kernel/verify integration.
     Path: `D:\Projects\guardspine-openclaw\redteam\providers\guardspine_provider.py:286`
     Path: `D:\Projects\guardspine-openclaw\redteam\providers\guardspine_provider.py:309`
     Impact: Evidence can be produced that will not verify against guardspine-verify/kernel, undermining ecosystem interop.

2. L4 approval can be self-approved via tool call (no auth gate).
   - guardspine_approve is registered as a tool and directly approves pending L4 without authentication.
     Path: `D:\Projects\guardspine-openclaw\plugin.js:683`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:692`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:699`
     Impact: Any agent with tool access can approve its own L4 actions, bypassing human approval intent.

P1 Findings (high risk)

1. Internal evidence schema mismatch: evaluator expects fields not produced by rlm-docsync packs.
   - evaluator requires id/manifest_hash/final_hash and hash_chain list entries.
     Path: `D:\Projects\guardspine-openclaw\evidence-evaluator\evaluate_evidence.py:319`
     Path: `D:\Projects\guardspine-openclaw\evidence-evaluator\evaluate_evidence.py:334`
   - rlm-docsync produces pack_id/schema_version/hash_chain dict with entries[].
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:75`
     Path: `D:\Projects\guardspine-openclaw\rlm-docsync\rlm_docsync.py:148`
     Impact: Evaluator cannot validate the packs it is supposed to audit; council signal becomes unreliable.

2. Unknown tool default classified as L2 (allowed in enforce mode).
   - classifyRisk falls back to L2 for any unknown tool name.
     Path: `D:\Projects\guardspine-openclaw\plugin.js:86`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:99`
     Impact: New tools are allowed with only evidence logging, bypassing L3/L4 safeguards.

3. Evidence packs are written locally and never imported into backend.
   - Evidence pack written to ~/.openclaw/guardspine-logs; no backend import/verify integration.
     Path: `D:\Projects\guardspine-openclaw\plugin.js:176`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:632`
     Impact: Evidence is siloed and not part of the canonical ingest/export/verify pipeline.

P2 Findings (cleanup/maintainability)

1. Config guardspine_root is defined but unused.
   - openclaw.plugin.json defines guardspine_root, but no usage in plugin code.
     Path: `D:\Projects\guardspine-openclaw\openclaw.plugin.json:21`
     Impact: Confusing configuration; suggests intended integration that is not implemented.

2. Evidence pack contains un-hashed fields (created_at) that can be mutated without chain breakage.
   - created_at is included in items, but content_hash is computed from content only.
     Path: `D:\Projects\guardspine-openclaw\plugin.js:123`
     Path: `D:\Projects\guardspine-openclaw\plugin.js:139`
     Impact: Audit metadata can be altered without detection (if used downstream).

Concrete Fixes (targeted)

- Replace all custom canonicalization + chain logic with @guardspine/kernel sealing and guardspine-verify compatibility.
  - plugin.js EvidencePack: remove canonicalJSON + hash_chain, call kernel seal/verify.
  - rlm-docsync + redteam provider: emit v0.2.0 bundles via kernel, or explicitly mark as legacy/non-canonical.
- Lock down L4 approval path:
  - Remove guardspine_approve tool OR require an authenticated, out-of-band token check before approval.
  - Do not treat missing pendingApprovals entry as implicit approval.
- Align evaluator schema with emitted packs (single schema); add round-trip tests to prove evaluator can validate real output.
- Wire evidence packs to backend import endpoint (POST /api/v1/bundles/import) and verify export via guardspine-verify.
- Remove unused guardspine_root config or implement its usage.

Interop Risk Statement
This repo currently emits evidence packs via multiple non-canonical formats and does not ingest into the backend import/export/verify pipeline. Left as-is, GuardSpine evidence from OpenClaw integrations will not be provably verifiable and may diverge from spec/kernel expectations, undermining cross-repo interop guarantees.

Tests Run

- None (audit only; no repo tests executed).

Skeptical Annex

- Assumptions: guardspine-spec v0.2.0 remains the canonical bundle; kernel/verify are the sole canonicalization authority.
- Possible false positives: some modules may be legacy or unused paths; if rlm-docsync or redteam provider are not in production, impact is lower.
- Missing evidence: no OpenClaw runtime hooks inspected here; no live integration run in this repo.
- Edge cases not validated: compatibility with kernel proofVersion v0.2.0, adapter import pathway, or signature requirements.
- Recommendation: run a live OpenClaw integration flow and confirm backend import/export/verify using artifacts produced by this repo once kernel-only sealing is implemented.
