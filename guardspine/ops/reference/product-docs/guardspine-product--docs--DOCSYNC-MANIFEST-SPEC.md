# guardspine.docs.yaml Manifest Specification v1.0

## Purpose

Every document managed by DocSync must have a manifest entry. No document gets
synced without one. This file is the control plane for the RLM-powered nightly
doc sync engine. If a document is not listed here, DocSync ignores it entirely.

## Schema

```yaml
docsync_version: "1.0"
documents:
  - doc_id: "unique-string-id"
    path: "relative/path/to/doc.md"
    mode: "spec" | "reality"
    coverage:
      paths:
        - "src/api/**/*.py"
        - "src/models/*.py"
      tags:
        - "authentication"
        - "authorization"
    allowed_updates:
      - "## API Reference"
      - "## Configuration"
    required_tests:
      - command: "pytest tests/api/"
        description: "API integration tests"
      - command: "npm test -- --grep auth"
        description: "Auth unit tests"
    owners:
      - "team-platform"
      - "jane@example.com"
    escalation_policy:
      on_violation: "L2"
      on_protected_section: "L3"
      on_test_failure: "L2"
    sync_schedule: "nightly"
    enabled: true
```

## Field Reference

### Top-Level Fields

| Field           | Type   | Required | Default | Description                             |
| --------------- | ------ | -------- | ------- | --------------------------------------- |
| docsync_version | string | Yes      | -       | Manifest schema version. Must be "1.0". |
| documents       | list   | Yes      | -       | Array of document entries.              |

### Document Entry Fields

| Field                                  | Type            | Required | Default      | Description                                                                                                                                                        |
| -------------------------------------- | --------------- | -------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| doc_id                                 | string          | Yes      | -            | Unique identifier for this document. Must be URL-safe (lowercase alphanumeric, hyphens). Example: "api-auth-reference".                                            |
| path                                   | string          | Yes      | -            | Relative path from repo root to the document file. Example: "docs/api/auth.md".                                                                                    |
| mode                                   | string          | Yes      | -            | Either "spec" or "reality". Controls sync direction. See Modes Explained below.                                                                                    |
| coverage                               | object          | Yes      | -            | Defines which source files and semantic tags this document covers.                                                                                                 |
| coverage.paths                         | list of strings | Yes      | -            | Glob patterns relative to repo root. Matched files are considered covered by this document. Example: ["src/api/**/*.py"].                                          |
| coverage.tags                          | list of strings | No       | []           | Semantic tags that match code annotations or comments. Example: ["authentication"].                                                                                |
| allowed_updates                        | list of strings | No       | []           | Section headings the AI may edit without elevated approval. All other sections are protected. Example: ["## API Reference"]. If empty, all sections are protected. |
| required_tests                         | list of objects | No       | []           | Tests that must pass before any sync-generated change is merged.                                                                                                   |
| required_tests[].command               | string          | Yes      | -            | Shell command to execute. Example: "pytest tests/api/".                                                                                                            |
| required_tests[].description           | string          | Yes      | -            | Human-readable description of what this test validates.                                                                                                            |
| owners                                 | list of strings | No       | []           | Team names or email addresses responsible for this document. Used for notifications and approval routing.                                                          |
| escalation_policy                      | object          | No       | See defaults | Controls risk tier assignment for different events.                                                                                                                |
| escalation_policy.on_violation         | string          | No       | "L2"         | Risk tier when spec mode detects code violating the document.                                                                                                      |
| escalation_policy.on_protected_section | string          | No       | "L3"         | Risk tier when a change touches a protected section (not in allowed_updates).                                                                                      |
| escalation_policy.on_test_failure      | string          | No       | "L2"         | Risk tier when required_tests fail after a proposed change.                                                                                                        |
| sync_schedule                          | string          | No       | "nightly"    | When DocSync checks this document. One of: "nightly", "on-pr", "manual".                                                                                           |
| enabled                                | boolean         | No       | true         | Set to false to temporarily disable syncing without removing the entry.                                                                                            |

### sync_schedule Values

| Value   | Behavior                                                                          |
| ------- | --------------------------------------------------------------------------------- |
| nightly | DocSync checks this document once per night on the configured cron schedule.      |
| on-pr   | DocSync checks this document whenever a PR touches files matching coverage.paths. |
| manual  | DocSync only checks this document when explicitly triggered via CLI or API.       |

## Modes Explained

### spec mode

The document IS the source of truth. Code that contradicts the document is a
violation. DocSync raises violations (not doc PRs) when mismatches are found.

Use spec mode for:

- API contracts and endpoint definitions
- Security policies and access control rules
- Data model schemas that external consumers depend on
- Compliance documentation

When DocSync detects a mismatch in spec mode, it:

1. Creates a violation report with the specific divergence
2. Assigns the risk tier from escalation_policy.on_violation
3. Notifies owners
4. Does NOT propose changes to the document

### reality mode

The code IS the source of truth. When the document is outdated, DocSync
proposes a PR to update the document with citations pointing to the code
that changed.

Use reality mode for:

- README files
- Architecture overview documents
- Developer guides and tutorials
- Internal process documentation

When DocSync detects a mismatch in reality mode, it:

