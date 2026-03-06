# openclaw-upstream audit (2026-02-03)

## Scorecard (0-10)

- Contract correctness: 5
- Boundary hygiene: 6
- Test quality: 5
- Operational safety: 6
- Complexity / maintainability: 5

## P0 findings (breaks contract or critical security)

- None identified in the audited surfaces.

## P1 findings (interop drift, platform gaps, or reliability risks)

- Windows support is effectively partial: core build/test paths rely on bash scripts (e.g., `pnpm build` uses `bash scripts/bundle-a2ui.sh`), and onboarding explicitly warns that native Windows is untested. This makes native Windows installs fragile and non-deterministic without WSL2. (`package.json:91,149`, `scripts/bundle-a2ui.sh:1-2`, `src/commands/onboard.ts:63-68`)
- A critical onboarding test is skipped on Windows because config writes can be dropped in that flow, which means a real production path is not validated on Windows. This indicates unresolved platform-specific I/O or mocking behavior. (`src/commands/onboard-non-interactive.gateway.test.ts:216-231`)
- Hook events are effectively unversioned at the API surface: hooks only declare `events: string[]` with no schema/version contract. For downstream integrations (like OpenClaw hardening/GuardSpine), this means upstream changes can silently break external consumers. (`src/hooks/types.ts:10-67`)

## P2 findings (quality, coverage, and tooling concerns)

- Windows CI runs Vitest with `--dangerouslyIgnoreUnhandledErrors` and reduced parallelism. This is a pragmatic stability hack but risks masking real failures and making Windows-only regressions invisible. (`scripts/test-parallel.mjs:32-34,54-66`)
- Large surface areas are explicitly excluded from unit coverage (gateway/server methods, cli entrypoints, agent integrations, channels, UI flows). This is documented, but it increases the risk that regressions in high-impact areas slip past CI. (`vitest.config.ts:45-101`)
- Local Windows runs default to worker counts derived from CPU without a low-memory guardrail; given prior OOMs in related repos, this can be a recurring issue on Windows machines. (`vitest.config.ts:9-23`, `scripts/test-parallel.mjs:40-47`)

## Concrete fixes (downstream-only)

- Add a documented Windows-safe build path: either provide PowerShell equivalents for `bash` scripts (e.g., `bundle-a2ui.ps1`) or gate `pnpm build` with an explicit WSL requirement and a clear error message.
- Fix the Windows config write flake by isolating config mocks in tests (or by injecting a real config IO in this flow, as noted in the test itself) and remove the Windows skip once stable.
- Version hook event payloads (or provide a JSON schema) and document them as part of the plugin/automation contract. A minimal schema version in `HookSnapshot` or hook frontmatter would reduce downstream breakage risk.
- Add a low-memory test profile (`OPENCLAW_TEST_WORKERS=1`, `--no-file-parallelism`) for Windows local runs and document it in README or CONTRIBUTING.

## Interop risk statement

OpenClaw upstream is the host platform for GuardSpine/OpenClaw integrations. The current hook/event surfaces are not explicitly versioned, and Windows support is acknowledged as unstable. Without a versioned contract for hook events, upstream changes can silently break downstream integrations (including evidence capture/hardening). Stabilizing hook schemas and tightening Windows reliability are the highest leverage interop fixes.

## Skeptical Annex (assumptions and gaps)

- Assumption: GuardSpine integration depends on OpenClaw hook/event payloads or tool-call surfaces. This audit did not trace the full OpenClaw hardening plugin path inside this repo.
- Not validated: end-to-end Windows onboarding or gateway startup (audit based on code and tests only).
- False positive risk: some Windows issues are intentionally out-of-scope if WSL2 is the only supported path. If Windows native support is explicitly unsupported, downgrade those P1s but add clear documentation.
- Missing artifacts: no live protocol/schema diff was performed for gateway or hooks; versioning risk is inferred from type definitions and docs, not runtime telemetry.
