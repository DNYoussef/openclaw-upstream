# GuardSpine 5-Minute Demo Script

For Eric intro and investor meetings.

## Minute 0-1: The Problem

Screen: GitHub PR with 200+ changed files.

"Your team shipped 47 PRs this week. 30 were AI-generated. How many
were actually reviewed?"

Show a rubber-stamped PR -- approved in under 2 minutes, 200+ files,
single thumbs-up from a dev in 3 other meetings.

"This is the governance gap. Someone approved this, but nobody reviewed
it. And your audit trail says it was reviewed."

## Minute 1-2: Install

Screen: GitHub Actions marketplace listing for codeguard-action.

Show marketplace page. Copy-paste the workflow YAML -- 12 lines.

"Two minutes. No infrastructure. No API keys from us -- you bring your
own models. Claude, GPT, Gemini, Ollama. We never see your code."

## Minute 2-3: Trigger

Screen: New PR with a deliberate security issue.

Push a PR with a hardcoded API key in config. GuardSpine Action fires
on PR open. Show Actions tab: AI models running in parallel. For L2
risk, two models review independently then cross-check. No human
assigned reviewers or wrote a checklist.

## Minute 3-4: The Judgment Receipt

Screen: PR comment with decision + evidence bundle JSON.
Show the BLOCK decision, findings, severity ratings. Open the bundle:

- Signer IDs and model names for each reviewer
- SHA-256 prompt hashes and response hashes
- Timestamps for each review round
- Consensus score and agreement metrics

"Court-admissible proof of what was reviewed, by whom, and what they
found. Edit it -- the hash chain breaks. Auditors verify offline."

## Minute 4-5: The Dashboard

Screen: GuardSpine UI.
Guard lane overview -- code lane active, data lane configured.
Audit trail timeline: every PR, every decision, every receipt.
Compliance report export -- one click, PDF or JSON.

"This is what your CISO sees. Every change, every decision, every
receipt. Tamper-proof. Exportable. No manual assembly."

## Closing Line

"Two minutes to install. Zero infrastructure cost. Court-admissible
governance for every code change. Questions?"

---

## Pre-Demo Checklist

- [ ] Test repo ready with clean history
- [ ] API keys loaded and verified (2+ providers)
- [ ] Security issue planted in branch ready to PR
- [ ] Dashboard populated with sample audit data
- [ ] Evidence bundle JSON formatted for readability
- [ ] Browser tabs pre-loaded: repo, Actions tab, dashboard
- [ ] Backup screen recording saved locally
- [ ] Font size 150%+ for screen sharing
- [ ] Practice run under 5 minutes at least twice