1. Identifies which code changes caused the divergence
2. Generates a doc update PR with inline citations
3. Limits edits to allowed_updates sections (or flags for owner review)
4. Runs required_tests before marking the PR as ready

## Coverage Rules

### paths

Glob patterns relative to the repository root. Standard glob syntax applies:

- `*` matches any file in a single directory
- `**` matches across directory boundaries
- `?` matches a single character
- `{a,b}` matches either a or b

Examples:

```yaml
coverage:
  paths:
    - "src/api/**/*.py" # All Python files under src/api/
    - "src/models/user.py" # A specific file
    - "src/auth/*.{py,ts}" # Python and TypeScript in src/auth/
    - "config/security/**" # Everything under config/security/
```

### tags

Semantic tags that match annotations in source code. DocSync scans covered
files for tag markers in comments. The marker format is:

```python
# @docsync-tag: authentication
```

```typescript
// @docsync-tag: authorization
```

A document covers a file if the file matches any path glob OR contains any
listed tag. Tags provide a secondary, content-based coverage mechanism for
cross-cutting concerns that span many directories.

## Escalation Matrix

| Event                    | Default Tier | Override Field                         | Description                                           |
| ------------------------ | ------------ | -------------------------------------- | ----------------------------------------------------- |
| Spec violation           | L2           | escalation_policy.on_violation         | Code contradicts a spec-mode document                 |
| Protected section change | L3           | escalation_policy.on_protected_section | AI attempted to edit a section not in allowed_updates |
| Test failure             | L2           | escalation_policy.on_test_failure      | required_tests failed after proposed change           |
| New undocumented API     | L1           | -                                      | Code introduces a new API with no covering document   |

### Risk Tier Definitions

| Tier | Meaning     | Response                                                            |
| ---- | ----------- | ------------------------------------------------------------------- |
| L1   | Low risk    | Automated notification to owners. May auto-merge if tests pass.     |
| L2   | Medium risk | Requires at least one owner approval before merge.                  |
| L3   | High risk   | Requires explicit approval from all listed owners. Blocks pipeline. |

## Validation Rules

DocSync validates the manifest on load and rejects it if:

1. docsync_version is missing or not a supported version.
2. Any doc_id is duplicated across entries.
3. Any doc_id contains characters other than lowercase letters, digits, and hyphens.
4. Any path points to a file that does not exist (warning, not hard failure).
5. mode is not one of "spec" or "reality".
6. sync_schedule is not one of "nightly", "on-pr", or "manual".
7. required_tests entries are missing command or description.
8. coverage.paths is empty (every document must cover at least one path).

## Examples

### Example 1: API Reference in spec Mode

The API auth document is the source of truth. Any code that deviates from the
documented endpoints is a violation.

```yaml
- doc_id: "api-auth-reference"
  path: "docs/api/authentication.md"
  mode: "spec"
  coverage:
    paths:
      - "src/api/auth/**/*.py"
      - "src/api/middleware/auth.py"
    tags:
      - "authentication"
      - "jwt"
  allowed_updates:
    - "## API Reference"
    - "## Request Examples"
  required_tests:
    - command: "pytest tests/api/test_auth.py -v"
      description: "Auth endpoint integration tests"
    - command: "pytest tests/api/test_jwt.py -v"
      description: "JWT token validation tests"
  owners:
    - "team-security"
    - "alice@example.com"
  escalation_policy:
    on_violation: "L3"
    on_protected_section: "L3"
    on_test_failure: "L2"
  sync_schedule: "on-pr"
  enabled: true
```

### Example 2: Architecture Overview in reality Mode

The code is the source of truth. When the architecture changes, DocSync
proposes a PR to update the overview document.

```yaml
- doc_id: "architecture-overview"
  path: "docs/architecture/overview.md"
  mode: "reality"
  coverage:
    paths:
      - "src/**/*.py"
      - "src/**/*.ts"
    tags:
      - "architecture"
  allowed_updates:
    - "## Component Overview"
    - "## Data Flow"
    - "## Dependencies"
  required_tests:
    - command: "python scripts/validate_arch_diagrams.py"
      description: "Validate architecture diagram references"
  owners:
    - "team-platform"
  escalation_policy:
    on_violation: "L1"
    on_protected_section: "L2"
    on_test_failure: "L1"
  sync_schedule: "nightly"
  enabled: true
```

### Example 3: Security Policy with Strict Escalation

A compliance-critical document where every section is protected (no
allowed_updates) and all escalation tiers are set to L3.

```yaml
- doc_id: "security-policy"
  path: "docs/security/access-control-policy.md"
  mode: "spec"
  coverage:
    paths:
      - "src/auth/**/*.py"
      - "src/rbac/**/*.py"
      - "config/security/**"
    tags:
      - "security"
      - "rbac"
      - "compliance"
  allowed_updates: []
  required_tests:
    - command: "pytest tests/security/ -v"
      description: "Full security test suite"
    - command: "python scripts/check_rbac_consistency.py"
      description: "RBAC policy consistency check"
    - command: "bandit -r src/auth/ src/rbac/"
      description: "Static security analysis"
  owners:
    - "team-security"
    - "ciso@example.com"
  escalation_policy:
    on_violation: "L3"
    on_protected_section: "L3"
    on_test_failure: "L3"
  sync_schedule: "on-pr"
  enabled: true
```
