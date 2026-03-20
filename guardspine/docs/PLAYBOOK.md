# GuardSpine Playbook

> Standard operating procedures. No theory. Just what to do, when, and how.
> Updated: 2026-03-18

---

## 1. Outreach SOP

### Target Selection

Pick prospects with ALL FIVE characteristics:

1. GitHub-centered workflow
2. Meaningful PR volume
3. AI-assisted coding adoption (Copilot, Cursor)
4. Compliance or audit pressure (SOC 2, HIPAA, finance regulation)
5. Engineering maturity to install GitHub Actions

### Pain Bucket Classification

Assign exactly ONE per prospect:

| Bucket                       | Signal                                         | Example Trigger                         |
| ---------------------------- | ---------------------------------------------- | --------------------------------------- |
| review_velocity_gap          | PR volume outpaces review capacity             | "We ship 200 PRs/week with 3 reviewers" |
| evidence_chain_gap           | Approval trail won't survive an auditor        | SOC 2 prep, recent audit findings       |
| semantic_governance_gap      | Risky changes get same treatment as typo fixes | No CODEOWNERS, flat review policy       |
| authorization_provenance_gap | Can't prove who authorized what                | Compliance hiring, audit mentions       |
| regulatory_readiness_gap     | Can't answer auditor questions under pressure  | Finance/health/gov sector               |

### Message Template (70-150 words)

Four parts, in order:

1. **Hook** (1-2 sentences): A specific fact about THEIR company or role. Must pass the swap test -- could not be sent to anyone else.
2. **Pain bridge** (1-2 sentences): Hypothesize their struggling moment in second person. "You're probably seeing X..." or "When Y happens..."
3. **Value prop** (1-2 sentences): Risk-tiered diff governance. Be concrete. Name the pain bucket.
4. **CTA** (1 sentence): Exactly one low-friction ask. Pick from:
   - working_session: "Want to walk through one repo together?"
   - repo_pilot: "Can I run our action on one of your public repos and show you what it finds?"
   - evidence_walkthrough: "I can show you what a governed PR trail looks like in 10 minutes."
   - control_gap_review: "Want me to map where your current review process has evidence gaps?"

Sign off with just "David" -- no title, no company name, no links.

### Follow-Up Timing

- First follow-up: 3-5 business days after initial message
- Second follow-up: 7-10 business days after first follow-up
- After 2 follow-ups without response: mark as "cancelled." Don't chase.
- Never send the same template to two people at the same company.

### Pre-Flight Checklist (MANDATORY for external sends)

Before sending any email or DM:

