"""Tier 2 message drafts from research agents - Batches C and D."""

tier2_messages = {
    # BATCH C
    'Dan McInerney': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Dan. Your AI threat research at Protect AI -- especially the work on prompt injection and model supply chain attacks -- means you see the attack surface from the inside. GuardSpine is an open-source GitHub Action that routes each PR through multi-model AI reviewers at tiered risk levels, producing signed evidence bundles per decision. For someone mapping AI attack vectors, the architecture might be worth poking at: https://github.com/DNYoussef/codeguard-action",
    },
    'Lucas Walter': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Lucas. Building Calico AI's platform means you're deep in the infrastructure decisions around how AI systems get deployed and governed. GuardSpine is an open-source CI/CD governance layer -- AI reviewers (Claude, GPT, Ollama) enforce compliance rubrics on every PR, producing signed evidence bundles. For a CTO shipping AI tooling, the architecture might be relevant: https://github.com/DNYoussef/codeguard-action",
    },
    'Iannis Drakos': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Iannis. Your work on Enterprise AI governance and FAIR data principles -- especially the emphasis on accountability in pharma -- aligns with what GuardSpine enforces at the code layer. AI reviewers run compliance rubrics on every PR and produce signed audit records. For someone pushing interoperability and governance at scale, the approach might resonate: https://guardspine.ai",
    },
    'Casey Fleming': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Casey. Your work at BlackOps Partners on strategic risk and counterintelligence means you see the supply chain threat that AI-generated code introduces -- not just bugs, but unaudited decision paths in production systems. GuardSpine enforces compliance rubrics on every AI-generated PR and produces cryptographically signed evidence bundles. Governance as a security control: https://guardspine.ai",
    },
    'Tarek Ahmad': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Tarek. Your cyber security risk management work -- especially in the financial services context -- means you understand the audit trail requirements regulators are moving toward for AI systems. GuardSpine enforces compliance rubrics on every AI-generated code change and produces signed evidence bundles. Provable governance before code hits production: https://guardspine.ai",
    },
    # BATCH D
    'Craig Schmitz': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Craig. As a partner at Goodwin Procter working on technology transactions, you're advising clients on the legal and compliance frameworks around AI adoption. GuardSpine is an open-source CI/CD governance layer that produces cryptographically signed compliance records for every AI-generated code change -- the kind of evidence your clients' auditors and regulators will be asking for. Context: https://guardspine.ai",
    },
    'Matt Schmid': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Matt. Your AI-first product marketing work and the AI Council you founded show you're tracking how AI tooling gets adopted at scale. GuardSpine is an open-source CI/CD governance layer where AI reviewers enforce compliance rubrics on every PR, producing signed evidence bundles. The GTM angle: enterprises can't adopt AI code generation without provable governance. Details: https://guardspine.ai",
    },
    'Travis Lee': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Travis. Your HumanSovereigntyAI work on keeping humans in the loop with autonomous systems maps directly to what GuardSpine does at the code layer. AI reviewers enforce compliance rubrics on every PR with tiered risk levels -- L4 changes require human approval. Sovereignty through governance architecture, not policy documents: https://guardspine.ai",
    },
    'Doug Hubbard': {
        'page': 'https://guardspine.ai',
        'msg': "Thanks for connecting, Doug. Your 'How to Measure Anything' framework -- especially applied risk analysis and the case against risk matrices -- is the intellectual foundation for what GuardSpine does. We quantify AI code review decisions with agreement scores, risk tiers, and signed evidence bundles instead of subjective review checkboxes. Measurement over theater: https://guardspine.ai",
    },
    'Andrew Penner': {
        'page': 'https://github.com/DNYoussef/codeguard-action',
        'msg': "Thanks for connecting, Andrew. Leading software engineering at TriZetto -- where healthcare claims processing meets HIPAA compliance -- means every AI-generated code change touching PHI needs a governance trail. GuardSpine is a GitHub Action that routes PRs through multi-model AI reviewers at tiered risk levels, producing signed evidence bundles. Drop-in for existing workflows: https://github.com/DNYoussef/codeguard-action",
    },
}

for name, data in tier2_messages.items():
    words = len(data['msg'].split())
    print('{}: {} words -> {}'.format(name, words, data['page']))
