# GuardSpine OSS Boundary Specification

This document defines the hard boundary between open-source and proprietary
code across the GuardSpine ecosystem. Every contributor, contractor, and
automated system must respect these rules without exception.

---

## Rules (R0-R6): No Exceptions

**R0: Trust Independence**
OSS repos must function without any private repo. A developer cloning only
the OSS repos must be able to build, test, and verify bundles with zero
references to GuardSpine or guardspine-product.

**R1: One-Way Dependencies**
OSS never imports from private. Private may import OSS. The dependency arrow
points in one direction only: private -> OSS. Any reverse import is a defect.

**R2: Verifiability Sacred**
All verification logic stays in OSS. If a bundle can be sealed, it can be
verified using only open-source code. No verification step may require a
proprietary library, API call, or service.

**R3: Premium = Judgment Only**
Private repos contain judgment and intelligence -- scoring heuristics,
council calibration, compression algorithms, policy engines. They never
contain truth. Truth (schemas, verification, sealing) lives in OSS.

**R4: No Bespoke Trap**
OSS uses standard formats: JSON, YAML, SARIF, JSON Schema. No proprietary
encoding, no custom binary formats, no vendor-locked serialization. A
third-party tool must be able to consume GuardSpine outputs without our code.

**R5: Mixed Repos Physically Separated**
In repos that contain both OSS and premium code (e.g., n8n-nodes-guardspine),
OSS code lives in nodes/core/ and premium code lives in nodes/premium/.
These directories have separate LICENSE files. No cross-imports from core/
into premium/ internals.

**R6: License Clarity**
Every repo has a LICENSE file in its root. OSS repos use Apache 2.0 unless
otherwise noted. Private repos use a Proprietary license. There is no
ambiguity.

---

## Repo-by-Repo Specification

| Repo                          | License     | Layer                | What Goes In                                                             | What Stays Out                                |
| ----------------------------- | ----------- | -------------------- | ------------------------------------------------------------------------ | --------------------------------------------- |
| guardspine-spec               | Apache 2.0  | Truth                | JSON schemas, specification docs, test vectors, format definitions       | NO policy logic, scoring, compression         |
| guardspine-verify             | Apache 2.0  | Truth                | Offline verifier CLI, schema validation, seal checking                   | NO network calls, premium features            |
| guardspine-connector-template | Apache 2.0  | Truth                | Adapter boilerplate, interface contracts, example connectors             | NO org-specific config                        |
| codeguard-action              | Apache 2.0  | Distribution         | GitHub Action for PR review, bundle attachment, SARIF output             | NO council, compression, org policy           |
| n8n-nodes-guardspine          | MIT         | Distribution (Mixed) | Core nodes in nodes/core/ (OSS), premium nodes in nodes/premium/ (gated) | NO premium logic in core/                     |
| guardspine-kernel             | Apache 2.0  | Trust Anchor         | JSON Schema definitions, verify.ts, seal.ts, core types                  | NO backend deps, no HTTP, no runtime services |
| guardspine-adapter-webhook    | Apache 2.0  | Integration          | Webhook handler, bundle emitter, event formatting                        | NO org policy, compression                    |
| guardspine-local-council      | Apache 2.0  | Intelligence (OSS)   | Ollama provider, basic aggregator, local model runner                    | NO Byzantine voting, calibration, cloud SLAs  |
| GuardSpine                    | Proprietary | Judgment             | FastAPI backend, 149 routes, premium services                            | Everything premium (this IS the premium repo) |
| guardspine-product            | Proprietary | Judgment             | Guard lanes, compression, council logic, nomotic engine                  | Everything premium (this IS the premium repo) |

---

## OSS = Truth, Private = Judgment

The split philosophy is simple: truth is free, judgment is paid.

**Truth** means the ability to answer "is this bundle valid?" A developer,
auditor, or CI system can take any GuardSpine bundle and verify its
integrity, check its schema conformance, and validate its seals using only
open-source tooling. This is non-negotiable. If verification requires a
paid service, the entire trust model collapses.

**Judgment** means the ability to answer "is this bundle good?" Scoring
code quality, running council debates, compressing review output, applying
organizational policy, calibrating model confidence -- these are intelligence
layers that sit on top of truth. They consume verified bundles and produce
assessments. They are valuable, but they are opinions, not facts.

This split has a practical consequence: any premium feature that accidentally
embeds verification logic must be extracted back to OSS. The test is always
the same -- can a user verify a bundle without our paid code? If not, we
have a boundary violation.

---

## CI Enforcement

A leak-check CI job (tracked as GS-D3) will enforce these boundary rules
automatically on every pull request across all repos.

The job will:

1. **Import scanning**: Parse all import/require statements in OSS repos.
   Flag any reference to GuardSpine, guardspine-product, or any private
   package name. Fail the build on detection.

2. **Schema format check**: Verify that all output formats in OSS repos
   are standard (JSON, YAML, SARIF). Flag any custom binary or proprietary
   encoding.

3. **License file check**: Confirm LICENSE exists at repo root. Confirm
   its content matches the expected license for that repo.

4. **Mixed repo separation check**: For n8n-nodes-guardspine, verify that
   no file in nodes/core/ imports from nodes/premium/. The reverse is
   allowed.

5. **Network isolation check**: For guardspine-verify and guardspine-kernel,
   confirm zero HTTP/fetch/axios/request imports. These repos must work
   fully offline.

The job runs as a required status check. No PR merges if it fails.

---

## Contractor Quick Reference

One sentence per repo for fast lookup:

- **guardspine-spec**: Schemas and test vectors only -- no logic, no code that runs.
- **guardspine-verify**: Offline CLI that checks bundles -- no network, no premium.
- **guardspine-connector-template**: Boilerplate for new adapters -- no org config.
- **codeguard-action**: GitHub Action that attaches bundles to PRs -- no council or policy.
- **n8n-nodes-guardspine**: Core nodes are OSS in core/, premium nodes are gated in premium/ -- never cross-import.
- **guardspine-kernel**: The trust anchor with verify.ts and seal.ts -- no HTTP, no backend deps.
- **guardspine-adapter-webhook**: Receives webhooks and emits bundles -- no policy, no compression.
- **guardspine-local-council**: Runs local models via Ollama with basic aggregation -- no Byzantine voting or cloud features.
- **GuardSpine**: The proprietary backend -- everything premium lives here.
- **guardspine-product**: The proprietary product logic -- guard lanes, compression, council, nomotic engine.
