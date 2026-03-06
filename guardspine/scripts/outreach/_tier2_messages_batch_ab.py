"""Tier 2 message drafts from research agents - Batches A and B."""

tier2_messages = {
    # BATCH A
    'Steve Messina': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Steve. Building Heimdall around automated code vulnerability detection and supply chain security shows you see the same risk surface we do. GuardSpine is an open-source CI/CD layer where AI reviewers (Claude, GPT, Ollama) enforce compliance rubrics on every PR and produce cryptographically signed evidence bundles -- purpose-built for teams shipping AI-generated code at speed. Worth a look: https://github.com/DNYoussef/codeguard-action",
    },
    'Tim Wedande': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Tim. Saviynt's 2026 thesis -- that AI agents are identities requiring the same lifecycle controls as humans -- maps directly to something we're addressing at the code layer. GuardSpine puts AI reviewers inside the PR workflow, enforcing compliance rubrics and generating signed audit trails before AI-written code ever merges. Given your identity-first framing, this might be useful context: https://guardspine.ai",
    },
    'Berta Rodriguez-Hervas': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Berta. Your line about AI governance -- 'without trust, nothing scales' -- is exactly the constraint GuardSpine was built to remove. We put AI reviewers (Claude, GPT, Gemini) directly into the CI/CD pipeline, so every AI-generated PR gets a cryptographically signed compliance record before it ships. At Pfizer's scale, that audit trail matters: https://guardspine.ai",
    },
    'Leo Cullen': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Leo. Your focus on governance, interoperability, and accountability for enterprise AI lines up with a gap we're closing at the code layer. GuardSpine is an open-source CI/CD governance tool where AI reviewers enforce compliance rubrics on every PR and produce signed evidence bundles -- making AI code changes auditable by design, not retrofit. Might be worth a look: https://guardspine.ai",
    },
    'Erick Antezana': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Erick. Your work on semantic data governance and ontology at Bayer -- especially the recent push into MCP servers for scientific querying -- shows you're thinking about how AI tooling gets governed across R&D workflows. GuardSpine brings that same discipline to the code layer: AI reviewers enforce rubrics on every PR and produce signed audit records. Worth a look: https://guardspine.ai",
    },
    # BATCH B
    'Richard Schaefer': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Richard. Your work building Lunar Analytics on top of two decades architecting AI at the VA puts you in a rare position to understand what 'trustworthy AI in a regulated environment' actually requires. GuardSpine enforces compliance rubrics on every AI-generated PR, producing signed evidence bundles at the point of code change, not after deployment. For federal health AI, that paper trail matters. Details at https://guardspine.ai",
    },
    'Christos Varsakelis': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Christos. Leading AI/ML across all of Janssen's therapeutic areas means shipping models into one of the most scrutinized regulatory environments on earth -- FDA's 2025 draft guidance and the EU AI Act both treat high-risk pharmaceutical AI as requiring documented human oversight at every step. GuardSpine puts that oversight directly inside the PR workflow: AI reviewers enforce GxP-aligned rubrics and sign every decision cryptographically. You get an audit-ready evidence trail without adding process friction. Worth a look: https://guardspine.ai",
    },
    'Aaron Bennett': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Aaron. Shaping product strategy at the intersection of platform and cybersecurity means you spend a lot of time explaining to partners why governance isn't optional -- it's a sales accelerator. GuardSpine is an open-source CI/CD governance layer that gives AI-generated code a cryptographically signed compliance record on every PR, turning 'we have a review process' into verifiable proof. That kind of assurance shortens enterprise security reviews considerably. Relevant context: https://guardspine.ai",
    },
    'Varun Chhibber': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Varun. You've written that engineers building AI systems can't afford mistakes -- that framing resonates. At Elevance Health's scale, every AI-generated PR touching claims or clinical data is a liability if it slips past review. GuardSpine is a GitHub Action that routes each PR through multi-model AI reviewers (Claude, GPT, Gemini, Ollama) at L0-L4 risk tiers and produces a signed evidence bundle per decision. Drop it in a workflow in under an hour. Apache 2.0: https://github.com/DNYoussef/codeguard-action",
    },
    'Andreas Freund': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Andreas. Your work on the Baseline Protocol showed that zero-knowledge proofs can make multi-party business processes auditable without exposing underlying data -- the same principle applies to AI code review. GuardSpine cryptographically signs every AI reviewer's decision on a PR using prompt hash, response hash, and signer attestation, producing a tamper-evident evidence bundle. For anyone advising enterprises on GenAI governance, that's a concrete implementation to point clients at: https://github.com/DNYoussef/codeguard-action",
    },
}

for name, data in tier2_messages.items():
    words = len(data['msg'].split())
    print('{}: {} words -> {}'.format(name, words, data['page']))