1. Present the send plan: recipient, email, subject, first 3 lines, attachments
2. Get explicit "send" approval from David
3. Verify attachments match promises in the body
4. Verify email addresses (HIGH confidence = OK, MEDIUM = flag, LOW = don't send)
5. Complete all requested audits BEFORE sending

Cold emails to prospects are one-shot. Bounced email = burned impression. No fixing after send.

---

## 2. Content SOP

### LinkedIn Post -- David's Account (Hot Take)

- Post time: 8-9 AM ET
- ONE uncomfortable truth per post
- First person, confrontational
- Max 200 words
- Structure: Hook -> Problem -> Insight -> CTA
- Max 3 hashtags: #DevSecOps #CodeGovernance + rotate a third
- CTA: cal.com/david-youssef
- End with a manifesto line, not just a CTA

**Hook rules (Joel Smith method):**

- Lead with an uncomfortable truth the reader agrees with privately but hasn't seen anyone say
- Bad: "AI code governance is becoming important"
- Good: "Most code review in 2026 is a rubber stamp. Everyone knows it. Nobody says it."

### LinkedIn Post -- GuardSpine Account (Educational)

- Post time: 11 AM-12 PM ET
- Educational, factual, product-specific
- "Here's what it does" not "here's why you should care"
- Shorter than David's posts
- Max 3 hashtags: #CodeGovernance #DevSecOps + one topic-specific
- CTA: guardspine.com

### Newsletter (Biweekly)

- 800-1200 words
- Curate from week's LinkedIn posts + 1 new insight + 1 proof point
- CTA: cal.com/david-youssef
- Week rotation:
  - Week 1: "Why AI code governance is not code review"
  - Week 2: XZ Utils proof case
  - Week 3: BYOK architecture deep dive
  - Week 4: PE/enterprise adoption patterns

### Case Study ("Caught It" Format)

- Real example of codeguard-action finding a risk in a PR
- Structure: what was the change, what did codeguard catch, what would have happened without it
- Include actual evidence bundle data (risk tier, consensus, findings)
- This IS the lead magnet AND the validation proof point

### Lead Magnet

- Max 1500 words, 6th grade reading level
- Story-driven, not listicle
- Must create the next problem GuardSpine solves
- Gate behind LinkedIn comment ("Comment X to get this")
- CTA: cal.com/david-youssef

---

## 3. Sales SOP

### Discovery Call Structure (from Kristen meeting insights)

1. **Open** (2 min): "Tell me about your current code review process."
2. **Struggling moment** (5 min): Find the pain. "What happens when an auditor asks how you governed a specific change?" "How many PRs get real scrutiny vs rubber-stamp approval?"
3. **Current state** (5 min): "What tools do you use? GitHub native? Third-party scanner? Manual checklists?"
4. **Gap identification** (5 min): Map their process to the pain buckets. Name the gap.
5. **Show, don't tell** (10 min): Run codeguard-action on one of their repos (or a similar public repo). Show the evidence bundle. Show the PR comment.
6. **Close** (3 min): One next step. "Can I set this up on one repo and show you what it finds over a week?"

### Objection Handling

| Objection                           | Response                                                                                                                                                                          |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| "We already do code review"         | "Review is not governance. Can you reconstruct the story of any change -- who approved, what they saw, what they missed -- in under 5 minutes?"                                   |
| "GitHub CODEOWNERS is enough"       | "CODEOWNERS proves who clicked approve. It doesn't prove they saw the auth logic change in line 47."                                                                              |
| "We don't have compliance pressure" | "Yet. AI-generated code is 40%+ of new commits at most companies. Regulators are watching. The question is whether you build the evidence trail before or after they ask for it." |
| "We'll build it ourselves"          | "You could. It's about 6 months of work for multi-model deliberation, risk tiering, evidence signing, and consensus logic. Or you install a GitHub Action in 5 minutes."          |
| "What if the AI review is wrong?"   | "That's why we use multi-model consensus with provenance. If one model misses something, the others catch it. And every decision is signed and auditable."                        |

### Positioning Rules

- Never describe architecture before establishing pain
- Never pitch in the first message. Earn the right to explain.
- Frame as "code governance" not "code review" -- review is what they already think they're doing
- "Proportional" is the key differentiator. Not everything gets the same treatment.

---

## 4. Operations SOP

### Deployment Procedure

```bash
# 1. Link Railway service
railway link -p PROJECT_ID -s SERVICE_NAME -e production

# 2. Deploy from subdirectory (NEVER from repo root -- OOM crash)
cd guardspine/<service-dir>/
railway up --detach

# 3. Verify
curl http://<service>.railway.internal:<port>/health
# Then verify the specific fix
```

NEVER claim a fix is done until verified against the LIVE system.
`Coded != Deployed != Verified`

### Morning Briefing

David opens Claude Code and says "morning brief." The system:

1. Reads today's calendar events (Google Calendar MCP)
2. Classifies each: build | content | outreach | admin | review | meeting | personal
3. For claude_execute/claude_prepare blocks: identifies data sources, preps materials
4. Flags blockers (missing files, pending PRs, keys not set)
5. Estimates evidence output per block

Output: `TIME - EVENT - TYPE - PREP STATUS - EVIDENCE TARGET`

### Monitoring Check

1. Check Railway dashboard for service status
2. Hit /health on each core service
3. Check n8n execution history (GET /api/v1/executions?limit=10)
4. Query telemetry: `POST /query {"query_name": "recent_telemetry", "params": {"limit": 20}}`
5. Check agent heartbeats: `POST /query {"query_name": "agent_heartbeats", "params": {"hours": "24 hours"}}`

### Workflow Debugging

Before touching any n8n workflow, check LEARNINGS.md. The same mistakes have been made before.

Key gotchas:

- Code nodes CANNOT use $env.\* -- hardcode Railway internal URLs
- POST body needs specifyBody: 'json' + jsonBody field
- Parallel node connections cause race conditions -- chain sequentially
- PUT workflow updates reset cron timers -- deactivate/activate after PUT
- Credential names must match exactly -- check GET /api/v1/credentials

### Block Wrap-Up

After each calendar block, David says "wrap up [event name]." The system:

1. Checks git log for commits since block start
2. Checks test results if applicable
3. Writes to evidence journal: `Desktop/guardspine/evidence-journal/daily/{date}.md`
4. Stores observation via memory-mcp

### Weekly Review (Friday)

1. **Block Completion Audit**: Every calendar block from the week accounted for (done/skipped/deferred)
2. **Content Performance**: What shipped, what's in queue, draft 3 posts if queue < 3
3. **Hormozi Evidence Journal**: One paragraph: "What evidence did I produce this week that GuardSpine will succeed?"
4. **Template Refinement**: Which calendar descriptions worked, which needed mid-block clarification

---

## 5. Voice Rules

### David's Writing Style

- First person. Expert informed. Direct assertive.
- Contractions always (doesn't, isn't, can't, won't)
- Short sentences. Fragments OK. White space between every thought.
- Trust the reader. Don't explain things they already know.
- Specific numbers over vague quantities ("116 contributors, one DevOps engineer" not "most teams")
- Name real frameworks, real companies, real people
- Ask questions that make the reader uncomfortable
- Personal admissions build trust ("I've made this mistake myself")
- Lead with THEIR struggling moment, not YOUR credentials
- Make the reader feel seen, not lectured
- End with a manifesto line, not just a CTA
- Uses dashes for asides
- Never uses semicolons
- Rarely uses exclamation marks
- Leads with "the short version" or "honest answer"
- Asks for correction ("Am I reading this right?")
- Admits what isn't working

---

## 6. Banned Slop Words (36+)

### Instant Rejection (never use)

delve, tapestry, multifaceted, underscore, cornerstone, testament,
paradigm, synergy, holistic, myriad, plethora, embark, leverage,
utilize, facilitate, robust, seamless, empower, transformative,
groundbreaking, cutting-edge, proactive, impactful, actionable,
insightful, nuanced, pivotal, realm, foster, endeavor, intricate,
paradigm shift, game-changing, revolutionize, journey, vibrant,
beacon, spearhead, underpin, harness (as verb meaning "use"), elevate,
supercharge, unlock, disruptive, scalable, ecosystem, innovative,
streamline, compelling

### Banned Phrase Patterns

- "In today's ever-evolving/fast-paced/digital/modern..."
- "It's worth noting that..."
- "It's important to note/remember/consider..."
- "One could argue that..."
- "At its core..."
- "In the realm of..."
- "plays a crucial/vital/key/pivotal role"
- "a testament to"
- "serves as a reminder/beacon/foundation"
- "shaping/reshaping the future/landscape/way"
- "take/have taken X to new/the next level"
- "In conclusion/summary"
- "As we navigate/move forward/look ahead"
- "not just X, but also Y"
- "Whether X or Y, one thing is/the fact remains"

---

## 7. CTA Rules

- David posts: cal.com/david-youssef
- GuardSpine posts: guardspine.com
- Vary CTAs. Don't use the same template every post.
- Never say "pilot program" -- say "partnership" or "work together on a repo"
- Never say "AI governance platform" -- say "code governance"
- Never say "compliance automation"
- Never describe architecture before establishing pain
- One ask per message. Never two CTAs.

---

## 8. Adapt Technical Depth to Recipient

| Persona            | Technical Depth                                       | Content Focus                  |
| ------------------ | ----------------------------------------------------- | ------------------------------ |
| Engineer/Developer | FULL -- component counts, architecture, stack details | Infrastructure, code, systems  |
| Executive/CISO     | MINIMAL -- business outcomes only                     | Value, risk, ROI               |
| Advisor/Connector  | MODERATE -- high-level technical + business           | Framing, patterns, positioning |

---

## 9. EU-Specific Rules

- Simplified surname format for Nordic/European email addresses: `first.married@domain` not `first.middle.last@domain`
- Verify email before sending to ex-employees (check current employer first)
- Document legitimate interest basis before drafting for EU contacts
- LinkedIn personalized invitation notes limited to ~3 per week -- prioritize top prospects
