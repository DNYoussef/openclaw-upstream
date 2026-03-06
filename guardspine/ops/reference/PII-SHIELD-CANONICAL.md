# PII-Shield: Canonical Reference

**Last updated**: 2026-02-23
**Status**: Integrated across 3 repos; standalone repo planned

---

## What It Is

PII-Shield is an entropy-based secret detection and redaction system integrated into the
GuardSpine ecosystem. It prevents secrets and PII from leaking into AI prompts, PR comments,
and evidence bundles.

**Core technique**: Shannon entropy analysis + bigram frequency detection. High-entropy strings
that match secret-like character distributions are replaced with deterministic HMAC tokens
(`[HIDDEN:a1b2c3]`), preserving referential integrity across bundles without exposing values.

## Where It Lives

| Repo                         | What                                                          | Files                                                  |
| ---------------------------- | ------------------------------------------------------------- | ------------------------------------------------------ |
| **codeguard-action**         | Full integration: local entropy detector + remote WASM client | `src/pii_shield.py`, `src/adapters/pii_wasm_client.py` |
| **guardspine-local-council** | Sanitizer interface for Ollama prompts                        | `src/guardspine_local_council/council.py`              |
| **GuardSpine backend**       | Guard lane sanitization hooks                                 | `app/routers/guard_lanes.py`                           |

## Canonical Documentation

The primary PII-Shield documentation is in the
[codeguard-action README](https://github.com/DNYoussef/codeguard-action#pii-shield-integration),
which covers:

- Why PII-Shield matters (secrets in diffs sent to AI providers)
- Three deployment modes: Kubernetes sidecar, Docker standalone, local mode
- Configuration reference (12 inputs)
- Hash field preservation (SHA-256 fields whitelisted automatically)
- Custom regex whitelist (`PII_SAFE_REGEX_LIST`)
- Org-wide HMAC salt requirements
- Cross-ecosystem integration matrix

## Design Principles

1. **Fail-closed by default**: If sanitization errors occur, the action fails rather than
   sending unsanitized content to AI providers.
2. **Raw diff never modified**: PII-Shield operates on copies. The evidence bundle hash chain
   covers sanitized content, so verification remains valid.
3. **Deterministic tokens**: Same secret + same salt = same `[HIDDEN:...]` token across all
   bundles, enabling cross-bundle correlation in audits.
4. **Hash field preservation**: GuardSpine SHA-256 hashes (`content_hash`, `chain_hash`,
   `root_hash`, `diff_hash`, `signature_value`, `signed_hash`) are automatically extracted
   before sanitization and reinjected after.

## Architecture

```
Raw diff
  |
  +-- SHA-256 hash (raw diff preserved for integrity proof)
  |
  +-- PII-Shield sanitize -----> Sanitized diff
        |                            |
        |                     AI model review (Claude/GPT/Gemini/Ollama)
        |                            |
        v                            v
   Sanitization attestation    AI findings (on sanitized content)
        |                            |
        +------- Evidence Bundle ----+
```

## Contributors

- **Ilya Ploskovitov** ([@aragossa](https://github.com/aragossa)): Original Go sidecar,
  WASM port, 4 PRs merged across codeguard-action and guardspine-local-council.

## Planned: Standalone Repo

`DNYoussef/pii-shield` will be published as a standalone Apache 2.0 repo containing:

- Go sidecar source
- WASM build artifacts
- Python client library (extracted from codeguard-action)
- Integration tests

Until then, this document and the codeguard-action README are the canonical references.
