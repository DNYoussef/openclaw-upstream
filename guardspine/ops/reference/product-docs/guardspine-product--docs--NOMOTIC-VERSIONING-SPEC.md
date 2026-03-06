# Nomotic Policy Pack Versioning Specification

**GS-N1** -- Making policy packs versionable like code.

> "GuardSpine governs its own rules with the same rigor it governs code."

---

## 1. Overview

Policy packs are YAML files that define governance rules, blindness checks,
maturity models, and quality thresholds. Changes to these packs carry the
same risk as changes to production code -- a mis-configured severity level
or a removed rule can silently disable an entire class of governance checks.

This specification defines a version-control layer on top of
`nomotic_loader.py` so that every policy change is:

- **Versioned** with semantic versioning (semver)
- **Diffed** at the field level against the prior version
- **Reviewed** through a pull-request workflow with named approvers
- **Rolled out** gradually: shadow -> warn -> enforce
- **Reversible** via parent-version rollback
- **Evidenced** with an immutable bundle proving the review occurred

---

## 2. Version Lifecycle

Every pack version moves through a fixed sequence:

```
draft  -->  shadow (7 days)  -->  warn (7 days)  -->  enforce
                                                        |
                                                        v
                                                   deprecated (on rollback)
```

| Status     | Behavior                                              |
| ---------- | ----------------------------------------------------- |
| draft      | Not active. Under construction or awaiting PR review. |
| shadow     | Active in observation mode. Violations are logged but |
|            | do not block. Minimum 7 days before advancing.        |
| warn       | Active in warning mode. Violations produce warnings   |
|            | surfaced to operators. Minimum 7 days.                |
| enforce    | Active in enforcement mode. Violations block actions  |
|            | and require remediation.                              |
| deprecated | No longer active. Replaced by a newer version or      |
|            | rolled back.                                          |

The graduated rollout exists to catch unintended consequences before a
policy change can block production work.

---

## 3. Pull-Request Workflow

Policy changes follow a code-review model:

```
create PR  -->  reviewers approve/reject  -->  merge  -->  shadow rollout
```

### 3.1 Creating a PR

A PR links two versions: the currently-enforced version (`from_version_id`)
and the proposed replacement (`to_version_id`, in `draft` status). The PR
includes a computed diff showing every field-level change.

### 3.2 Review

Each PR declares a list of `required_approvers`. Approvers record an
approval or rejection with a rationale string. The PR auto-advances to
`approved` status once every required approver has signed off.

### 3.3 Merge

Merging an approved PR:

1. Sets the target version status from `draft` to `shadow`.
2. Creates an **evidence bundle** reference (`evb-{id}`) proving that
   the change was reviewed and approved by the required parties.
3. Sets the PR status to `merged`.

### 3.4 Rejection

If any reviewer rejects, the PR moves to `rejected` status. The author
can create a new version and open a fresh PR.

---

## 4. Diff Format

Diffs are computed recursively over the YAML structure using dotted paths:

| Change Type | Example Path                     | Meaning                     |
| ----------- | -------------------------------- | --------------------------- |
| added       | `rules.NOM-010`                  | New rule added              |
| modified    | `rules.NOM-003.severity`         | Severity changed            |
| removed     | `thresholds.max_blindness`       | Threshold key removed       |
| added       | `rules.NOM-001.anti_patterns[3]` | New anti-pattern at index 3 |

Each `PackChange` record contains:

- `change_type`: "added", "modified", or "removed"
- `path`: dotted path with bracket notation for list indices
- `old_value`: previous value (None if added)
- `new_value`: new value (None if removed)

---

## 5. Rollback

To revert a policy change:

1. The current version is set to `deprecated`.
2. Its `parent_version_id` is looked up and set to `enforce`.

This instantly restores the previous policy behavior. The deprecated
version and its PR remain in storage for audit purposes.

Rollback requires that a parent version exists. The root version of a
pack (the first version ever created) cannot be rolled back.

---

## 6. Evidence Bundles

Every merged PR produces an evidence bundle ID (`evb-{hex}`). This ID
references the proof that:

- A diff was computed and presented to reviewers
- All required approvers explicitly approved with rationale
- The merge was executed by an authorized actor
- Timestamps are recorded at each step

Evidence bundles integrate with the broader GuardSpine evidence system
(`common/evidence.py` and `common/doc_evidence_pack.py`) to provide a
complete audit trail.

---

## 7. Meta-Governance

This versioning system applies GuardSpine's own governance principles to
its governance rules:

- **No silent changes**: Every policy modification is diffed and reviewed.
- **Graduated rollout**: Shadow and warn periods catch mistakes before
  enforcement.
- **Accountability**: Named approvers with rationale strings.
- **Reversibility**: One-step rollback to parent version.
- **Evidence**: Immutable proof of review for compliance audits.

The same rigor that GuardSpine applies to user code is applied to the
rules that define that rigor. Policy packs are governed artifacts.

---

## 8. Data Model Summary

```
PackVersion
  version_id    str          unique identifier
  pack_id       str          which policy pack
  version       str          semver (e.g. "1.2.0")
  parent_version_id  str?    previous version (for rollback)
  created_at    str          ISO-8601
  created_by    str          author identity
  changelog     str          human description of changes
  status        str          draft|shadow|warn|enforce|deprecated

PackDiff
  diff_id       str          unique identifier
  from_version  str          source version ID
  to_version    str          target version ID
  changes       list         list of PackChange
  created_at    str          ISO-8601

PackChange
  change_type   str          added|modified|removed
  path          str          dotted path
  old_value     any          previous value
  new_value     any          new value

PackPR
  pr_id         str          unique identifier
  pack_id       str          which policy pack
  from_version_id  str       base version
  to_version_id    str       proposed version
  title         str          short summary
  description   str          detailed rationale
  diff          PackDiff     computed changes
  status        str          open|approved|rejected|merged
  required_approvers  list   list of approver identities
  approvals     list         list of approval/rejection records
  evidence_bundle_id  str?   set on merge
  created_at    str          ISO-8601
  created_by    str          PR author
```

---

## 9. File Locations

| File                              | Purpose                          |
| --------------------------------- | -------------------------------- |
| `common/nomotic_versioning.py`    | Version manager and data classes |
| `common/nomotic_diff.py`          | Deep diff utility                |
| `common/nomotic_loader.py`        | Pack loading (existing)          |
| `docs/NOMOTIC-VERSIONING-SPEC.md` | This specification               |
