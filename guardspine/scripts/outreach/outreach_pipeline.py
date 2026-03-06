#!/usr/bin/env python3
"""
Research & Outreach Pipeline v2.0

Precision influence architecture for upstream positioning.
NOT marketing. This is agenda-setting.

Purpose:
- Seed framing into power-adjacent networks
- Make ideas feel familiar before introduction
- Let judgment-only engagements emerge organically

Weekly Limits (Non-Negotiable):
- 10-20 total messages per week
- Max 1-2 people per company
- One artifact per person
- No follow-ups unless meaningful reply

Usage:
    python outreach_pipeline.py research --industry biotech
    python outreach_pipeline.py draft --prospect-id ABC123
    python outreach_pipeline.py status
    python outreach_pipeline.py signals
"""

import os
import sys
import json
import logging
import argparse
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum
import sqlite3
import hashlib

# Graceful degradation for optional dependencies
try:
    from universal_components import (
        init_memory_client,
        init_tagger,
        init_telemetry_bridge,
    )
    tagger = init_tagger()
    memory_client = init_memory_client()
    telemetry_bridge = init_telemetry_bridge()
except ImportError:
    # Stub implementations when library not available
    tagger = None
    memory_client = None
    telemetry_bridge = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================
# STRATEGIC CONSTANTS (DO NOT MODIFY LIGHTLY)
# ============================================

WEEKLY_MESSAGE_LIMIT = 20
MAX_PER_COMPANY = 2
ARTIFACTS_PER_PERSON = 1
FOLLOWUP_COOLDOWN_DAYS = 14

# Landing page URLs for campaign outreach
DEV_LANDING_URL = "https://guardspine.ai/dev"
CISO_LANDING_URL = "https://guardspine.ai/security"

POSITION_STATEMENT = """
I built the open-source governance layer for AI-era work. GuardSpine turns every code change,
document edit, and spreadsheet update into cryptographically sealed evidence - verifiable offline,
without trusting us. 8 Apache 2.0 packages. 210 API endpoints. 737 automated tests. GitHub Action installs in 5 minutes.

The Core Insight: Existing tools govern fragments - GitHub covers code, DocuSign covers signatures,
Purview covers data movement - but nobody governs the semantic content of what AI actually changed.
GuardSpine fills that gap.
"""


class Layer(Enum):
    """Four layers of memetic strategy."""
    PUBLIC = 1          # Public legibility (indexed, discoverable)
    ORPHAN = 2          # Orphan authority (share-by-link only)
    SEED = 3            # Private conversation seeding
    PULL = 4            # Engagement pull (diagnostic conversations)


class SignalType(Enum):
    """Response signal classification."""
    GREEN = "green"     # Thoughtful reply, questions about sequencing/governance
    YELLOW = "yellow"   # Requests for training/decks/scale
    RED = "red"         # Pressure to brand/package/mass-distribute
    NONE = "none"       # No response yet


class NarrowcastPainSignal(Enum):
    """Pain signals to listen for in narrowcast channels."""
    REVIEWER_OVERWHELM = "reviewer_overwhelm"
    MAINTAINER_DDOS = "maintainer_ddos"
    SECRETS_PII_LEAK = "secrets_pii_leak"
    COMPLIANCE_AUDIT_GAP = "compliance_audit_gap"
    ACCOUNTABILITY_GAP = "accountability_gap"


class NarrowcastPlatform(Enum):
    """Platforms for narrowcast monitoring."""
    HACKER_NEWS = "hacker_news"
    REDDIT = "reddit"
    GITHUB_DISCUSSIONS = "github_discussions"
    DEV_TO = "dev_to"
    LINKEDIN = "linkedin"
    OWASP_SLACK = "owasp_slack"
    CISO_SERIES = "ciso_series"
    OTHER = "other"


class NarrowcastTier(Enum):
    """Check frequency tiers."""
    TIER_1 = "weekly"       # Highest signal density
    TIER_2 = "biweekly"     # Specialized communities
    TIER_3 = "monthly"      # Decision-maker watering holes
    TIER_4 = "opportunistic" # Niche high-value


class NarrowcastProfile(Enum):
    """Psychological profiles for narrowcast targets."""
    DROWNING_REVIEWER = "drowning_reviewer"
    BESIEGED_MAINTAINER = "besieged_maintainer"
    COMPLIANCE_SQUEEZED = "compliance_squeezed"
    WORRIED_CISO = "worried_ciso"
    SECRET_HUNTER = "secret_hunter"
    DORA_SQUEEZED = "dora_squeezed"


# Narrowcast psychological profile definitions
NARROWCAST_PROFILES = {
    NarrowcastProfile.DROWNING_REVIEWER: {
        "title_patterns": ["Senior Engineer", "Staff Engineer", "Tech Lead", "Principal"],
        "pain": "50+ PRs/week, half AI-generated, review quality declining",
        "emotion": "frustrated, exhausted, feels quality slipping",
        "language_signals": [
            "review fatigue", "rubber stamping", "can't keep up",
            "LGTM without reading", "too many PRs", "AI slop"
        ],
        "codeguard_value": "L0-L4 risk tiering: review dangerous changes carefully, fast-track trivial ones",
        "platforms": [NarrowcastPlatform.REDDIT, NarrowcastPlatform.HACKER_NEWS, NarrowcastPlatform.DEV_TO],
        "subreddits": ["r/ExperiencedDevs", "r/programming", "r/softwareengineering"],
        "persona_map": NarrowcastProfile.DROWNING_REVIEWER,
    },
    NarrowcastProfile.BESIEGED_MAINTAINER: {
        "title_patterns": ["Maintainer", "Core Contributor", "Project Lead"],
        "pain": "Inbox full of AI slop PRs, considering closing PRs entirely",
        "emotion": "angry, burned out, feels abandoned by platforms",
        "language_signals": [
            "AI slop", "vibe coded", "DDoS", "kill switch",
            "closing PRs", "low quality contributions", "spam PRs"
        ],
        "codeguard_value": "Evidence bundles prove whether a PR was meaningfully reviewed before merge",
        "platforms": [NarrowcastPlatform.GITHUB_DISCUSSIONS, NarrowcastPlatform.HACKER_NEWS, NarrowcastPlatform.REDDIT],
        "subreddits": ["r/opensource", "r/programming"],
        "github_threads": ["185387", "159749"],
        "persona_map": NarrowcastProfile.BESIEGED_MAINTAINER,
    },
    NarrowcastProfile.COMPLIANCE_SQUEEZED: {
        "title_patterns": ["Compliance Engineer", "DevSecOps", "Platform Engineer", "GRC"],
        "pain": "Auditors asking 'who reviewed this AI code?' - no evidence exists",
        "emotion": "anxious, squeezed between engineering speed and compliance proof",
        "language_signals": [
            "audit trail", "evidence", "SOC2", "HIPAA", "who approved",
            "immutable record", "EU AI Act", "compliance gap"
        ],
        "codeguard_value": "Cryptographically sealed evidence bundles, offline-verifiable, one command",
        "platforms": [NarrowcastPlatform.REDDIT, NarrowcastPlatform.OWASP_SLACK, NarrowcastPlatform.LINKEDIN],
        "subreddits": ["r/devops", "r/devsecops", "r/compliance"],
        "persona_map": NarrowcastProfile.COMPLIANCE_SQUEEZED,
    },
    NarrowcastProfile.WORRIED_CISO: {
        "title_patterns": ["CISO", "VP Security", "Head of AppSec", "Chief Security"],
        "pain": "Board asking about AI code governance, no good answer",
        "emotion": "politically exposed, needs cover, sees risk but lacks tooling",
        "language_signals": [
            "governance gap", "AI code risk", "accountability",
            "who is responsible", "framework", "board question"
        ],
        "codeguard_value": "Competitive Matrix - only tool covering semantic content governance",
        "platforms": [NarrowcastPlatform.CISO_SERIES, NarrowcastPlatform.REDDIT, NarrowcastPlatform.LINKEDIN],
        "subreddits": ["r/netsec", "r/cissp", "r/cybersecurity"],
        "persona_map": NarrowcastProfile.WORRIED_CISO,
    },
    NarrowcastProfile.SECRET_HUNTER: {
        "title_patterns": ["Security Engineer", "DevSecOps Lead", "AppSec"],
        "pain": "AI code leaking secrets, PII in prompts reaching repos",
        "emotion": "alarmed, fighting a losing battle with volume",
        "language_signals": [
            "hardcoded keys", "secrets in AI code", "PII exposure",
            "entropy detection", "pre-commit hooks", "secret scanning"
        ],
        "codeguard_value": "PII-Shield entropy detection on diffs + HMAC redaction in evidence bundles",
        "platforms": [NarrowcastPlatform.REDDIT, NarrowcastPlatform.HACKER_NEWS, NarrowcastPlatform.OWASP_SLACK],
        "subreddits": ["r/netsec", "r/devsecops"],
        "persona_map": NarrowcastProfile.SECRET_HUNTER,
    },
    NarrowcastProfile.DORA_SQUEEZED: {
        "title_patterns": [
            "Head of IT Risk", "DORA Programme Lead", "Operational Resilience",
            "ICT Risk Manager", "VP Technology Risk", "Compliance Engineer",
            "DevSecOps Lead", "Head of AppSec", "CISO", "CTO",
        ],
        "pain": "DORA enforceable since Jan 2025, regulators want evidence not assurances, no tooling covers AI-generated code semantics",
        "emotion": "squeezed between enforcement deadline and governance gap, politically exposed, needs audit-ready artifacts now",
        "language_signals": [
            "DORA compliance", "ICT risk management", "evidence chain",
            "operational resilience testing", "register of information",
            "third-party ICT risk", "AI code governance", "audit trail gap",
            "who reviewed this AI code", "compliance nightmare",
            "evidence not assurances", "DORA deadline unrealistic",
        ],
        "codeguard_value": "Sealed evidence bundles designed to support DORA Art.6 ICT risk management evidence collection - prove who reviewed AI-generated changes, offline-verifiable, vendor-neutral",
        "platforms": [NarrowcastPlatform.LINKEDIN, NarrowcastPlatform.REDDIT, NarrowcastPlatform.OWASP_SLACK],
        "subreddits": ["r/devsecops", "r/netsec", "r/cybersecurity", "r/fintech"],
        "trade_press": [
            "qa-financial.com", "americanbanker.com", "fintech.global",
            "fintechmagazine.com", "risk.net",
        ],
        "persona_map": NarrowcastProfile.DORA_SQUEEZED,
    },
}

