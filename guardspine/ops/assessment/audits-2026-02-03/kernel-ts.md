# GuardSpine Kernel Audit (Linus-Style)

Date: 2026-02-03
Repo: D:\Projects\guardspine-kernel

## Findings (ordered by severity)

### High

- None.

### Medium

- Version check missing in verification. `verifyBundle()` does not enforce bundle.version == "0.2.0" (spec requirement), so a structurally-valid bundle with an arbitrary version string will verify as valid. This weakens the wire-contract boundary and can mask downstream drift. (File: D:\Projects\guardspine-kernel\src\verify.ts)

### Low

- Proof version semantics are implicit at runtime. `buildHashChain()` defaults to v0.2.0 but does not record which proof version was used anywhere in the bundle, so consumers must coordinate out-of-band. If legacy proofs are accepted in the same system, this ambiguity increases integration risk. (Files: D:\Projects\guardspine-kernel\src\seal.ts, D:\Projects\guardspine-kernel\src\verify.ts)
- Verification of signature algorithms is permissive: unsupported algorithms are treated as verification failures but do not yield an explicit "unsupported algorithm" error, which makes triage less precise. (File: D:\Projects\guardspine-kernel\src\verify.ts)

## Notes

- Golden vectors are now in place and passing against real ecosystem artifacts. Keep them immutable and avoid regenerating them from code.
- Hash chain computation now supports explicit proof versions with default v0.2.0, which is the correct canonical direction.

## Do-Not-Touch

- Canonical JSON + hash chain semantics (v0.2.0) and the golden vector fixtures.
