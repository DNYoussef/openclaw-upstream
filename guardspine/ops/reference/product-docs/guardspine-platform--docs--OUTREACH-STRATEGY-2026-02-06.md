# CodeGuard Action - Proactive Outreach Strategy

> Generated: 2026-02-06
> Target: Developers/maintainers complaining about AI-generated code review burden

---

## The Landscape (Feb 2026)

The problem CodeGuard solves is the #1 developer pain point right now:

- GitHub is building a PR kill switch because maintainers are drowning
- curl, Ghostty, tldraw have banned AI PRs entirely
- Only 1 in 10 AI PRs meet quality standards (Xavier Portilla Edo, Voiceflow)
- AI code creates 1.7x more issues than human code (CodeRabbit research)
- PRs are 18% larger with AI, incidents per PR up 24%
- RedMonk coined it "AI Slopageddon"
- Academic research confirms AI decreases experienced dev productivity by increasing tech debt (arXiv 2510.10165)

---

## Target Personas

### Tier 1: High-Profile Maintainers (Public Pain)

| Person             | Project                    | Their Pain                                            | Source  |
| ------------------ | -------------------------- | ----------------------------------------------------- | ------- |
| Daniel Stenberg    | curl                       | Ended bug bounty - "death by a thousand AI slops"     | RedMonk |
| Mitchell Hashimoto | Ghostty                    | Zero-tolerance ban, permanent ban for AI code         | RedMonk |
| Steve Ruiz         | tldraw                     | Auto-closes ALL external PRs now                      | RedMonk |
| Seth Larson        | Python Software Foundation | "Surest way to burn out maintainers"                  | RedMonk |
| Craig McLuckie     | Stacklok                   | "Good first issue now inundated with vibe coded slop" | RedMonk |

### Tier 2: GitHub Discussion #185387 Commenters

These people are actively asking for a solution.

| GitHub User                    | Pain Point                                      | CodeGuard Angle                         |
| ------------------------------ | ----------------------------------------------- | --------------------------------------- |
| @Mossaka (Azure Core)          | "Line-by-line review doesn't scale with AI PRs" | CodeGuard does the triage automatically |
| @xavidop (Voiceflow)           | Wants AI-detection with configurable thresholds | CodeGuard classifies risk L0-L4         |
| @sirosen                       | Wants to "chuck laptop into ocean" from AI spam | CodeGuard auto-filters low-quality      |
| @chadlwilson                   | Worried about undisclosed AI agents in PRs      | CodeGuard produces evidence trails      |
| @ThiefMaster                   | Frustrated by low-activity spam PRs             | CodeGuard's risk classification helps   |
| Camilla Moraes (GitHub PM)     | Opened the discussion - looking for solutions   | CodeGuard IS the solution               |
| Matthew Isabel (GitHub PM)     | "More PRs for maintainers to review than ever"  | CodeGuard reduces review load           |
| Jiaxiao (Joe) Zhou (Microsoft) | Review rigor vs sustainability tension          | Risk-proportional review solves this    |

### Tier 3: HN Commenters (Vocal, Technical)

| HN User        | Quote/Pain                                                                              | Thread                    |
| -------------- | --------------------------------------------------------------------------------------- | ------------------------- |
| ModernMech     | "786 AI-generated PRs accumulating without merging"                                     | AI code review bubble     |
| diogolsq       | "Code review has become the new bottleneck"                                             | AI code review bubble     |
| trjordan       | "You either become a bottleneck or rubber-stamp it"                                     | Comprehension debt        |
| fhd2           | "Terrified by what vibe coding did to PR quality"                                       | Mozilla Firefox repo      |
| kace91         | Can't review faster than AI generates                                                   | JetBrains Agentic         |
| yicmoggIrl     | "AI converts engineers into slop reviewers - burnout"                                   | OpenJDK thread            |
| regularfry     | "Thousands of lines generated daily"                                                    | Agentic coding thread     |
| radarsat1      | "User is nothing more than a spectator, a rubber stamp"                                 | AI Adoption Journey       |
| JambalayaJimbo | "Rubber stamp PRs have been the norm at every place I worked"                           | Evolution of Software Dev |
| flohofwoe      | "A blanket ban is the only sensible thing" (Zig maintainer)                             | Zig migration thread      |
| jemiluv8       | "LLMs make people feel they can code without understanding"                             | OSS maintainer thread     |
| ben_w          | "Vibe-coding quality and speed both insufficient"                                       | Opus 4.5 thread           |
| BeetleB        | "Whole point of vibe coding is letting LLM run loose with minimal quality checks"       | Vibe Code Warning         |
| fudged71       | "AI code compiles, runs, passes tests - but has no error handling, SQL injection vulns" | 3D printed aircraft       |
| sksisksbbs     | "Reviewing AI code is a slot machine"                                                   | AI Adoption Journey       |