# Narrowcast monitoring channels with search queries
NARROWCAST_CHANNELS = {
    NarrowcastTier.TIER_1: [
        {
            "platform": NarrowcastPlatform.HACKER_NEWS,
            "name": "Hacker News",
            "url": "https://news.ycombinator.com",
            "search_queries": [
                "AI code review", "AI slop", "maintainer overwhelmed",
                "vibe coding production", "kill switch pull request",
                "DORA compliance AI code", "bank AI governance evidence",
            ],
            "profiles": [NarrowcastProfile.DROWNING_REVIEWER, NarrowcastProfile.BESIEGED_MAINTAINER, NarrowcastProfile.DORA_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.GITHUB_DISCUSSIONS,
            "name": "GitHub Community Discussions",
            "url": "https://github.com/orgs/community/discussions",
            "search_queries": [
                "low quality contributions", "AI generated pull request",
                "block copilot", "maintainer tools"
            ],
            "key_threads": ["185387", "159749"],
            "profiles": [NarrowcastProfile.BESIEGED_MAINTAINER],
        },
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/ExperiencedDevs",
            "url": "https://reddit.com/r/ExperiencedDevs",
            "search_queries": [
                "AI code review", "review fatigue", "AI pull requests",
                "too many PRs", "copilot review"
            ],
            "profiles": [NarrowcastProfile.DROWNING_REVIEWER],
        },
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/programming",
            "url": "https://reddit.com/r/programming",
            "search_queries": [
                "vibe coding", "AI code quality", "who reviews AI code",
                "AI slop open source"
            ],
            "profiles": [NarrowcastProfile.DROWNING_REVIEWER, NarrowcastProfile.BESIEGED_MAINTAINER],
        },
    ],
    NarrowcastTier.TIER_2: [
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/netsec",
            "url": "https://reddit.com/r/netsec",
            "search_queries": [
                "AI secrets leak", "PII AI code", "code scanning AI",
                "AI generated vulnerabilities",
                "DORA ICT risk AI", "financial AI code evidence",
            ],
            "profiles": [NarrowcastProfile.SECRET_HUNTER, NarrowcastProfile.WORRIED_CISO, NarrowcastProfile.DORA_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/devsecops",
            "url": "https://reddit.com/r/devsecops",
            "search_queries": [
                "AI compliance", "audit trail AI", "AI governance code",
                "SOC2 AI evidence",
                "DORA compliance code", "DORA evidence AI",
            ],
            "profiles": [NarrowcastProfile.COMPLIANCE_SQUEEZED, NarrowcastProfile.SECRET_HUNTER, NarrowcastProfile.DORA_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/fintech",
            "url": "https://reddit.com/r/fintech",
            "search_queries": [
                "DORA compliance", "AI code governance bank",
                "operational resilience AI", "fintech audit evidence AI",
            ],
            "profiles": [NarrowcastProfile.DORA_SQUEEZED, NarrowcastProfile.COMPLIANCE_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.OWASP_SLACK,
            "name": "OWASP Slack/Discord",
            "url": "https://owasp.org/slack/invite",
            "search_queries": [
                "AI security governance", "AI code review security",
                "agentic AI risk",
                "DORA operational resilience", "financial AI governance",
            ],
            "profiles": [NarrowcastProfile.COMPLIANCE_SQUEEZED, NarrowcastProfile.WORRIED_CISO, NarrowcastProfile.DORA_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.DEV_TO,
            "name": "dev.to",
            "url": "https://dev.to",
            "search_queries": [
                "vibe coding hangover", "code review AI era",
                "AI generated code production"
            ],
            "profiles": [NarrowcastProfile.DROWNING_REVIEWER],
        },
    ],
    NarrowcastTier.TIER_3: [
        {
            "platform": NarrowcastPlatform.CISO_SERIES,
            "name": "CISO Series",
            "url": "https://cisoseries.com",
            "search_queries": [
                "AI governance", "code accountability", "AI risk board",
                "DORA AI evidence gap", "DORA operational resilience CIO",
            ],
            "profiles": [NarrowcastProfile.WORRIED_CISO, NarrowcastProfile.DORA_SQUEEZED],
        },
        {
            "platform": NarrowcastPlatform.LINKEDIN,
            "name": "LinkedIn",
            "url": "https://linkedin.com",
            "search_queries": [
                "AI code review overwhelm", "governance gap AI",
                "EU AI Act compliance code",
                "DORA compliance AI code", "DORA evidence chain bank",
                "who reviewed AI code DORA",
            ],
            "profiles": [NarrowcastProfile.WORRIED_CISO, NarrowcastProfile.COMPLIANCE_SQUEEZED, NarrowcastProfile.DORA_SQUEEZED],
        },
    ],
    NarrowcastTier.TIER_4: [
        {
            "platform": NarrowcastPlatform.REDDIT,
            "name": "r/opensource",
            "url": "https://reddit.com/r/opensource",
            "search_queries": ["maintainer burnout AI", "AI spam PRs"],
            "profiles": [NarrowcastProfile.BESIEGED_MAINTAINER],
        },
        {
            "platform": NarrowcastPlatform.OTHER,
            "name": "HackerOne/Bugcrowd Forums",
            "url": "https://hackerone.com",
            "search_queries": ["AI security reports", "AI generated bugs"],
            "profiles": [NarrowcastProfile.SECRET_HUNTER],
        },
    ],
}

# Narrowcast engagement rules
NARROWCAST_RULES = {
    "max_threads_per_platform_per_week": 1,
    "comment_before_link": True,
    "insight_to_product_ratio": "80/20",
    "never_lead_with_product": True,
    "register_match": {
        NarrowcastPlatform.HACKER_NEWS: "technical depth, concise, evidence-based",
        NarrowcastPlatform.REDDIT: "relatable, empathetic, community-first",
        NarrowcastPlatform.GITHUB_DISCUSSIONS: "solution-oriented, code examples",
        NarrowcastPlatform.DEV_TO: "tutorial-style, practical, show-don't-tell",
        NarrowcastPlatform.LINKEDIN: "framework-oriented, strategic, executive-friendly",
    },
}


class PersonaType(Enum):
    """Target persona categories."""
    # Buyer personas (enterprise sales)
    CEO_BOARD = "ceo_board"
    CFO = "cfo"
    CRO_RISK = "cro_risk"
    TRANSFORMATION_VP = "transformation_vp"
    DATA_AI_LEAD = "data_ai_lead"
    RECRUITER = "recruiter"
    CHIEF_OF_STAFF = "chief_of_staff"
    POWER_ADJACENT = "power_adjacent"
    # Builder personas (product-led growth)
    VP_ENGINEERING = "vp_engineering"
    CISO = "ciso"
    PLATFORM_ENG = "platform_eng"
    COMPLIANCE_ENG = "compliance_eng"
    DEVSECOPS = "devsecops"
    # DORA-specific personas (financial sector)
    DORA_ICT_RISK = "dora_ict_risk"
    DORA_CISO = "dora_ciso"
    # Investor personas (angel/seed fundraising)
    ANGEL_COMPLIANCE_OPS = "angel_compliance_ops"      # Archetype A
    ANGEL_DEVTOOLS_FOUNDER = "angel_devtools_founder"  # Archetype B
    ANGEL_REGULATORY = "angel_regulatory"              # Archetype C


class OutreachLane(Enum):
    """Dual-funnel lane classification."""
    BUILDER = "builder"   # PLG: GitHub -> install -> evidence bundle -> premium
    BUYER = "buyer"       # Enterprise: LinkedIn -> demo -> architecture review -> license
    INVESTOR = "investor" # Angel/Seed: LinkedIn -> artifact -> warm intro -> meeting -> check


class Industry(Enum):
    """Target industries."""
    BIOTECH = "biotech"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    MANUFACTURING = "manufacturing"
    LEGAL = "legal"
    INSURANCE = "insurance"
    GOVERNMENT = "government"
    TECHNOLOGY = "technology"
    VENTURE_CAPITAL = "venture_capital"
    AI_ENGINEERING = "AI Engineering"
    AI_GOVERNANCE = "AI Governance"
    AI_GOVERNANCE_BANKING = "AI Governance / Banking"
    AI_KNOWLEDGE_GRAPHS = "AI/Knowledge Graphs"
    SECURITY_COMPLIANCE = "Security/Compliance"
    WEB3_OPEN_SOURCE = "Web3 / Open Source"


# ============================================
# ARTIFACT DEFINITIONS
# ============================================

@dataclass
class Artifact:
    """An artifact for strategic sharing."""
    id: str
    name: str
    layer: Layer
    description: str
    url: str
    personas: List[PersonaType]
    is_default: bool = False


ARTIFACTS = {
    "vision_brief": Artifact(
        id="vision_brief",
        name="Vision Brief (Why GuardSpine Exists)",
        layer=Layer.PUBLIC,
        description="High-level framing of AI judgment challenges and GuardSpine solution",
        url="/artifacts/public/vision-brief.pdf",
        personas=[PersonaType.CEO_BOARD, PersonaType.CHIEF_OF_STAFF],
        is_default=True
    ),
    "evolution_ladder": Artifact(
        id="evolution_ladder",
        name="Evolution Ladder (GuardSpine Maturity Model)",
        layer=Layer.PUBLIC,
        description="5-stage AI adoption progression with audit levels L0-L4",
        url="/artifacts/public/evolution-ladder.pdf",
        personas=[PersonaType.TRANSFORMATION_VP]
    ),
    "executive_keynote": Artifact(
        id="executive_keynote",
        name="Executive Keynote (The 40% Problem)",
        layer=Layer.PUBLIC,
        description="Leadership transition preparation - why AI initiatives fail",
        url="/artifacts/public/executive-keynote.pdf",
        personas=[PersonaType.RECRUITER, PersonaType.CEO_BOARD]
    ),
    "platform_strategy": Artifact(
        id="platform_strategy",
        name="Platform Strategy (40% Failure Pattern)",
        layer=Layer.PUBLIC,
        description="Why AI initiatives fail quietly - four failure modes",
        url="/artifacts/public/platform-strategy.pdf",
        personas=[PersonaType.CFO, PersonaType.RECRUITER]
    ),
    "codeguard_action": Artifact(
        id="codeguard_action",
        name="CodeGuard GitHub Action",
        layer=Layer.PUBLIC,
        description="Open-source PR risk classification and evidence bundles",
        url="https://github.com/DNYoussef/guardspine-action",
        personas=[PersonaType.DATA_AI_LEAD]
    ),
    "safe_exploration": Artifact(
        id="safe_exploration",
        name="Safe Exploration Framework",
        layer=Layer.ORPHAN,
        description="How to let teams explore AI without fear",
        url="/working/safe-exploration",
        personas=[PersonaType.DATA_AI_LEAD, PersonaType.TRANSFORMATION_VP]
    ),
    "anti_hollowing": Artifact(
        id="anti_hollowing",
        name="Anti-Hollowing Guide",
        layer=Layer.ORPHAN,
        description="First Draft Not First Thought - preventing capability degradation",
        url="/working/anti-hollowing",
        personas=[PersonaType.TRANSFORMATION_VP, PersonaType.CRO_RISK]
    ),
    "regulatory_mapping": Artifact(
        id="regulatory_mapping",
        name="Regulatory Mapping",
        layer=Layer.ORPHAN,
        description="Governance landscape analysis for SOX, HIPAA, SOC2",
        url="/working/regulatory-mapping",
        personas=[PersonaType.CRO_RISK]
    ),
    "value_measurement": Artifact(
        id="value_measurement",
        name="Value Measurement Methodology",
        layer=Layer.ORPHAN,
        description="ROI framework for AI judgment and governance",
        url="/working/value-measurement",
        personas=[PersonaType.CFO]
    ),
    "evidence_bundles": Artifact(
        id="evidence_bundles",
        name="Evidence Bundle Specification",
        layer=Layer.PUBLIC,
        description="Vendor-neutral, offline-verifiable audit format",
        url="https://github.com/DNYoussef/guardspine-spec",
        personas=[PersonaType.CRO_RISK, PersonaType.DATA_AI_LEAD]
    ),
    "market_futures": Artifact(
        id="market_futures",
        name="Market Futures",
        layer=Layer.ORPHAN,
        description="Strategic landscape projection",
        url="/working/market-futures",
        personas=[PersonaType.CEO_BOARD, PersonaType.CFO]
    ),
    # --- PRODUCT ARTIFACTS (Builder Lane) ---
    "github_action": Artifact(
        id="github_action",
        name="GuardSpine GitHub Action",
        layer=Layer.PUBLIC,
        description="Risk-classify PRs and generate audit-grade evidence bundles in CI - designed to support DORA Art.6 evidence collection",
        url="https://github.com/DNYoussef/guardspine-action",
        personas=[PersonaType.VP_ENGINEERING, PersonaType.DEVSECOPS, PersonaType.PLATFORM_ENG, PersonaType.DORA_ICT_RISK]
    ),
    "install_guide": Artifact(
        id="install_guide",
        name="GuardSpine Install Guide (10 min)",
        layer=Layer.PUBLIC,
        description="8 OSS packages, Apache 2.0, zero telemetry - install and verify in 10 minutes",
        url="/product/install",
        personas=[PersonaType.PLATFORM_ENG, PersonaType.DEVSECOPS]
    ),
    "roi_calculator": Artifact(
        id="roi_calculator",
        name="ROI Calculator",
        layer=Layer.PUBLIC,
        description="Interactive compliance cost reduction and audit prep time savings estimator",
        url="/assess#product",
        personas=[PersonaType.CFO, PersonaType.CRO_RISK, PersonaType.CISO]
    ),
    "competitive_matrix": Artifact(
        id="competitive_matrix",
        name="The Missing Middle (Competitive Matrix)",
        layer=Layer.PUBLIC,
        description="Why Vanta/GitHub/DocuSign/Purview all miss semantic artifact governance",
        url="/product",
        personas=[PersonaType.CISO, PersonaType.VP_ENGINEERING, PersonaType.TRANSFORMATION_VP, PersonaType.DORA_CISO]
    ),
    "compliance_rubrics": Artifact(
        id="compliance_rubrics",
        name="Compliance Rubric Packs (HIPAA/SOC2/PCI-DSS/DORA)",
        layer=Layer.PUBLIC,
        description="YAML-based governance rubrics for regulated industries including DORA ICT risk, offline-verifiable",
        url="https://github.com/DNYoussef/GuardSpine",
        personas=[PersonaType.COMPLIANCE_ENG, PersonaType.CRO_RISK, PersonaType.CISO, PersonaType.DORA_ICT_RISK, PersonaType.DORA_CISO]
    ),
    "nomotic_deck": Artifact(
        id="nomotic_deck",
        name="GuardSpine x Nomotic AI Partnership Deck",
        layer=Layer.ORPHAN,
        description="From theory to infrastructure - Nomotic provides the philosophy, GuardSpine the plumbing",
        url="/artifacts/orphan/guardspine-nomotic-deck.pdf",
        personas=[PersonaType.CEO_BOARD, PersonaType.TRANSFORMATION_VP, PersonaType.CHIEF_OF_STAFF]
    ),
    "evidence_demo": Artifact(
        id="evidence_demo",
        name="Before/After Evidence Bundle Demo",
        layer=Layer.PUBLIC,
        description="Run locally: 253 violations -> 0 violations, with sealed hash-chain proof",
        url="/guardspine/artifacts",
        personas=[PersonaType.VP_ENGINEERING, PersonaType.COMPLIANCE_ENG, PersonaType.DEVSECOPS]
    ),
    "open_core_model": Artifact(
        id="open_core_model",
        name="Open-Core Model (What's Free Forever)",
        layer=Layer.PUBLIC,
        description="6 immutable OSS boundary rules - verify without paying, build connectors freely",
        url="/product/open-core",
        personas=[PersonaType.PLATFORM_ENG, PersonaType.VP_ENGINEERING, PersonaType.CISO]
    )
}


# ============================================
# INVESTOR PIPELINE CONSTANTS
# ============================================

INVESTOR_SCORING_RUBRIC = {
    "dimensions": {
        "capacity": {
            "weight": 25,
            "description": "Check size, velocity, current portfolio room",
            "signals": ["Recent exits", "Known check sizes", "Active deal flow"],
        },
        "scar_tissue": {
            "weight": 25,
            "description": "Direct experience with compliance/governance pain",
            "signals": ["CISO/security background", "Audit failures", "Regulatory fines"],
        },
        "catalyst_conviction": {
            "weight": 25,
            "description": "Belief in regulatory-driven adoption, EU AI Act understanding",
            "signals": ["Public statements on AI regulation", "Portfolio in govtech/regtech", "Policy network"],
        },
        "team_execution_fit": {
            "weight": 25,
            "description": "Technical depth match, domain expertise overlap, network value",
            "signals": ["DevTools/infra background", "Open-source track record", "Distribution network"],
        },
    },
    "pass_threshold": 75,
    "max_score": 100,
}

INVESTOR_ARCHETYPES = {
    "A": {
        "name": "Compliance-Scarred Operator",
        "description": "Ex-CISO or security VP who lived through audit failures, breach response, or regulatory fines",
        "positioning": "Lead with evidence gap + regulatory clock. Show the competitive matrix.",
        "pain": "Board asking about AI code governance with no good answer",
        "artifact": "competitive_matrix",
        "meeting_duration_min": 20,
    },
    "B": {
        "name": "DevTools Founder",
        "description": "Built and exited a developer infrastructure company. Understands open-core, PLG, and infra moats.",
        "positioning": "Lead with architecture + open-core model. Show the install path and GitHub Action.",
        "pain": "Sees the governance gap from a builder perspective",
        "artifact": "github_action",
        "meeting_duration_min": 20,
    },
    "C": {
        "name": "Regulatory-Thesis Investor",
        "description": "Invests based on regulatory catalysts. Tracks EU AI Act, DORA, NIS2 timelines.",
        "positioning": "Lead with regulatory calendar + market timing. Show the compliance rubric packs.",
        "pain": "Looking for infrastructure plays that ride regulatory adoption curves",
        "artifact": "compliance_rubrics",
        "meeting_duration_min": 20,
    },
}

NETWORK_MULTIPLIERS = {
    "svci": {
        "name": "Silicon Valley CISO Investments (SVCI)",
        "description": "70+ CISOs co-investing, typical check $350K+/deal",
        "members_in_pipeline": ["Caleb Sima", "David B. Cross", "Sounil Yu"],
        "value": "One SVCI member converts -> warm intro to 70+ security leaders",
    },
    "duo_orbit": {
        "name": "Duo Security Alumni Network",
        "description": "Oberheide/Song + extended Cisco/Decibel network",
        "members_in_pipeline": ["Jon Oberheide", "Dug Song"],
        "value": "Identity/access alumni deeply understand governance infrastructure",
    },
    "drata_syndicate": {
        "name": "Drata Angel Syndicate",
        "description": "Pomel/Sima/Tejada/Slootman/Agarwal co-invest in compliance infra",
        "members_in_pipeline": ["Olivier Pomel", "Caleb Sima"],
        "value": "Compliance-adjacent portfolio = warm referral path to Drata syndicate deals",
    },
}

INVESTOR_MEETING_AGENDAS = {
    "A": {
        "title": "Profile A: Compliance-Scarred Operator",
        "duration": "20 min",
        "segments": [
            {"time": "0-3 min", "topic": "Their pain story", "notes": "Let them describe the audit/breach. Mirror language."},
            {"time": "3-8 min", "topic": "The evidence gap", "notes": "Show competitive matrix. Nobody governs semantic content."},
            {"time": "8-13 min", "topic": "Live demo", "notes": "Evidence bundle generation. Offline verification."},
            {"time": "13-17 min", "topic": "Market timing", "notes": "EU AI Act Aug 2026. DORA already live. Regulatory clock."},
            {"time": "17-20 min", "topic": "Ask", "notes": "Lead angel or co-lead. SVCI syndicate interest."},
        ],
    },
    "B": {
        "title": "Profile B: DevTools Founder",
        "duration": "20 min",
        "segments": [
            {"time": "0-3 min", "topic": "Their exit story", "notes": "What they built, how it scaled, what they learned."},
            {"time": "3-8 min", "topic": "Architecture walkthrough", "notes": "8 OSS packages, hash-chain, kernel parity. Show code."},
            {"time": "8-13 min", "topic": "Open-core model", "notes": "6 immutable OSS boundary rules. Free forever vs paid tiers."},
            {"time": "13-17 min", "topic": "GTM + distribution", "notes": "PLG install path. GitHub Action -> evidence bundle -> premium."},
            {"time": "17-20 min", "topic": "Ask", "notes": "Lead angel or intro to their network. Technical advisory."},
        ],
    },
    "C": {
        "title": "Profile C: Regulatory-Thesis Investor",
        "duration": "20 min",
        "segments": [
            {"time": "0-3 min", "topic": "Their thesis", "notes": "What regulatory catalyst they are tracking. Validate alignment."},
            {"time": "3-8 min", "topic": "Market timing analysis", "notes": "EU AI Act timeline. Binary event Aug 2 2026. First-mover math."},
            {"time": "8-13 min", "topic": "Compliance rubric demo", "notes": "YAML rubric packs. DORA Art.6. Offline verification."},
            {"time": "13-17 min", "topic": "Competitive landscape", "notes": "Nobody else covers semantic content governance. Natural SBOM complement."},
            {"time": "17-20 min", "topic": "Ask", "notes": "Fund-level investment or personal check. Policy network intros."},
        ],
    },
}

INVESTOR_TIERS = {
    "TIER1": {
        "label": "Priority Tier 1",
        "criteria": "Score >= 85, capacity >= $250K, warm-intro path exists",
        "action": "D2: Build 2-3 warm-intro routes within 48 hours",
    },
    "TIER2": {
        "label": "Priority Tier 2",
        "criteria": "Score >= 75, capacity >= $100K or strong network value",
        "action": "D4: Send connector intro ask or artifact-first cold note",
    },
    "TIER3": {
        "label": "Priority Tier 3",
        "criteria": "Score >= 65 or conditional pass (missing one dimension)",
        "action": "D2-D6: Build intro routes or ask for second-order intros",
    },
}

# Seed data: 20 angel investors from CSV + PDF research
SEED_ANGEL_PROSPECTS = [
    # TIER 1 (5 prospects)
    {"name": "Mohamed Nanabhay", "title": "Managing Partner, Mozilla Ventures", "archetype": "C",
     "capacity": "Lead ($1M-$5M)", "linkedin": "uk.linkedin.com/in/mohamedn",
     "intro_paths": "Portfolio adjacency (Credo AI/Holistic AI) | Regulatory networks (OECD AI)",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER1"},
    {"name": "Caleb Sima", "title": "Founding GP, WhiteRabbit; Chair, CSA AI Security Initiative", "archetype": "A/B",
     "capacity": "Lead-likely ($350K+)", "linkedin": "linkedin.com/in/calebsima",
     "intro_paths": "SVCI | Drata syndicate | CSA AI / cloud security ecosystem",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER1"},
    {"name": "Guy Podjarny", "title": "Founder & CEO, Tessl AI; Advisor, Boldstart Ventures", "archetype": "B",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/guypod",
     "intro_paths": "Boldstart orbit | Snyk alumni / devsecops ecosystem",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER1"},
    {"name": "David B. Cross", "title": "CISO, Atlassian; Venture Partner, Rain Capital", "archetype": "A",
     "capacity": "Lead ($1M-$5M)", "linkedin": "linkedin.com/in/david-b-cross-b856657",
     "intro_paths": "Rain Capital | SVCI | RSA circuit",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER1"},
    {"name": "Frederic Kerrest", "title": "Co-Founder & Vice Chairman, Okta; Managing Partner, 515 Ventures", "archetype": "B/C",
     "capacity": "Lead-likely ($250K-$1M+)", "linkedin": "linkedin.com/in/fkerrest",
     "intro_paths": "Okta/identity ecosystem | Supply-chain/provenance portfolio adjacency (Socket/Chainguard)",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER1"},
    # TIER 2 (6 prospects)
    {"name": "Jon Oberheide", "title": "Board member & angel investor (ex Co-founder & CTO, Duo Security)", "archetype": "B",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/jonoberheide",
     "intro_paths": "Duo Security orbit | Cisco/Decibel adjacency",
     "next_action": "D4: Send connector intro ask", "tier": "TIER2"},
    {"name": "Niloofar Razi Howe", "title": "President, The Stratham Group; Operating Partner, Capitol Meridian Partners", "archetype": "C",
     "capacity": "Co-lead or Lead-likely (verify)", "linkedin": "linkedin.com/in/niloofarhowe",
     "intro_paths": "RSA Innovation Sandbox circuit | Gov-tech / CISA networks",
     "next_action": "D4: Send connector intro ask", "tier": "TIER2"},
    {"name": "Jesse Robbins", "title": "General Partner, Heavybit", "archetype": "B",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/jesserobbins",
     "intro_paths": "Heavybit network | DevOps/Velocity conference circuit",
     "next_action": "D4: Send connector intro ask", "tier": "TIER2"},
    {"name": "Phil Venables", "title": "VP/CISO, Google Cloud", "archetype": "A",
     "capacity": "Strategic/Lead-likely (verify)", "linkedin": "linkedin.com/in/philvenables",
     "intro_paths": "Google Cloud / CISO community | Socket.dev portfolio adjacency",
     "next_action": "D4: Send connector intro ask", "tier": "TIER2"},
    {"name": "Solomon Hykes", "title": "Co-Founder & CEO, Dagger (ex Docker co-founder)", "archetype": "B",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/solomonhykes",
     "intro_paths": "Docker alumni / OSS infra networks | GitGuardian portfolio adjacency",
     "next_action": "D4: Send connector intro ask", "tier": "TIER2"},
    {"name": "Ian Hogarth", "title": "Chair, UK AI Safety Institute; Co-Founder & Partner, Plural Platform", "archetype": "C",
     "capacity": "Signal-only ($5K-$50K)", "linkedin": "uk.linkedin.com/in/ianhogarth",
     "intro_paths": "Policy networks | State of AI Report orbit",
     "next_action": "D4: Artifact-first cold note (signal value)", "tier": "TIER2"},
    # TIER 3 (9 prospects)
    {"name": "Luke Kanies", "title": "Angel investor (ex Founder & Executive Chairman, Puppet)", "archetype": "B",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/lukekanies",
     "intro_paths": "Infra-as-code / OSS networks | Puppet alumni",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER3"},
    {"name": "Olivier Pomel", "title": "Co-Founder & CEO, Datadog", "archetype": "B",
     "capacity": "Strategic/Lead-likely (verify)", "linkedin": "linkedin.com/in/olivierpomel",
     "intro_paths": "Drata angel syndicate | Datadog ecosystem",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER3"},
    {"name": "Dug Song", "title": "Managing Director, Cisco Investments; Co-founder, Duo Security", "archetype": "B/A",
     "capacity": "Lead-likely ($250K-$1M)", "linkedin": "linkedin.com/in/dugsong",
     "intro_paths": "Duo Security orbit | Cisco Investments adjacency",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER3"},
    {"name": "Richard Seiersen", "title": "Chief Risk Technology Officer, Qualys", "archetype": "A",
     "capacity": "Lead-likely (verify)", "linkedin": "linkedin.com/in/richardseiersen",
     "intro_paths": "IANS / FAIR Institute networks | Security risk community",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER3"},
    {"name": "Adam Wiggins", "title": "Co-founder & Partner, Muse; Co-founder, Ink & Switch", "archetype": "B",
     "capacity": "Co-lead or Lead-likely (verify)", "linkedin": "linkedin.com/in/adamwiggins",
     "intro_paths": "Heavybit advisory | Heroku alumni / platform engineering networks",
     "next_action": "D2: Build 2-3 warm-intro routes", "tier": "TIER3"},
    {"name": "Nathan Benaich", "title": "Founder & General Partner, Air Street Capital", "archetype": "C",
     "capacity": "Fund-level seed (verify personal check)", "linkedin": "nathanbenaich.substack.com",
     "intro_paths": "State of AI Report orbit | AI regulation investor networks",
     "next_action": "D4: Artifact-first cold note", "tier": "TIER3"},
    {"name": "Moritz Plassnig", "title": "Chief Product Officer, Immuta (ex Codeship founder)", "archetype": "B",
     "capacity": "Signal-only ($5K-$25K)", "linkedin": "moritzplassnig.com/angel-investments",
     "intro_paths": "Immuta governance ecosystem | Snyk orbit (CloudSkiff)",
     "next_action": "D6: Ask for second-order intros", "tier": "TIER3"},
    {"name": "Sounil Yu", "title": "Co-Founder & Chief AI Safety Officer, Knostic", "archetype": "B/C",
     "capacity": "Co-lead or Lead-likely (verify)", "linkedin": "linkedin.com/in/sounil",
     "intro_paths": "SVCI | AI safety / access-controls adjacency",
     "next_action": "D4: Send connector intro ask", "tier": "TIER3"},
    {"name": "Mark Curphey", "title": "Co-Founder & CMO, Crash Override (OWASP founder)", "archetype": "B/A",
     "capacity": "Connector/Advisory (verify)", "linkedin": "",
     "intro_paths": "OWASP / security founder ecosystem",
     "next_action": "D6: Ask for second-order intros", "tier": "TIER3"},
]

# Additional candidates from Lead Angel Targeting PDF (30 candidates)
# These need scoring before import -- listed for reference
LEAD_ANGEL_EXTENDED = [
    {"name": "Karl Mattson", "archetype": "A", "notes": "CISO, Noname Security"},
    {"name": "John Brennan", "archetype": "A", "notes": "VP Security"},
    {"name": "Mandy Andress", "archetype": "A", "notes": "CISO, Elastic"},
    {"name": "Al Ghous", "archetype": "A", "notes": "CISO"},
    {"name": "Kathy Wang", "archetype": "A", "notes": "CISO"},
    {"name": "Joel Fulton", "archetype": "A", "notes": "Co-founder, Lucidum"},
    {"name": "Oren Yunger", "archetype": "C", "notes": "GGV Capital, ex-CISO"},
    {"name": "Justin Somaini", "archetype": "A", "notes": "CISO, Unity"},
    {"name": "Andy Ellis", "archetype": "A", "notes": "Operating Partner, YL Ventures; ex-CSO Akamai"},
    {"name": "Jay Leek", "archetype": "A/C", "notes": "Managing Partner, SYN Ventures"},
    {"name": "Alex Tosheff", "archetype": "A", "notes": "VP CISO, Salesforce"},
    {"name": "Chenxi Wang", "archetype": "A/C", "notes": "Founder, Rain Capital"},
    {"name": "Nicole Perlroth", "archetype": "C", "notes": "Author, cybersecurity journalist"},
    {"name": "Ted Schlein", "archetype": "C", "notes": "Partner, Ballistic Ventures"},
    {"name": "Barmak Meftah", "archetype": "A/B", "notes": "Co-Founder/CEO, Ballistic Ventures; ex-AT&T CISO"},
    {"name": "Neil Daswani", "archetype": "A/B", "notes": "Co-director, Stanford AIS; ex-Snap CISO"},
    {"name": "Jim Routh", "archetype": "A", "notes": "Former CISO, MassMutual/Aetna/CVS"},
    {"name": "Nat Friedman", "archetype": "B", "notes": "ex-GitHub CEO"},
    {"name": "Ben Mann", "archetype": "B", "notes": "ex-Anthropic"},
    {"name": "Joseph Ruscio", "archetype": "B", "notes": "Heavybit"},
    {"name": "Tom Drummond", "archetype": "B", "notes": "ex-Docker"},
    {"name": "Dana Oshiro", "archetype": "B", "notes": "Heavybit"},
    {"name": "Jacob Jofe", "archetype": "B", "notes": "DevTools investor"},
    {"name": "Stephen Blum", "archetype": "B", "notes": "PubNub founder"},
    {"name": "Marius Luther", "archetype": "C", "notes": "EU regulatory"},
    {"name": "Michael Weider", "archetype": "A/B", "notes": "Security + DevTools"},
    {"name": "Jerry Perullo", "archetype": "A", "notes": "CISO, ICE/Intercontinental Exchange"},
    {"name": "Christina Cacioppo", "archetype": "B", "notes": "CEO, Vanta"},
    {"name": "Bret Taylor", "archetype": "B", "notes": "ex-Salesforce Co-CEO, Sierra AI"},
    {"name": "Elad Gil", "archetype": "B/C", "notes": "Prolific angel, infrastructure thesis"},
]


# ============================================
# MESSAGE TEMPLATES
# ============================================

MESSAGE_TEMPLATES = {
    "power_adjacent": """Hi {name},

I've been studying why AI initiatives in regulated environments fail quietly - not due to model performance, but because autonomy, governance, and accountability are mis-sequenced early.

I'm sharing a short note that captures the pattern I see most often. No expectation to reply - just thought it might resonate given your role.

Best,
David

{artifact_url}""",

    "recruiter": """Hi {name},

I work upstream of senior leadership transitions, focused on why strong executives stumble in their first 90-180 days when AI expectations collide with governance and risk reality.

I occasionally run private, off-the-record judgment calibration sessions for incoming leaders - not training, not evaluation - simply better language for navigating AI risk early.

Sharing a short public note that outlines the failure pattern. If it resonates, happy to compare notes sometime; if not, no response needed.

Best,
David

{artifact_url}""",

    "senior_executive": """Hi {name},

I focus on AI adoption from a judgment and governance perspective - specifically where organizations misjudge readiness, scaling, and accountability before problems surface politically or regulatorily.

I'm sharing a brief framework that captures the structural failure mode I see most often. No ask attached - just offering context.

- David

{artifact_url}""",

    "vp_engineering": """Hi {name},

I've been working on the governance gap in AI-assisted code changes - the space between "AI wrote this" and "we can prove how it was reviewed and approved."

I built an open-source GitHub Action that classifies code changes by risk tier and generates audit-grade evidence bundles. The spec is vendor-neutral; auditors can verify offline without trusting our system.

If you're thinking about how to govern AI-assisted code at scale, happy to share what's working. No pitch - just comparing notes.

- David

{artifact_url}""",

    "safe_exploration": """Hi {name},

I've been focused on a counterintuitive pattern: the organizations that move fastest with AI aren't the ones with the least governance - they're the ones with governance that SCALES with autonomy.

73% of orgs are stuck at Stage 1 AI adoption. The ones that advance have figured out how to let teams explore safely. I've been building both the framework and the tooling for this.

Sharing a short note on the evolution pattern. If it resonates, happy to compare notes.

- David

{artifact_url}""",

    "platform_engineer": """Hi {name},

I built an open-source governance layer for AI-assisted work - code, documents, and spreadsheets. The core is 8 Apache 2.0 packages with zero telemetry and offline verification.

The install is `pip install guardspine-verify` or `npm install @guardspine/kernel`. Evidence bundles seal with SHA-256 hash chains; auditors verify the math without touching our servers.

If your team is thinking about how to govern AI-generated changes at scale, the repo might be useful. No pitch - just sharing what we shipped.

- David

{artifact_url}""",

    "ciso_security": """Hi {name},

There's a gap in current tooling that I've been building to fill: Vanta handles process controls, GitHub handles code, DocuSign handles signatures, Purview handles data movement - but nobody governs the semantic content of what AI actually changed in a document or spreadsheet.

I built GuardSpine to close that gap. Open-source core (Apache 2.0), offline-verifiable evidence bundles, L0-L4 risk tiering. The spec is vendor-neutral - auditors verify without trusting our system.

If this blind spot is on your radar, happy to compare notes.

- David

{artifact_url}""",

    "compliance_engineer": """Hi {name},

I've been building open-source governance tooling for AI-era compliance. The part that might interest you: we ship YAML-based rubric packs for HIPAA, SOC2, and PCI-DSS that generate cryptographically sealed evidence bundles.

The key design decision: offline verification. Auditors run `guardspine-verify bundle.zip` and get integrity/signature validation without network access or vendor dependency. Apache 2.0, no license keys.

If you're dealing with the gap between AI-assisted work and audit-grade evidence, this might be relevant.

- David

{artifact_url}""",

    "dora_finance": """Hi {name},

With DORA now enforceable, I keep hearing the same question from compliance teams at financial institutions: "How do we prove AI-assisted code changes went through proper ICT risk management?"

Current tooling covers code review (GitHub), process controls (Vanta), and data movement (Purview) - but none generate evidence of what AI semantically changed and who approved it. That is the gap DORA Article 6 exposes.

I built an open-source governance layer that seals every code change into a cryptographically verifiable evidence bundle - who reviewed it, what risk tier, what changed semantically. Auditors verify offline without trusting our system. Apache 2.0, zero vendor lock-in.

If this blind spot is on your DORA roadmap, happy to compare notes.

- David

{artifact_url}""",

    "dora_ciso": """Hi {name},

A recent QA Financial piece noted that no CIO or CISO they interviewed thought the DORA deadline was realistic. The hardest part: proving AI-assisted code changes went through proper risk management when existing tools were never designed for it.

GitHub tracks who merged. Vanta tracks process controls. Neither tracks what AI semantically changed in a codebase and whether a human meaningfully reviewed it. That is the evidence gap regulators are starting to ask about.

I built GuardSpine to close it - open-source, offline-verifiable evidence bundles with L0-L4 risk tiering. The spec is vendor-neutral; your auditors verify the math without touching our servers.

If DORA evidence chains are on your radar, happy to share what we shipped.

- David

{artifact_url}""",

    # --- LANDING PAGE CAMPAIGN TEMPLATES (Feb 2026) ---

    "dev_landing_page": """Hi {name},

{hook}

{pain_bridge}

I built an open-source GitHub Action that risk-tiers every PR and generates tamper-proof audit trails. 737 automated tests across the ecosystem, Apache 2.0 license, works with your own models.

I put together a calculator that shows how many hours your team loses to rubber-stamped reviews: {landing_url}

- David""",

    "ciso_landing_page": """Hi {name},

{hook}

{pain_bridge}

I built GuardSpine -- open-source, offline-verifiable judgment receipts for every PR. Risk-tiered L0-L4, multi-model AI deliberation, tamper-proof hash chain. Maps to {frameworks}.

I put together a cost model for what this saves on audit prep and regulatory exposure: {landing_url}

- David""",

    # --- INVESTOR TEMPLATES ---

    "investor_warm_intro_ask": """Hi {connector_name},

I'm raising a small angel round for GuardSpine - open-source governance infrastructure for AI-generated code changes. We seal every code change into a cryptographically verifiable evidence bundle. 8 Apache 2.0 packages, 149 API endpoints, offline-verifiable.

{target_name} keeps coming up as someone who deeply understands {target_angle}. Would you be open to a quick intro? I can send a one-pager or the GitHub Action link - whatever makes the intro easiest for you.

Happy to return the favor on anything in my network.

- David""",

    "investor_artifact_cold": """Hi {name},

{hook}

I built the open-source governance layer for AI-era code changes - GuardSpine seals every PR into a cryptographically verifiable evidence bundle. 8 Apache 2.0 packages, offline verification, no vendor lock-in.

With the EU AI Act fully applicable Aug 2 2026, the compliance gap for AI-generated code is becoming a board-level question. We are raising a small angel round to ship the Team and Org tiers.

I put together a {artifact_name} that maps the gap. Worth 5 minutes if {value_prop}.

No worries if timing is off.

- David

{artifact_url}""",

    "investor_archetype_a": """Hi {name},

{hook}

I keep hearing the same question from CISOs: "How do we prove AI-assisted code changes went through proper risk management?" GitHub tracks who merged. Vanta tracks process controls. Neither tracks what AI semantically changed.

I built GuardSpine to close that gap - open-source, offline-verifiable evidence bundles, L0-L4 risk tiering. The spec is vendor-neutral. With the EU AI Act hitting full applicability Aug 2 2026, the compliance gap is becoming urgent.

We are raising a small angel round. Given your experience with {pain_reference}, I thought this might resonate. Happy to send the competitive matrix or jump on a 20-min call.

- David

{artifact_url}""",

    "investor_archetype_b": """Hi {name},

{hook}

I built the open-source governance layer for AI-generated code changes. The architecture: 8 Apache 2.0 packages, SHA-256 hash-chain evidence bundles, cross-language kernel parity (TypeScript + Python). Install is `pip install guardspine-verify` or `npm install @guardspine/kernel`. Auditors verify offline without trusting our servers.

Open-core model: spec + kernels + GitHub Action = free forever. UI dashboard + multi-lane guards + approval workflows = paid tiers.

We are raising a small angel round. Given what you built with {their_company}, I thought the infra pattern might resonate. Happy to walk through the architecture or share the repo.

- David

{artifact_url}""",

    "investor_archetype_c": """Hi {name},

{hook}

The EU AI Act hits full applicability Aug 2 2026. Every organization using AI-assisted code will need to prove governance - who reviewed what, what changed semantically, what risk tier. No existing tool covers this.

I built GuardSpine to fill the gap: open-source governance infrastructure with cryptographically sealed evidence bundles. 8 Apache 2.0 packages. Offline-verifiable. Already shipping the free tier.

We are raising a small angel round to ship Team and Org tiers before the regulatory window opens. If infrastructure plays on regulatory catalysts are in your thesis, happy to share the market timing analysis.

- David

{artifact_url}""",
}


# ============================================
# DATA MODELS
# ============================================

@dataclass
class Prospect:
    """A potential outreach target."""
    id: str
    name: str
    title: str
    company: str
    industry: Industry
    persona: PersonaType
    linkedin_url: Optional[str] = None
    email: Optional[str] = None
    notes: str = ""
    source: str = ""
    lane: OutreachLane = OutreachLane.BUYER
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    # Engagement tracking
    artifact_sent: Optional[str] = None
    message_sent_at: Optional[str] = None
    response_received: bool = False
    signal_type: SignalType = SignalType.NONE
    signal_notes: str = ""


@dataclass
class WeeklyMetrics:
    """Weekly cadence tracking."""
    week_start: str
    messages_sent: int = 0
    companies_contacted: List[str] = field(default_factory=list)
    artifacts_shared: Dict[str, int] = field(default_factory=dict)
    responses_received: int = 0
    green_signals: int = 0
    yellow_signals: int = 0
    red_signals: int = 0


# ============================================
# DATABASE LAYER
# ============================================

class OutreachDatabase:
    """SQLite database for outreach tracking."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS prospects (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    title TEXT,
                    company TEXT,
                    industry TEXT,
                    persona TEXT,
                    lane TEXT DEFAULT 'buyer',
                    linkedin_url TEXT,
                    email TEXT,
                    notes TEXT,
                    source TEXT,
                    created_at TEXT,
                    artifact_sent TEXT,
                    message_sent_at TEXT,
                    response_received INTEGER DEFAULT 0,
                    signal_type TEXT DEFAULT 'none',
                    signal_notes TEXT
                );

                CREATE TABLE IF NOT EXISTS weekly_metrics (
                    week_start TEXT PRIMARY KEY,
                    messages_sent INTEGER DEFAULT 0,
                    companies_json TEXT,
                    artifacts_json TEXT,
                    responses_received INTEGER DEFAULT 0,
                    green_signals INTEGER DEFAULT 0,
                    yellow_signals INTEGER DEFAULT 0,
                    red_signals INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    action TEXT,
                    prospect_id TEXT,
                    details TEXT
                );

                CREATE TABLE IF NOT EXISTS narrowcast_threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    title TEXT,
                    pain_signal TEXT,
                    profiles_json TEXT,
                    discovered_at TEXT,
                    engaged_at TEXT,
                    comment_text TEXT,
                    outcome TEXT,
                    prospects_sourced INTEGER DEFAULT 0,
                    notes TEXT
                );

                CREATE TABLE IF NOT EXISTS narrowcast_scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_date TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    channel_name TEXT,
                    query TEXT,
                    threads_found INTEGER DEFAULT 0,
                    threads_relevant INTEGER DEFAULT 0,
                    notes TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_prospects_company ON prospects(company);
                CREATE INDEX IF NOT EXISTS idx_prospects_persona ON prospects(persona);
                CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
                CREATE INDEX IF NOT EXISTS idx_narrowcast_platform ON narrowcast_threads(platform);
                CREATE INDEX IF NOT EXISTS idx_narrowcast_scans_date ON narrowcast_scans(scan_date);
            """)
            # Migration: add lane column if missing
            try:
                conn.execute("SELECT lane FROM prospects LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute("ALTER TABLE prospects ADD COLUMN lane TEXT DEFAULT 'buyer'")
            # Migration: add investor columns if missing
            try:
                conn.execute("SELECT archetype FROM prospects LIMIT 1")
            except sqlite3.OperationalError:
                conn.execute("ALTER TABLE prospects ADD COLUMN archetype TEXT")
                conn.execute("ALTER TABLE prospects ADD COLUMN investor_score INTEGER")
                conn.execute("ALTER TABLE prospects ADD COLUMN investor_tier TEXT")
                conn.execute("ALTER TABLE prospects ADD COLUMN capacity_band TEXT")
                conn.execute("ALTER TABLE prospects ADD COLUMN intro_paths TEXT")
                conn.execute("ALTER TABLE prospects ADD COLUMN next_action TEXT")

    def add_prospect(self, prospect: Prospect) -> bool:
        """Add a new prospect."""
        with sqlite3.connect(self.db_path) as conn:
            try:
                conn.execute("""
                    INSERT INTO prospects
                    (id, name, title, company, industry, persona, lane, linkedin_url,
                     email, notes, source, created_at, signal_type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    prospect.id, prospect.name, prospect.title, prospect.company,
                    prospect.industry.value, prospect.persona.value, prospect.lane.value,
                    prospect.linkedin_url,
                    prospect.email, prospect.notes, prospect.source, prospect.created_at,
                    prospect.signal_type.value
                ))
                self._log_activity(conn, "prospect_added", prospect.id, f"Added {prospect.name}")
                return True
            except sqlite3.IntegrityError:
                return False

    def get_prospect(self, prospect_id: str) -> Optional[Prospect]:
        """Get a prospect by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM prospects WHERE id = ?", (prospect_id,)
            ).fetchone()
            if row:
                return self._row_to_prospect(row)
        return None

    def get_prospects_by_company(self, company: str) -> List[Prospect]:
        """Get all prospects at a company."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM prospects WHERE company = ?", (company,)
            ).fetchall()
            return [self._row_to_prospect(row) for row in rows]

    def get_uncontacted_prospects(self, limit: int = 20) -> List[Prospect]:
        """Get prospects who haven't been contacted."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM prospects
                WHERE message_sent_at IS NULL
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [self._row_to_prospect(row) for row in rows]

    def mark_contacted(self, prospect_id: str, artifact_id: str) -> bool:
        """Mark a prospect as contacted."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE prospects
                SET artifact_sent = ?, message_sent_at = ?
                WHERE id = ?
            """, (artifact_id, datetime.now().isoformat(), prospect_id))
            self._log_activity(conn, "message_sent", prospect_id, f"Artifact: {artifact_id}")
            return True

    def record_signal(self, prospect_id: str, signal: SignalType, notes: str = "") -> bool:
        """Record a response signal."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE prospects
                SET response_received = 1, signal_type = ?, signal_notes = ?
                WHERE id = ?
            """, (signal.value, notes, prospect_id))
            self._log_activity(conn, f"signal_{signal.value}", prospect_id, notes)
            return True

    def get_weekly_metrics(self, week_start: Optional[str] = None) -> WeeklyMetrics:
        """Get metrics for a week."""
        if not week_start:
            # Get current week's Monday
            today = datetime.now()
            week_start = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                "SELECT * FROM weekly_metrics WHERE week_start = ?", (week_start,)
            ).fetchone()

            if row:
                return WeeklyMetrics(
                    week_start=row["week_start"],
                    messages_sent=row["messages_sent"],
                    companies_contacted=json.loads(row["companies_json"] or "[]"),
                    artifacts_shared=json.loads(row["artifacts_json"] or "{}"),
                    responses_received=row["responses_received"],
                    green_signals=row["green_signals"],
                    yellow_signals=row["yellow_signals"],
                    red_signals=row["red_signals"]
                )
            return WeeklyMetrics(week_start=week_start)

    def increment_weekly_message(self, company: str, artifact_id: str):
        """Increment weekly message count."""
        metrics = self.get_weekly_metrics()
        metrics.messages_sent += 1
        if company not in metrics.companies_contacted:
            metrics.companies_contacted.append(company)
        metrics.artifacts_shared[artifact_id] = metrics.artifacts_shared.get(artifact_id, 0) + 1

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO weekly_metrics
                (week_start, messages_sent, companies_json, artifacts_json,
                 responses_received, green_signals, yellow_signals, red_signals)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metrics.week_start, metrics.messages_sent,
                json.dumps(metrics.companies_contacted), json.dumps(metrics.artifacts_shared),
                metrics.responses_received, metrics.green_signals,
                metrics.yellow_signals, metrics.red_signals
            ))

    @staticmethod
    def _safe_enum(enum_cls, value, default):
        """Parse enum value, falling back to default on mismatch."""
        if not value:
            return default
        try:
            return enum_cls(value)
        except ValueError:
            return default

    def _row_to_prospect(self, row: sqlite3.Row) -> Prospect:
        """Convert database row to Prospect."""
        return Prospect(
            id=row["id"],
            name=row["name"],
            title=row["title"] or "",
            company=row["company"] or "",
            industry=self._safe_enum(Industry, row["industry"], Industry.TECHNOLOGY),
            persona=self._safe_enum(PersonaType, row["persona"], PersonaType.POWER_ADJACENT),
            linkedin_url=row["linkedin_url"],
            email=row["email"],
            notes=row["notes"] or "",
            source=row["source"] or "",
            lane=self._safe_enum(OutreachLane, row["lane"], OutreachLane.BUYER),
            created_at=row["created_at"] or "",
            artifact_sent=row["artifact_sent"],
            message_sent_at=row["message_sent_at"],
            response_received=bool(row["response_received"]),
            signal_type=self._safe_enum(SignalType, row["signal_type"], SignalType.NONE),
            signal_notes=row["signal_notes"] or ""
        )

    def _log_activity(self, conn: sqlite3.Connection, action: str,
                      prospect_id: str, details: str):
        """Log an activity."""
        conn.execute("""
            INSERT INTO activity_log (timestamp, action, prospect_id, details)
            VALUES (?, ?, ?, ?)
        """, (datetime.now().isoformat(), action, prospect_id, details))

    # --- Narrowcast DB methods ---

    def add_narrowcast_thread(self, url: str, platform: str, title: str,
                              pain_signal: str, profiles: List[str],
                              notes: str = "") -> int:
        """Record a discovered narrowcast thread."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO narrowcast_threads
                (url, platform, title, pain_signal, profiles_json,
                 discovered_at, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url, platform, title, pain_signal,
                  json.dumps(profiles), datetime.now().isoformat(), notes))
            return cursor.lastrowid

    def mark_thread_engaged(self, thread_id: int, comment_text: str) -> bool:
        """Mark a narrowcast thread as engaged (commented on)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE narrowcast_threads
                SET engaged_at = ?, comment_text = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), comment_text, thread_id))
            return True

    def update_thread_outcome(self, thread_id: int, outcome: str,
                              prospects_sourced: int = 0) -> bool:
        """Update a thread's engagement outcome."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE narrowcast_threads
                SET outcome = ?, prospects_sourced = ?
                WHERE id = ?
            """, (outcome, prospects_sourced, thread_id))
            return True

    def log_narrowcast_scan(self, tier: str, platform: str,
                            channel_name: str, query: str,
                            threads_found: int, threads_relevant: int,
                            notes: str = "") -> int:
        """Log a narrowcast monitoring scan."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO narrowcast_scans
                (scan_date, tier, platform, channel_name, query,
                 threads_found, threads_relevant, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (datetime.now().isoformat(), tier, platform,
                  channel_name, query, threads_found, threads_relevant, notes))
            return cursor.lastrowid

    def get_narrowcast_threads(self, platform: Optional[str] = None,
                               engaged_only: bool = False,
                               limit: int = 20) -> List[Dict]:
        """Get narrowcast threads with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM narrowcast_threads WHERE 1=1"
            params = []
            if platform:
                query += " AND platform = ?"
                params.append(platform)
            if engaged_only:
                query += " AND engaged_at IS NOT NULL"
            query += " ORDER BY discovered_at DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def get_narrowcast_scan_history(self, days: int = 7) -> List[Dict]:
        """Get recent scan history."""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("""
                SELECT * FROM narrowcast_scans
                WHERE scan_date > ?
                ORDER BY scan_date DESC
            """, (cutoff,)).fetchall()
            return [dict(row) for row in rows]

    def get_narrowcast_stats(self) -> Dict[str, Any]:
        """Get narrowcast engagement statistics."""
        with sqlite3.connect(self.db_path) as conn:
            total = conn.execute(
                "SELECT COUNT(*) FROM narrowcast_threads"
            ).fetchone()[0]
            engaged = conn.execute(
                "SELECT COUNT(*) FROM narrowcast_threads WHERE engaged_at IS NOT NULL"
            ).fetchone()[0]
            prospects = conn.execute(
                "SELECT COALESCE(SUM(prospects_sourced), 0) FROM narrowcast_threads"
            ).fetchone()[0]

            # Per-platform breakdown
            conn.row_factory = sqlite3.Row
            platform_rows = conn.execute("""
                SELECT platform,
                       COUNT(*) as threads,
                       SUM(CASE WHEN engaged_at IS NOT NULL THEN 1 ELSE 0 END) as engaged,
                       COALESCE(SUM(prospects_sourced), 0) as prospects
                FROM narrowcast_threads
                GROUP BY platform
            """).fetchall()

            # Recent scans
            week_ago = (datetime.now() - timedelta(days=7)).isoformat()
            scans_this_week = conn.execute(
                "SELECT COUNT(*) FROM narrowcast_scans WHERE scan_date > ?",
                (week_ago,)
            ).fetchone()[0]

            return {
                "total_threads": total,
                "engaged_threads": engaged,
                "prospects_sourced": prospects,
                "scans_this_week": scans_this_week,
                "platforms": [dict(r) for r in platform_rows],
            }


# ============================================
# CORE PIPELINE
# ============================================

class OutreachPipeline:
    """Main outreach pipeline orchestrator."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.db_path = Path(self.config.get(
            "db_path",
            Path.home() / ".claude" / "outreach" / "outreach.db"
        ))
        self.db = OutreachDatabase(self.db_path)
        self.artifact_base_url = self.config.get(
            "artifact_base_url",
            "https://dnyoussef.com"
        )

    def get_artifact_for_persona(self, persona: PersonaType) -> Artifact:
        """Get the best artifact for a persona."""
        # Find artifacts that match this persona
        matches = [a for a in ARTIFACTS.values() if persona in a.personas]

        if not matches:
            # Return default (Vision Brief)
            return ARTIFACTS["vision_brief"]

        # Prefer public artifacts for first contact
        public = [a for a in matches if a.layer == Layer.PUBLIC]
        if public:
            return public[0]

        return matches[0]

    def get_template_for_persona(self, persona: PersonaType) -> str:
        """Get message template for persona."""
        PERSONA_TEMPLATE_MAP = {
            PersonaType.RECRUITER: "recruiter",
            PersonaType.CEO_BOARD: "senior_executive",
            PersonaType.CFO: "senior_executive",
            PersonaType.CRO_RISK: "senior_executive",
            PersonaType.VP_ENGINEERING: "vp_engineering",
            PersonaType.PLATFORM_ENG: "platform_engineer",
            PersonaType.DEVSECOPS: "platform_engineer",
            PersonaType.CISO: "ciso_security",
            PersonaType.COMPLIANCE_ENG: "compliance_engineer",
            PersonaType.TRANSFORMATION_VP: "safe_exploration",
            PersonaType.DATA_AI_LEAD: "vp_engineering",
            PersonaType.DORA_ICT_RISK: "dora_finance",
            PersonaType.DORA_CISO: "dora_ciso",
            PersonaType.ANGEL_COMPLIANCE_OPS: "investor_archetype_a",
            PersonaType.ANGEL_DEVTOOLS_FOUNDER: "investor_archetype_b",
            PersonaType.ANGEL_REGULATORY: "investor_archetype_c",
        }
        template_key = PERSONA_TEMPLATE_MAP.get(persona, "power_adjacent")
        return MESSAGE_TEMPLATES[template_key]

    @staticmethod
    def infer_lane(persona: PersonaType) -> OutreachLane:
        """Infer outreach lane from persona type."""
        INVESTOR_PERSONAS = {
            PersonaType.ANGEL_COMPLIANCE_OPS,
            PersonaType.ANGEL_DEVTOOLS_FOUNDER,
            PersonaType.ANGEL_REGULATORY,
        }
        BUILDER_PERSONAS = {
            PersonaType.VP_ENGINEERING, PersonaType.PLATFORM_ENG,
            PersonaType.DEVSECOPS, PersonaType.COMPLIANCE_ENG,
            PersonaType.DORA_ICT_RISK, PersonaType.DORA_CISO,
            PersonaType.DATA_AI_LEAD,
        }
        if persona in INVESTOR_PERSONAS:
            return OutreachLane.INVESTOR
        return OutreachLane.BUILDER if persona in BUILDER_PERSONAS else OutreachLane.BUYER

    def can_contact_this_week(self) -> tuple[bool, str]:
        """Check if we can send more messages this week."""
        metrics = self.db.get_weekly_metrics()

        if metrics.messages_sent >= WEEKLY_MESSAGE_LIMIT:
            return False, f"Weekly limit reached ({metrics.messages_sent}/{WEEKLY_MESSAGE_LIMIT})"

        return True, f"{WEEKLY_MESSAGE_LIMIT - metrics.messages_sent} messages remaining"

    def can_contact_company(self, company: str) -> tuple[bool, str]:
        """Check if we can contact more people at this company."""
        prospects = self.db.get_prospects_by_company(company)
        contacted = [p for p in prospects if p.message_sent_at]

        if len(contacted) >= MAX_PER_COMPANY:
            return False, f"Company limit reached ({len(contacted)}/{MAX_PER_COMPANY})"

        return True, f"{MAX_PER_COMPANY - len(contacted)} contacts available at {company}"

    def generate_prospect_id(self, name: str, company: str) -> str:
        """Generate unique prospect ID."""
        data = f"{name.lower()}:{company.lower()}"
        return hashlib.sha256(data.encode()).hexdigest()[:12]

    def add_prospect(
        self,
        name: str,
        title: str,
        company: str,
        industry: Industry,
        persona: PersonaType,
        linkedin_url: Optional[str] = None,
        email: Optional[str] = None,
        notes: str = "",
        source: str = "manual"
    ) -> Prospect:
        """Add a new prospect to the database."""
        prospect_id = self.generate_prospect_id(name, company)

        prospect = Prospect(
            id=prospect_id,
            name=name,
            title=title,
            company=company,
            industry=industry,
            persona=persona,
            lane=self.infer_lane(persona),
            linkedin_url=linkedin_url,
            email=email,
            notes=notes,
            source=source
        )

        self.db.add_prospect(prospect)
        logger.info(f"Added prospect: {name} ({title}) at {company}")

        return prospect

    def draft_message(self, prospect_id: str) -> Dict[str, Any]:
        """Draft an outreach message for a prospect."""
        prospect = self.db.get_prospect(prospect_id)
        if not prospect:
            return {"error": f"Prospect not found: {prospect_id}"}

        # Check constraints
        can_send, reason = self.can_contact_this_week()
        if not can_send:
            return {"error": reason, "blocked": True}

        can_company, company_reason = self.can_contact_company(prospect.company)
        if not can_company:
            return {"error": company_reason, "blocked": True}

        # Already contacted?
        if prospect.message_sent_at:
            return {
                "error": f"Already contacted on {prospect.message_sent_at}",
                "blocked": True
            }

        # Get artifact and template
        artifact = self.get_artifact_for_persona(prospect.persona)
        template = self.get_template_for_persona(prospect.persona)

        # Build artifact URL (don't prepend base for absolute URLs)
        if artifact.url.startswith("http"):
            artifact_url = artifact.url
        else:
            artifact_url = f"{self.artifact_base_url}{artifact.url}"

        # Generate message
        message = template.format(
            name=prospect.name.split()[0],  # First name only
            artifact_url=artifact_url
        )

        return {
            "prospect": asdict(prospect),
            "artifact": {
                "id": artifact.id,
                "name": artifact.name,
                "url": artifact_url,
                "layer": artifact.layer.name
            },
            "message": message,
            "ready_to_send": True
        }

    def confirm_sent(self, prospect_id: str, artifact_id: str) -> Dict[str, Any]:
        """Confirm a message was sent (call after actually sending)."""
        prospect = self.db.get_prospect(prospect_id)
        if not prospect:
            return {"error": f"Prospect not found: {prospect_id}"}

        self.db.mark_contacted(prospect_id, artifact_id)
        self.db.increment_weekly_message(prospect.company, artifact_id)

        logger.info(f"Confirmed message sent to {prospect.name} with {artifact_id}")

        return {
            "success": True,
            "prospect": prospect.name,
            "artifact": artifact_id,
            "timestamp": datetime.now().isoformat()
        }

    def record_response(
        self,
        prospect_id: str,
        signal: SignalType,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Record a response signal from a prospect."""
        prospect = self.db.get_prospect(prospect_id)
        if not prospect:
            return {"error": f"Prospect not found: {prospect_id}"}

        self.db.record_signal(prospect_id, signal, notes)

        # Log guidance based on signal
        guidance = ""
        if signal == SignalType.GREEN:
            guidance = "Good signal! Consider diagnostic conversation if they express interest."
        elif signal == SignalType.YELLOW:
            guidance = "Respond by CONSTRAINING, not expanding. Redirect to judgment-only."
        elif signal == SignalType.RED:
            guidance = "Decline politely. This is not your market."

        logger.info(f"Recorded {signal.value} signal from {prospect.name}: {notes}")

        return {
            "success": True,
            "signal": signal.value,
            "guidance": guidance
        }

    # ============================================
    # NARROWCAST METHODS
    # ============================================

    def narrowcast_scan_plan(self, tier: Optional[str] = None) -> Dict[str, Any]:
        """Generate a narrowcast monitoring plan for the current period."""
        plan = {}
        tiers_to_scan = [NarrowcastTier(tier)] if tier else list(NarrowcastTier)

        for t in tiers_to_scan:
            channels = NARROWCAST_CHANNELS.get(t, [])
            plan[t.value] = {
                "frequency": t.value,
                "channels": []
            }
            for ch in channels:
                plan[t.value]["channels"].append({
                    "name": ch["name"],
                    "platform": ch["platform"].value,
                    "url": ch["url"],
                    "search_queries": ch["search_queries"],
                    "target_profiles": [p.value for p in ch["profiles"]],
                })

        return {
            "plan": plan,
            "rules": {
                "max_threads_per_platform_per_week": NARROWCAST_RULES["max_threads_per_platform_per_week"],
                "insight_to_product_ratio": NARROWCAST_RULES["insight_to_product_ratio"],
                "never_lead_with_product": NARROWCAST_RULES["never_lead_with_product"],
            },
            "profiles_available": [p.value for p in NarrowcastProfile],
        }

    def narrowcast_add_thread(self, url: str, platform: str, title: str,
                              pain_signal: str, profiles: List[str],
                              notes: str = "") -> Dict[str, Any]:
        """Add a discovered thread to narrowcast tracking."""
        thread_id = self.db.add_narrowcast_thread(
            url=url, platform=platform, title=title,
            pain_signal=pain_signal, profiles=profiles, notes=notes
        )

        # Get profile-specific guidance
        guidance = []
        for profile_name in profiles:
            try:
                profile = NarrowcastProfile(profile_name)
                pdata = NARROWCAST_PROFILES.get(profile, {})
                if pdata:
                    guidance.append({
                        "profile": profile_name,
                        "language_signals": pdata.get("language_signals", []),
                        "codeguard_value": pdata.get("codeguard_value", ""),
                    })
            except ValueError:
                pass

        # Get platform register
        try:
            plat = NarrowcastPlatform(platform)
            register = NARROWCAST_RULES["register_match"].get(plat, "")
        except ValueError:
            register = ""

        logger.info(f"Added narrowcast thread #{thread_id}: {title} ({platform})")

        return {
            "thread_id": thread_id,
            "url": url,
            "platform": platform,
            "pain_signal": pain_signal,
            "engagement_guidance": guidance,
            "register": register,
            "rule_reminder": "80% insight, 20% product. Comment before link. Match the register.",
        }

    def narrowcast_engage(self, thread_id: int, comment_text: str) -> Dict[str, Any]:
        """Record engagement with a narrowcast thread."""
        self.db.mark_thread_engaged(thread_id, comment_text)
        logger.info(f"Engaged narrowcast thread #{thread_id}")
        return {
            "success": True,
            "thread_id": thread_id,
            "engaged_at": datetime.now().isoformat(),
        }

    def narrowcast_outcome(self, thread_id: int, outcome: str,
                           prospects_sourced: int = 0) -> Dict[str, Any]:
        """Record outcome of a narrowcast engagement."""
        self.db.update_thread_outcome(thread_id, outcome, prospects_sourced)
        logger.info(
            f"Narrowcast thread #{thread_id} outcome: {outcome} "
            f"({prospects_sourced} prospects)"
        )
        return {
            "success": True,
            "thread_id": thread_id,
            "outcome": outcome,
            "prospects_sourced": prospects_sourced,
        }

    def narrowcast_log_scan(self, tier: str, platform: str,
                            channel_name: str, query: str,
                            threads_found: int, threads_relevant: int,
                            notes: str = "") -> Dict[str, Any]:
        """Log a completed narrowcast scan."""
        scan_id = self.db.log_narrowcast_scan(
            tier=tier, platform=platform, channel_name=channel_name,
            query=query, threads_found=threads_found,
            threads_relevant=threads_relevant, notes=notes
        )
        logger.info(
            f"Scan #{scan_id}: {channel_name} '{query}' -> "
            f"{threads_relevant}/{threads_found} relevant"
        )
        return {
            "scan_id": scan_id,
            "tier": tier,
            "platform": platform,
            "threads_found": threads_found,
            "threads_relevant": threads_relevant,
        }

    def narrowcast_dashboard(self) -> Dict[str, Any]:
        """Get narrowcast monitoring dashboard."""
        stats = self.db.get_narrowcast_stats()
        recent_threads = self.db.get_narrowcast_threads(limit=10)
        recent_scans = self.db.get_narrowcast_scan_history(days=7)

        # Build profile summary
        profile_summary = {}
        for profile in NarrowcastProfile:
            pdata = NARROWCAST_PROFILES.get(profile, {})
            profile_summary[profile.value] = {
                "pain": pdata.get("pain", ""),
                "language_signals": pdata.get("language_signals", [])[:3],
                "codeguard_value": pdata.get("codeguard_value", ""),
            }

        return {
            "stats": stats,
            "recent_threads": recent_threads,
            "recent_scans": recent_scans,
            "profiles": profile_summary,
            "channels": {
                tier.value: [
                    {"name": ch["name"], "platform": ch["platform"].value}
                    for ch in channels
                ]
                for tier, channels in NARROWCAST_CHANNELS.items()
            },
            "rules": NARROWCAST_RULES,
        }

    def narrowcast_search_queries(self, profile: Optional[str] = None) -> Dict[str, Any]:
        """Get search queries for narrowcast monitoring, optionally filtered by profile."""
        queries = {}

        for tier, channels in NARROWCAST_CHANNELS.items():
            for ch in channels:
                if profile:
                    try:
                        target_profile = NarrowcastProfile(profile)
                        if target_profile not in ch["profiles"]:
                            continue
                    except ValueError:
                        pass

                key = ch["name"]
                queries[key] = {
                    "tier": tier.value,
                    "platform": ch["platform"].value,
                    "url": ch["url"],
                    "queries": ch["search_queries"],
                    "profiles": [p.value for p in ch["profiles"]],
                }

        return {"channels": queries, "filter_profile": profile}

    def get_status(self) -> Dict[str, Any]:
        """Get current outreach status and metrics."""
        metrics = self.db.get_weekly_metrics()
        uncontacted = self.db.get_uncontacted_prospects(50)

        return {
            "week_start": metrics.week_start,
            "weekly_metrics": {
                "messages_sent": metrics.messages_sent,
                "limit": WEEKLY_MESSAGE_LIMIT,
                "remaining": WEEKLY_MESSAGE_LIMIT - metrics.messages_sent,
                "companies_contacted": len(metrics.companies_contacted),
                "max_per_company": MAX_PER_COMPANY
            },
            "signals": {
                "responses": metrics.responses_received,
                "green": metrics.green_signals,
                "yellow": metrics.yellow_signals,
                "red": metrics.red_signals
            },
            "pipeline": {
                "uncontacted_prospects": len(uncontacted),
                "ready_to_draft": min(
                    len(uncontacted),
                    WEEKLY_MESSAGE_LIMIT - metrics.messages_sent
                )
            },
            "position": POSITION_STATEMENT.strip()
        }

    def archetype_to_persona(self, archetype: str) -> PersonaType:
        """Map investor archetype string (A/B/C/A/B etc) to PersonaType."""
        primary = archetype.split("/")[0].strip()
        mapping = {
            "A": PersonaType.ANGEL_COMPLIANCE_OPS,
            "B": PersonaType.ANGEL_DEVTOOLS_FOUNDER,
            "C": PersonaType.ANGEL_REGULATORY,
        }
        return mapping.get(primary, PersonaType.ANGEL_DEVTOOLS_FOUNDER)

    def seed_angel_prospects(self) -> Dict[str, Any]:
        """Import seed angel investor prospects from SEED_ANGEL_PROSPECTS constant."""
        added = 0
        skipped = 0
        errors = []

        for entry in SEED_ANGEL_PROSPECTS:
            name = entry["name"]
            title = entry["title"]
            # Extract company from title (text after last comma)
            parts = title.rsplit(",", 1)
            company = parts[-1].strip() if len(parts) > 1 else "Independent"

            persona = self.archetype_to_persona(entry["archetype"])
            prospect_id = self.generate_prospect_id(name, company)

            # Check if already exists
            existing = self.db.get_prospect(prospect_id)
            if existing:
                skipped += 1
                continue

            linkedin = entry.get("linkedin", "")
            if linkedin and not linkedin.startswith("http"):
                linkedin = "https://" + linkedin

            prospect = Prospect(
                id=prospect_id,
                name=name,
                title=title,
                company=company,
                industry=Industry.TECHNOLOGY,
                persona=persona,
                lane=OutreachLane.INVESTOR,
                linkedin_url=linkedin if linkedin else None,
                notes=f"Archetype: {entry['archetype']} | Capacity: {entry['capacity']}",
                source="angel_seed_csv",
            )

            success = self.db.add_prospect(prospect)
            if success:
                # Update investor-specific columns
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.execute("""
                        UPDATE prospects SET
                            archetype = ?, investor_tier = ?,
                            capacity_band = ?, intro_paths = ?,
                            next_action = ?
                        WHERE id = ?
                    """, (
                        entry["archetype"], entry["tier"],
                        entry["capacity"], entry.get("intro_paths", ""),
                        entry.get("next_action", ""), prospect_id
                    ))
                added += 1
                logger.info(f"Imported investor: {name} [{entry['archetype']}] -> {entry['tier']}")
            else:
                errors.append(name)

        return {
            "added": added,
            "skipped": skipped,
            "errors": errors,
            "total_seed": len(SEED_ANGEL_PROSPECTS),
        }

    def get_investor_dashboard(self) -> Dict[str, Any]:
        """Get investor pipeline dashboard."""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # All investor prospects
            rows = conn.execute("""
                SELECT * FROM prospects
                WHERE lane = 'investor'
                ORDER BY investor_tier, name
            """).fetchall()

            tiers = {"TIER1": [], "TIER2": [], "TIER3": [], "untiered": []}
            for row in rows:
                entry = {
                    "id": row["id"],
                    "name": row["name"],
                    "title": row["title"],
                    "archetype": row["archetype"] if "archetype" in row.keys() else "",
                    "capacity": row["capacity_band"] if "capacity_band" in row.keys() else "",
                    "contacted": bool(row["message_sent_at"]),
                    "signal": row["signal_type"],
                    "next_action": row["next_action"] if "next_action" in row.keys() else "",
                }
                tier = row["investor_tier"] if "investor_tier" in row.keys() else None
                tiers.get(tier or "untiered", tiers["untiered"]).append(entry)

        return {
            "tiers": tiers,
            "counts": {k: len(v) for k, v in tiers.items()},
            "total": sum(len(v) for v in tiers.values()),
            "archetypes": INVESTOR_ARCHETYPES,
            "network_multipliers": NETWORK_MULTIPLIERS,
            "scoring_rubric": INVESTOR_SCORING_RUBRIC,
        }

    def get_signals_dashboard(self) -> Dict[str, Any]:
        """Get detailed signals analysis."""
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row

            # Get all responses
            rows = conn.execute("""
                SELECT * FROM prospects
                WHERE response_received = 1
                ORDER BY message_sent_at DESC
            """).fetchall()

        signals = {
            "green": [],
            "yellow": [],
            "red": []
        }

        for row in rows:
            prospect = self.db._row_to_prospect(row)
            entry = {
                "name": prospect.name,
                "company": prospect.company,
                "title": prospect.title,
                "artifact": prospect.artifact_sent,
                "notes": prospect.signal_notes,
                "contacted": prospect.message_sent_at
            }
            signals[prospect.signal_type.value].append(entry)

        return {
            "signals": signals,
            "guidance": {
                "green": "Thoughtful replies, questions about sequencing/governance, artifact forwarding, language mirroring",
                "yellow": "Requests for training/decks/scale - respond by constraining",
                "red": "Pressure to brand/package/mass-distribute - decline politely"
            },
            "watch_for": [
                "Language mirroring: 'quiet failure', 'auditability', 'hollowing', 'evidence bundles'",
                "Questions about sequencing, governance, or risk tiering",
                "Internal forwarding of artifacts or product links",
                "GitHub: stars, forks, issues filed on guardspine repos",
                "npm/pip installs of guardspine packages",
                "Connector contributions or custom rubric PRs",
                "Requests for enterprise demo or architecture review"
            ]
        }


# ============================================
# CLI INTERFACE
# ============================================

def print_status(pipeline: OutreachPipeline):
    """Print current status."""
    status = pipeline.get_status()

    print("\n" + "=" * 60)
    print("OUTREACH PIPELINE STATUS")
    print("=" * 60)

    print(f"\nWeek: {status['week_start']}")
    print(f"Position: {status['position'][:80]}...")

    print("\nWEEKLY CADENCE:")
    wm = status["weekly_metrics"]
    print(f"  Messages: {wm['messages_sent']}/{wm['limit']} ({wm['remaining']} remaining)")
    print(f"  Companies: {wm['companies_contacted']} contacted")

    print("\nSIGNALS:")
    sig = status["signals"]
    print(f"  Responses: {sig['responses']}")
    print(f"  Green: {sig['green']} | Yellow: {sig['yellow']} | Red: {sig['red']}")

    print("\nPIPELINE:")
    print(f"  Uncontacted prospects: {status['pipeline']['uncontacted_prospects']}")
    print(f"  Ready to draft: {status['pipeline']['ready_to_draft']}")

    # Narrowcast summary
    try:
        nc_stats = pipeline.db.get_narrowcast_stats()
        print("\nNARROWCAST:")
        print(f"  Threads tracked: {nc_stats['total_threads']}")
        print(f"  Threads engaged: {nc_stats['engaged_threads']}")
        print(f"  Prospects sourced: {nc_stats['prospects_sourced']}")
        print(f"  Scans this week: {nc_stats['scans_this_week']}")
    except Exception:
        print("\nNARROWCAST: (run narrowcast-dashboard for details)")

    print("=" * 60 + "\n")


def print_signals(pipeline: OutreachPipeline):
    """Print signals dashboard."""
    dashboard = pipeline.get_signals_dashboard()

    print("\n" + "=" * 60)
    print("SIGNALS DASHBOARD")
    print("=" * 60)

    for signal_type in ["green", "yellow", "red"]:
        signals = dashboard["signals"][signal_type]
        print(f"\n{signal_type.upper()} SIGNALS ({len(signals)}):")
        print(f"  Guidance: {dashboard['guidance'][signal_type]}")
        for s in signals[:5]:
            print(f"  - {s['name']} ({s['company']}): {s['notes'][:50]}...")

    print("\nWATCH FOR:")
    for item in dashboard["watch_for"]:
        print(f"  - {item}")

    print("=" * 60 + "\n")


def print_narrowcast_dashboard(pipeline: OutreachPipeline):
    """Print narrowcast monitoring dashboard."""
    dashboard = pipeline.narrowcast_dashboard()
    stats = dashboard["stats"]

    print("\n" + "=" * 60)
    print("NARROWCAST MONITORING DASHBOARD")
    print("=" * 60)

    print("\nSTATS:")
    print(f"  Threads tracked: {stats['total_threads']}")
    print(f"  Threads engaged: {stats['engaged_threads']}")
    print(f"  Prospects sourced: {stats['prospects_sourced']}")
    print(f"  Scans this week: {stats['scans_this_week']}")

    if stats.get("platforms"):
        print("\nPER-PLATFORM:")
        for p in stats["platforms"]:
            print(f"  {p['platform']}: {p['threads']} threads, {p['engaged']} engaged, {p['prospects']} prospects")

    print("\nPROFILES:")
    for name, data in dashboard["profiles"].items():
        signals = ", ".join(data["language_signals"])
        print(f"  {name}:")
        print(f"    Pain: {data['pain'][:60]}")
        print(f"    Listen for: {signals}")
        print(f"    Value prop: {data['codeguard_value'][:60]}")

    print("\nCHANNELS BY TIER:")
    for tier, channels in dashboard["channels"].items():
        names = ", ".join(ch["name"] for ch in channels)
        print(f"  {tier}: {names}")

    threads = dashboard["recent_threads"]
    if threads:
        print(f"\nRECENT THREADS ({len(threads)}):")
        for t in threads[:5]:
            engaged = "ENGAGED" if t.get("engaged_at") else "TRACKED"
            print(f"  [{engaged}] {t['platform']}: {t['title'][:50]}")
            print(f"    {t['url']}")

    print("\nRULES:")
    print(f"  Max threads/platform/week: {dashboard['rules']['max_threads_per_platform_per_week']}")
    print(f"  Insight:Product ratio: {dashboard['rules']['insight_to_product_ratio']}")
    print(f"  Never lead with product: {dashboard['rules']['never_lead_with_product']}")

    print("=" * 60 + "\n")


def print_narrowcast_plan(pipeline: OutreachPipeline, tier: Optional[str] = None):
    """Print narrowcast scan plan."""
    plan_data = pipeline.narrowcast_scan_plan(tier)

    print("\n" + "=" * 60)
    print("NARROWCAST SCAN PLAN")
    print("=" * 60)

    for tier_name, tier_data in plan_data["plan"].items():
        print(f"\n{tier_name.upper()} (check {tier_data['frequency']}):")
        for ch in tier_data["channels"]:
            print(f"  {ch['name']} [{ch['platform']}]")
            print(f"    URL: {ch['url']}")
            print(f"    Queries: {', '.join(ch['search_queries'][:3])}")
            print(f"    Profiles: {', '.join(ch['target_profiles'])}")

    print(f"\nAvailable profiles: {', '.join(plan_data['profiles_available'])}")
    print("=" * 60 + "\n")


def print_narrowcast_queries(pipeline: OutreachPipeline, profile: Optional[str] = None):
    """Print search queries for narrowcast monitoring."""
    data = pipeline.narrowcast_search_queries(profile)

    print("\n" + "=" * 60)
    title = "NARROWCAST SEARCH QUERIES"
    if profile:
        title += f" (profile: {profile})"
    print(title)
    print("=" * 60)

    for name, ch in data["channels"].items():
        print(f"\n{name} [{ch['tier']}]:")
        print(f"  URL: {ch['url']}")
        for q in ch["queries"]:
            print(f"  -> {q}")
        print(f"  Profiles: {', '.join(ch['profiles'])}")

    print("=" * 60 + "\n")


async def main():
    parser = argparse.ArgumentParser(
        description="Research & Outreach Pipeline v2.0 + Narrowcast"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Status command
    subparsers.add_parser("status", help="Show current status")

    # Signals command
    subparsers.add_parser("signals", help="Show signals dashboard")

    # Add prospect command
    add_parser = subparsers.add_parser("add", help="Add a prospect")
    add_parser.add_argument("--name", required=True, help="Full name")
    add_parser.add_argument("--title", required=True, help="Job title")
    add_parser.add_argument("--company", required=True, help="Company name")
    add_parser.add_argument("--industry", required=True,
                           choices=[i.value for i in Industry])
    add_parser.add_argument("--persona", required=True,
                           choices=[p.value for p in PersonaType])
    add_parser.add_argument("--linkedin", help="LinkedIn URL")
    add_parser.add_argument("--email", help="Email address")
    add_parser.add_argument("--notes", default="", help="Notes")

    # Draft message command
    draft_parser = subparsers.add_parser("draft", help="Draft message for prospect")
    draft_parser.add_argument("--prospect-id", required=True, help="Prospect ID")

    # Confirm sent command
    confirm_parser = subparsers.add_parser("confirm", help="Confirm message sent")
    confirm_parser.add_argument("--prospect-id", required=True)
    confirm_parser.add_argument("--artifact-id", required=True)

    # Record signal command
    signal_parser = subparsers.add_parser("signal", help="Record response signal")
    signal_parser.add_argument("--prospect-id", required=True)
    signal_parser.add_argument("--type", required=True,
                              choices=["green", "yellow", "red"])
    signal_parser.add_argument("--notes", default="", help="Signal notes")

    # List prospects command
    list_parser = subparsers.add_parser("list", help="List prospects")
    list_parser.add_argument("--uncontacted", action="store_true",
                            help="Show only uncontacted")

    # --- Narrowcast subcommands ---

    # narrowcast-dashboard
    subparsers.add_parser("narrowcast-dashboard",
                          help="Show narrowcast monitoring dashboard")

    # narrowcast-plan
    nc_plan = subparsers.add_parser("narrowcast-plan",
                                    help="Show narrowcast scan plan")
    nc_plan.add_argument("--tier", choices=["weekly", "biweekly", "monthly", "opportunistic"],
                         help="Filter by tier")

    # narrowcast-queries
    nc_queries = subparsers.add_parser("narrowcast-queries",
                                       help="Show search queries for monitoring")
    nc_queries.add_argument("--profile",
                            choices=[p.value for p in NarrowcastProfile],
                            help="Filter by psychological profile")

    # narrowcast-add-thread
    nc_add = subparsers.add_parser("narrowcast-add-thread",
                                    help="Track a discovered thread")
    nc_add.add_argument("--url", required=True, help="Thread URL")
    nc_add.add_argument("--platform", required=True,
                        choices=[p.value for p in NarrowcastPlatform])
    nc_add.add_argument("--title", required=True, help="Thread title")
    nc_add.add_argument("--pain-signal", required=True,
                        choices=[s.value for s in NarrowcastPainSignal])
    nc_add.add_argument("--profiles", required=True,
                        help="Comma-separated profile names")
    nc_add.add_argument("--notes", default="", help="Notes")

    # narrowcast-engage
    nc_engage = subparsers.add_parser("narrowcast-engage",
                                      help="Record engagement with a thread")
    nc_engage.add_argument("--thread-id", required=True, type=int)
    nc_engage.add_argument("--comment", required=True,
                           help="Comment text posted")

    # narrowcast-outcome
    nc_outcome = subparsers.add_parser("narrowcast-outcome",
                                       help="Record thread engagement outcome")
    nc_outcome.add_argument("--thread-id", required=True, type=int)
    nc_outcome.add_argument("--outcome", required=True,
                            help="Outcome description")
    nc_outcome.add_argument("--prospects", type=int, default=0,
                            help="Number of prospects sourced")

    # narrowcast-log-scan
    nc_scan = subparsers.add_parser("narrowcast-log-scan",
                                    help="Log a completed monitoring scan")
    nc_scan.add_argument("--tier", required=True,
                         choices=["weekly", "biweekly", "monthly", "opportunistic"])
    nc_scan.add_argument("--platform", required=True,
                         choices=[p.value for p in NarrowcastPlatform])
    nc_scan.add_argument("--channel", required=True, help="Channel name")
    nc_scan.add_argument("--query", required=True, help="Search query used")
    nc_scan.add_argument("--found", type=int, required=True,
                         help="Threads found")
    nc_scan.add_argument("--relevant", type=int, required=True,
                         help="Threads relevant")
    nc_scan.add_argument("--notes", default="")

    # investor-import
    subparsers.add_parser("investor-import",
                          help="Import seed angel investor prospects")

    # investor-dashboard
    subparsers.add_parser("investor-dashboard",
                          help="Show investor pipeline dashboard")

    # narrowcast-threads
    nc_threads = subparsers.add_parser("narrowcast-threads",
                                       help="List tracked threads")
    nc_threads.add_argument("--platform",
                            choices=[p.value for p in NarrowcastPlatform])
    nc_threads.add_argument("--engaged-only", action="store_true")

    args = parser.parse_args()

    pipeline = OutreachPipeline()

    if args.command == "status":
        print_status(pipeline)

    elif args.command == "signals":
        print_signals(pipeline)

    elif args.command == "add":
        prospect = pipeline.add_prospect(
            name=args.name,
            title=args.title,
            company=args.company,
            industry=Industry(args.industry),
            persona=PersonaType(args.persona),
            linkedin_url=args.linkedin,
            email=args.email,
            notes=args.notes
        )
        print(f"Added prospect: {prospect.id}")

    elif args.command == "draft":
        result = pipeline.draft_message(args.prospect_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print("\n" + "=" * 60)
            print("DRAFT MESSAGE")
            print("=" * 60)
            print(f"\nTo: {result['prospect']['name']} ({result['prospect']['title']})")
            print(f"Company: {result['prospect']['company']}")
            print(f"Artifact: {result['artifact']['name']} ({result['artifact']['layer']})")
            print(f"\n{result['message']}")
            print("=" * 60)
            print("\nTo confirm sent, run:")
            print(f"  python outreach_pipeline.py confirm --prospect-id {args.prospect_id} --artifact-id {result['artifact']['id']}")

    elif args.command == "confirm":
        result = pipeline.confirm_sent(args.prospect_id, args.artifact_id)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Confirmed: Message sent to {result['prospect']}")

    elif args.command == "signal":
        result = pipeline.record_response(
            args.prospect_id,
            SignalType(args.type),
            args.notes
        )
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Recorded {result['signal']} signal")
            print(f"Guidance: {result['guidance']}")

    elif args.command == "list":
        if args.uncontacted:
            prospects = pipeline.db.get_uncontacted_prospects(50)
        else:
            # Get all prospects
            with sqlite3.connect(pipeline.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM prospects ORDER BY created_at DESC LIMIT 50").fetchall()
                prospects = [pipeline.db._row_to_prospect(row) for row in rows]

        print(f"\nProspects ({len(prospects)}):")
        for p in prospects:
            status = "SENT" if p.message_sent_at else "READY"
            signal = f" [{p.signal_type.value}]" if p.response_received else ""
            lane_tag = f"[{p.lane.value[0].upper()}]" if hasattr(p, 'lane') else "[B]"
            print(f"  {p.id[:8]} | {lane_tag} {status}{signal} | {p.name} ({p.title}) @ {p.company}")

    # --- Investor command handlers ---

    elif args.command == "investor-import":
        result = pipeline.seed_angel_prospects()
        print(f"\nImported {result['added']} angel investor prospects")
        print(f"Skipped {result['skipped']} (already exist)")
        if result['errors']:
            print(f"Errors: {', '.join(result['errors'])}")
        print(f"Total seed data: {result['total_seed']}")

    elif args.command == "investor-dashboard":
        dashboard = pipeline.get_investor_dashboard()
        print("\n" + "=" * 60)
        print("INVESTOR PIPELINE DASHBOARD")
        print("=" * 60)
        print(f"\nTotal investors: {dashboard['total']}")
        for tier_name, prospects in dashboard["tiers"].items():
            if not prospects:
                continue
            tier_info = INVESTOR_TIERS.get(tier_name, {})
            label = tier_info.get("label", tier_name)
            print(f"\n{label} ({len(prospects)}):")
            if tier_info.get("action"):
                print(f"  Action: {tier_info['action']}")
            for p in prospects:
                status = "SENT" if p["contacted"] else "READY"
                signal = f" [{p['signal']}]" if p["signal"] != "none" else ""
                arch = f"[{p['archetype']}]" if p.get("archetype") else ""
                cap = f" {p['capacity']}" if p.get("capacity") else ""
                print(f"  {p['id'][:8]} {arch} {status}{signal} | {p['name']}{cap}")
                if p.get("next_action"):
                    print(f"    -> {p['next_action']}")

        print("\nNETWORK MULTIPLIERS:")
        for key, nm in dashboard["network_multipliers"].items():
            members = ", ".join(nm["members_in_pipeline"])
            print(f"  {nm['name']}: {members}")
            print(f"    {nm['value']}")
        print("=" * 60 + "\n")

    # --- Narrowcast command handlers ---

    elif args.command == "narrowcast-dashboard":
        print_narrowcast_dashboard(pipeline)

    elif args.command == "narrowcast-plan":
        print_narrowcast_plan(pipeline, args.tier)

    elif args.command == "narrowcast-queries":
        print_narrowcast_queries(pipeline, getattr(args, "profile", None))

    elif args.command == "narrowcast-add-thread":
        profiles = [p.strip() for p in args.profiles.split(",")]
        result = pipeline.narrowcast_add_thread(
            url=args.url, platform=args.platform, title=args.title,
            pain_signal=args.pain_signal, profiles=profiles,
            notes=args.notes
        )
        print(f"Tracked thread #{result['thread_id']}: {args.title}")
        if result.get("engagement_guidance"):
            for g in result["engagement_guidance"]:
                print(f"  Profile: {g['profile']}")
                print(f"  Listen for: {', '.join(g['language_signals'][:3])}")
                print(f"  Value prop: {g['codeguard_value'][:60]}")
        if result.get("register"):
            print(f"  Register: {result['register']}")
        print(f"  Rule: {result['rule_reminder']}")

    elif args.command == "narrowcast-engage":
        result = pipeline.narrowcast_engage(args.thread_id, args.comment)
        print(f"Engaged thread #{args.thread_id} at {result['engaged_at']}")

    elif args.command == "narrowcast-outcome":
        result = pipeline.narrowcast_outcome(
            args.thread_id, args.outcome, args.prospects
        )
        print(f"Outcome recorded for thread #{args.thread_id}: {args.outcome}")
        if args.prospects:
            print(f"  Prospects sourced: {args.prospects}")

    elif args.command == "narrowcast-log-scan":
        result = pipeline.narrowcast_log_scan(
            tier=args.tier, platform=args.platform,
            channel_name=args.channel, query=args.query,
            threads_found=args.found, threads_relevant=args.relevant,
            notes=args.notes
        )
        print(f"Scan #{result['scan_id']}: {args.relevant}/{args.found} relevant threads")

    elif args.command == "narrowcast-threads":
        threads = pipeline.db.get_narrowcast_threads(
            platform=getattr(args, "platform", None),
            engaged_only=getattr(args, "engaged_only", False)
        )
        print(f"\nTracked Threads ({len(threads)}):")
        for t in threads:
            engaged = "ENGAGED" if t.get("engaged_at") else "TRACKED"
            outcome = f" -> {t['outcome']}" if t.get("outcome") else ""
            prospects = f" ({t['prospects_sourced']} prospects)" if t.get("prospects_sourced") else ""
            print(f"  #{t['id']} [{engaged}] {t['platform']}: {t['title'][:50]}{outcome}{prospects}")
            print(f"    {t['url']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
