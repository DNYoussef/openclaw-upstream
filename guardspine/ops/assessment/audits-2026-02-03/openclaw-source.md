# openclaw-source audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 6
- Test quality: 4
- Operational safety: 5
- Complexity / maintainability: 5

## P0 findings (breaks contract or critical security)

- None identified in the audited surfaces.

## P1 findings (interop drift, platform gaps, or reliability risks)

- Test suite is memory-bound in practice (Vitest worker OOMs reported in this environment). The test runner launches multiple suites and uses per-suite worker counts derived from CPU, with no low-memory guardrail. This makes CI/dev runs fragile on Windows and blocks verification. (`scripts/test-parallel.mjs:6-47`, `vitest.config.ts:9-23`)
- Windows support is effectively partial: build/test paths rely on bash scripts (`bundle-a2ui.sh`), and there is no Windows-native equivalent. This makes native Windows installs fragile without WSL2. (`package.json:88-89`, `scripts/bundle-a2ui.sh` in repo)
- Hook events are unversioned at the API surface: hooks declare `events: string[]` without a schema/version contract. Downstream integrations (GuardSpine hardening) can break silently on upstream changes. (`src/hooks/types.ts:10-67`)

## P2 findings (quality, coverage, and tooling concerns)

- Large surfaces are excluded from unit coverage (gateway/server methods, CLI entrypoints, agents, channels, UI). This is documented but increases regression risk in high-impact areas. (`vitest.config.ts:45-101`)
- Package overrides and dependency pins differ from upstream (e.g., tar override), which can cause subtle drift between this source copy and the upstream/hardening repos. If this is intended as a mirror, keep overrides synchronized. (`package.json:230-242`)

## Concrete fixes (downstream-only)

- Add a low-memory test profile for Windows/local runs (e.g., `OPENCLAW_TEST_WORKERS=1`, `--no-file-parallelism`, `NODE_OPTIONS=--max-old-space-size=8192`) and document it. Consider serializing suites on low-memory systems.
- Provide a Windows-safe build path or explicitly gate `pnpm build` with WSL-only messaging. If WSL is required, fail fast with a clear error.
- Version hook event payloads or publish a JSON schema so downstream integrations can pin to a stable contract.
- If this repo is a mirror of upstream, add a sync check or document the expected drift (dependency overrides, scripts, config).

## Interop risk statement

This repo is used as a source copy; without a memory-stable test path, it cannot reliably validate upstream changes. Combined with unversioned hook events, downstream integrations can drift without clear detection. Stabilizing tests and versioning hooks are the highest leverage changes.

## Skeptical Annex (assumptions and gaps)

- Assumption: the OOM issue reported in prior runs reflects the current state; no live test run was executed in this audit.
- Not validated: end-to-end Windows onboarding or gateway startup; audit is based on code inspection and prior failure reports.
- False positive risk: if this repo is not meant to be a strict mirror, dependency drift findings are advisory only.
- Missing artifacts: no runtime protocol diff or hook payload samples were captured.