---

## Where to Post/Engage

### Primary Targets (Open Now)

| #   | Platform | URL                                                  | Points/Comments       | Strategy                                 |
| --- | -------- | ---------------------------------------------------- | --------------------- | ---------------------------------------- |
| 1   | GitHub   | https://github.com/orgs/community/discussions/185387 | 500+ comments         | Direct solution pitch (most appropriate) |
| 2   | HN       | https://news.ycombinator.com/item?id=46766961        | 350pts / 247 comments | "There is an AI code review bubble"      |
| 3   | HN       | https://news.ycombinator.com/item?id=46884471        | Active                | "GitHub Ponders Kill Switch for PRs"     |
| 4   | HN       | https://news.ycombinator.com/item?id=46765120        | 329pts / 285 comments | "Vibe coding kills open source"          |

### Secondary Targets

| Platform  | Location                                           | Strategy                                     |
| --------- | -------------------------------------------------- | -------------------------------------------- |
| Reddit    | r/ExperiencedDevs                                  | Post about review automation for senior devs |
| Reddit    | r/opensource                                       | Maintainer-focused angle                     |
| Dev.to    | AI code review tools roundups                      | Get CodeGuard listed                         |
| Twitter/X | Reply to Daniel Stenberg, Mitchell Hashimoto posts | Short, empathetic, link to action            |

---

## Drafted Messages

### Message 1: GitHub Discussion #185387

Target: https://github.com/orgs/community/discussions/185387

```markdown
## Automated triage instead of blanket bans

I've been following this thread closely and the pattern is clear: maintainers
are choosing between "review everything manually" (burnout) and "ban all
external PRs" (killing contribution). Neither scales.

We've been building an open-source (MIT) GitHub Action called CodeGuard that
tries to solve the middle ground - automatic risk triage at the PR gate:

1. **Parses the unified diff** and detects what zones are touched (auth,
   payment, infra, etc.)
2. **Classifies risk L0-L4** automatically - an AI-generated typo fix (L0)
   doesn't need the same scrutiny as a change to your auth middleware (L3)
3. **Runs multi-model AI review** for L1+ changes - not one model that
   hallucinates, but 2-3 models that have to reach consensus
4. **Posts a structured summary to the PR** with findings, risk tier, and
   evidence
5. **Produces a hash-chained evidence bundle** - cryptographic proof of what
   was reviewed, when, and what the models found. Independently verifiable
   offline.

The key insight from @Mossaka's point about "line-by-line review not scaling
with AI PRs" - you don't need to review every PR the same way. You need to
know WHICH PRs need your attention. An L0 can be auto-merged with evidence.
An L4 needs a human. The 80% in between need triage, not banning.

This doesn't replace human judgment - it gives maintainers their time back by
filtering signal from noise before they ever open the diff.

Repo: github.com/DNYoussef/codeguard-action (MIT license)

Happy to answer questions or take feedback on what would make this more useful
for the specific problems discussed here.
```

---

### Message 2: HN - "There is an AI code review bubble"

Target: https://news.ycombinator.com/item?id=46766961

```
The article nails the core issue but I think misdiagnoses the solution space.

The problem isn't that AI code review exists - it's that current tools are
solving the wrong problem. They review code that humans wrote. The actual
crisis is reviewing code that AI wrote.

When AI increases code volume by 10x but reviewer count stays flat, you
don't need better review tools. You need risk triage. Not every PR deserves
the same attention:

- Typo fix to a README? L0. Auto-approve with an evidence log.
- New utility function with tests? L1. One model scans it, posts findings.
- Changes to auth middleware or payment flow? L3. Three models have to reach
  consensus before a human even looks at it.
- Production deployment config? L4. Models + mandatory human sign-off.

We've been building this (codeguard-action on GitHub, MIT licensed) - a
GitHub Action that classifies PR risk, runs multi-model review proportional
to that risk, and produces a cryptographic evidence bundle proving what was
checked. The evidence is hash-chained and independently verifiable offline
with a separate tool.

The point isn't to replace human reviewers. It's to stop burning them out
on L0-L1 changes so they have capacity for the L3-L4 ones that actually
matter.

The 786-PR-backlog problem mentioned upthread isn't a review problem. It's
a triage problem.
```

---

### Message 3: HN - "GitHub Ponders Kill Switch"

Target: https://news.ycombinator.com/item?id=46884471

