# Case Study: What CodeGuard Caught on Our Own PR

We ran CodeGuard on a PR to our own infrastructure. Here's what happened.

## The change

PR #29 fixed three crashed services in our Railway deployment. Seven files changed. Config files, a shell script, JSON schemas. Routine infrastructure work.

Any team would have merged this in five minutes. The CI passed. The diff was clean. The commit message explained everything.

## What CodeGuard found

24 findings. Two hard blocks. Two conditions requiring human review. Twenty advisories.

The two hard blocks flagged our health-check script as touching "sensitive crypto code." False positive -- the script runs curl and pg_isready, nothing cryptographic. But the pattern match caught it because health checks sit in the security boundary.

The two conditions flagged our gateway config changes as "sensitive auth code modified." True positive. We removed Slack authentication tokens and changed device auth settings. Those ARE auth-sensitive changes. A human needed to verify the intent was correct.

The twenty advisories? Config changes touching security zones, auth references, database credentials, path traversal patterns. Every one traceable to a specific line in the diff.

## What would have happened without it

Without CodeGuard, this PR merges silently. Nobody asks whether removing auth tokens was intentional. Nobody flags that the gateway config now has different device auth settings. The review is "looks good, ship it."

With CodeGuard, the merge was BLOCKED until a human verified the auth changes were intentional. The evidence bundle captured every finding, every risk tier, every file touched.

## The real point

This wasn't a dangerous PR. The changes were correct. But that's exactly when governance matters most -- when the change looks routine and the risk hides in the config diff.

Your team approved 200 PRs last month. Can you prove which ones touched auth config? Can you reconstruct that decision in five minutes when the auditor asks?

Approved is not governed. Your auditor knows the difference.

---

Want to see what CodeGuard finds on your repo? I can run it on one of your public repos in 10 minutes.

David
cal.com/david-youssef
