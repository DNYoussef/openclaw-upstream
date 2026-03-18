# LinkedIn Post Draft: Free GitHub Action announcement

**Account:** David Youssef (personal)
**Type:** Product-as-value announcement
**Target time:** 8-9am ET

---

We ran our own GitHub Action on a PR last week.

7 files changed. Config updates. A shell script. Routine infrastructure work.

It found 24 issues. Two hard blocks. Two conditions requiring human sign-off. Twenty advisories across auth, security, and database zones.

The PR was correct. The changes were intentional. But the Action caught that we modified authentication tokens and gateway security settings without explicit review.

Without it, that PR merges in five minutes. Nobody asks if removing auth tokens was on purpose.

Here's the thing: the Action is free.

codeguard-action. Open source. Install on any repo in 2 minutes. It risk-classifies every PR, runs AI code review, and produces a signed evidence bundle.

Not a SaaS trial. Not a "book a demo first." Just a GitHub Action you add to your workflow file.

Link in comments.

Run it on your repo. See what it catches.

Evidence over opinions. Every time.

#CodeGovernance #DevSecOps #OpenSource

---

**Slop audit:** PASS
**Hook quality:** uncomfortable_truth (our own PR had issues)
**Word count:** 148
**CTA:** Install link in comments (low friction)