```
A kill switch is treating symptoms. The disease is that maintainers have no
way to distinguish "AI-generated typo fix from a new contributor" from
"AI-generated rewrite of my auth system by someone who doesn't understand it."

Both show up as PRs. Both require manual triage. The kill switch treats them
identically by blocking both.

What maintainers actually need is automated risk classification at the gate.
We built a GitHub Action (codeguard-action, MIT) that does this:

- Parses the diff, identifies what zones are touched
- Classifies risk L0 through L4 based on what changed (not who submitted)
- Runs proportional AI review (1-3 models depending on risk tier)
- Posts structured findings to the PR
- Seals everything into a hash-chained evidence bundle

The "1 in 10 AI PRs is legitimate" stat from the GitHub discussion tells me
9 out of 10 could be auto-filtered before a maintainer ever sees them. That's
not a ban - it's triage.

Daniel Stenberg shouldn't have had to kill curl's bug bounty. He needed a
filter that could tell the difference between a real vulnerability report and
AI-generated noise. Risk classification solves this without shutting down the
program.
```

---

### Message 4: HN - "Vibe coding kills open source"

Target: https://news.ycombinator.com/item?id=46765120

```
The paper is right that vibe coding is creating an unsustainable burden on
OSS maintainers, but the proposed solutions (ban AI, restrict contributions)
are throwing the baby out with the bathwater.

Some AI-generated PRs are genuinely good. The problem is that maintainers
can't tell which ones without reading every line - and at current volumes,
that's impossible.

We've been working on this exact problem: a GitHub Action (MIT licensed)
that auto-triages PRs by risk level. It parses the diff, detects what
sensitive zones were touched (auth, payments, infra config), classifies
risk L0-L4, and runs multi-model AI review proportional to that risk.

The output is a structured comment on the PR plus a cryptographic evidence
bundle (hash-chained, independently verifiable). A maintainer can glance at
the risk tier and findings summary and decide in seconds whether this needs
their attention or not.

The goal isn't to automate away human judgment. It's to make sure human
judgment is spent on the PRs that actually need it, instead of being
exhausted on the 90% that don't.

codeguard-action on GitHub if anyone wants to try it.
```

---

## Posting Tips

1. **GitHub Discussion first** - most appropriate for a direct solution pitch, decision-makers are there
2. **HN: only post in ONE thread** - posting in multiple looks spammy. Pick the most active (AI code review bubble at 350pts is best)
3. **Wait for natural timing** - don't post all at once. GitHub first, HN a day or two later
4. **Engage with replies** - the real value comes from follow-up conversation
5. **Don't upvote your own posts** - HN detects and penalizes this
6. **Be genuine** - if someone pushes back, engage honestly. These communities respect authenticity

---

## Key Statistics to Reference

| Stat                                                      | Source                         |
| --------------------------------------------------------- | ------------------------------ |
| 1 in 10 AI PRs meet quality standards                     | Xavier Portilla Edo, Voiceflow |
| 18% larger PRs with AI adoption                           | CodeRabbit research            |
| Incidents per PR up 24%                                   | CodeRabbit research            |
| AI code creates 1.7x more issues                          | CodeRabbit State of AI report  |
| ~20% of curl bug bounty submissions were AI-generated     | Daniel Stenberg                |
| Only 5% of AI bug reports identified real vulnerabilities | Daniel Stenberg                |
| 30%+ of senior devs ship mostly AI-generated code         | Industry surveys               |
| Copilot PRs take 26% longer to review                     | Harness engineering            |
| AI decreases experienced dev productivity                 | arXiv 2510.10165               |

---

## Source URLs

- GitHub Discussion: https://github.com/orgs/community/discussions/185387
- RedMonk AI Slopageddon: https://redmonk.com/kholterhoff/2026/02/03/ai-slopageddon-and-the-oss-maintainers/
- The Register Kill Switch: https://www.theregister.com/2026/02/03/github_kill_switch_pull_requests_ai/
- HN AI Code Review Bubble: https://news.ycombinator.com/item?id=46766961
- HN Kill Switch Thread: https://news.ycombinator.com/item?id=46884471
- HN Vibe Coding Kills OSS: https://news.ycombinator.com/item?id=46765120
- CodeRabbit AI vs Human Report: https://www.coderabbit.ai/blog/state-of-ai-vs-human-code-generation-report
- arXiv AI Productivity Study: https://arxiv.org/abs/2510.10165
- Addy Osmani Code Review in AI Age: https://addyo.substack.com/p/code-review-in-the-age-of-ai
- Dev Genius Banning AI PRs: https://blog.devgenius.io/open-source-projects-are-now-banning-ai-generated-pull-requests-8e1dd3e8d41c
- Navendu AI Spam PRs: https://navendu.me/posts/ai-generated-spam-prs/
