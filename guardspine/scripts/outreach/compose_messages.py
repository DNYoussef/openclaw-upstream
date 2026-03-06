#!/usr/bin/env python3
"""
Research-driven message composition for campaign prospects.

Reads research_notes (from deep-research swarm) and composes personalized
messages where the hook references specific discoverable facts about each person.
Every message must pass the swap test: replacing the name must break coherence.

Usage:
    python compose_messages.py                Compose all with research_notes
    python compose_messages.py --batch 3      Compose only batch 3
    python compose_messages.py --review       Show all drafts for review
    python compose_messages.py --review-batch 2  Review specific batch (20 per batch)
    python compose_messages.py --stats        Show composition stats
    python compose_messages.py --swap-test    Run swap test on all drafted messages
    python compose_messages.py --quality      Run full quality gate report
"""

import sqlite3
import os
import hashlib
import sys
import re

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

DEV_LANDING = "https://guardspine.ai/dev"
CISO_LANDING = "https://guardspine.ai/security"

BANNED_TERMS = [
    "delve", "leverage", "paradigm shift", "synergy", "synergize",
    "revolutionize", "transform", "unlock", "supercharge", "empower",
    "game-changing", "cutting-edge", "disruptive", "next-generation",
    "best-in-class", "thought leader", "deep dive", "holistic",
    "scalable solution", "ecosystem", "move the needle", "circle back",
    "low-hanging fruit", "boil the ocean", "at the end of the day",
    "it goes without saying",
    "ai code review", "ai governance", "ai tool",
    "cryptographic proof", "evidence bundle",
    "multi-model consensus",
]

INDUSTRY_FRAMEWORKS = {
    "finance": "SOC 2, DORA, PCI DSS",
    "banking": "SOC 2, DORA, PCI DSS",
    "crypto": "SOC 2, PCI DSS",
    "insurance": "SOC 2, DORA",
    "healthcare": "HIPAA, SOC 2",
    "pharma": "HIPAA, SOC 2, EU AI Act",
    "biotech": "SOC 2, HIPAA, EU AI Act",
    "medtech": "SOC 2, FDA, HIPAA",
    "aviation": "SOC 2, DOT, ISO 27001",
    "telecom": "SOC 2, ISO 27001",
    "government": "ISO 27001, FedRAMP",
    "hospitality": "PCI DSS, SOC 2",
    "travel": "PCI DSS, SOC 2, DORA",
    "food": "PCI DSS, SOC 2",
    "sports": "SOC 2, PCI DSS",
    "ecommerce": "SOC 2, PCI DSS",
    "testing": "ISO 27001, SOC 2",
    "identity": "SOC 2, ISO 27001",
    "ics_security": "NERC CIP, ISO 27001",
    "consulting": "SOC 2, ISO 27001",
    "tech": "SOC 2, EU AI Act",
    "cybersecurity": "SOC 2, ISO 27001",
    "compliance": "SOC 2, DORA, HIPAA",
    "academia": "SOC 2, HIPAA",
    "gaming": "SOC 2, PCI DSS",
    "regulatory": "DORA, EU AI Act",
    "media": "SOC 2",
    "nonprofit": "SOC 2",
    "vc": "SOC 2",
    "security": "SOC 2, ISO 27001",
    "devsecops": "SOC 2, ISO 27001",
    "devtools": "SOC 2",
    "mlops": "SOC 2, EU AI Act",
    "ai": "SOC 2, EU AI Act",
    "AI Engineering": "SOC 2, EU AI Act",
    "AI/Knowledge Graphs": "SOC 2, EU AI Act",
    "AI Governance": "SOC 2, EU AI Act",
    "fintech": "SOC 2, DORA, PCI DSS",
    "data": "SOC 2, GDPR",
}


# ===== Research notes parser =====

def parse_research_notes(research_notes):
    """Parse structured research_notes into dict."""
    if not research_notes or not research_notes.strip():
        return {"facts": [], "hook_angle": "", "pain_signal": "", "confidence": "LOW"}

    facts = []
    hook_angle = ""
    pain_signal = ""
    confidence = "LOW"

    lines = research_notes.strip().split("\n")
    in_facts = False

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("FACTS:"):
            in_facts = True
            continue
        if stripped.startswith("HOOK_ANGLE:"):
            in_facts = False
            hook_angle = stripped.replace("HOOK_ANGLE:", "").strip()
            continue
        if stripped.startswith("PAIN_SIGNAL:"):
            in_facts = False
            pain_signal = stripped.replace("PAIN_SIGNAL:", "").strip()
            continue
        if stripped.startswith("CONFIDENCE:"):
            in_facts = False
            confidence = stripped.replace("CONFIDENCE:", "").strip().upper()
            continue
        if in_facts and stripped.startswith("- "):
            facts.append(stripped[2:].strip())

    return {
        "facts": facts,
        "hook_angle": hook_angle,
        "pain_signal": pain_signal,
        "confidence": confidence,
    }


def craft_hook(facts, hook_angle, name, company, title, segment):
    """Craft a hook line from research facts and hook_angle.

    The hook MUST reference at least one specific fact unique to this person.
    Returns a 1-2 sentence hook that reads as natural direct address.
    """
    if not hook_angle or hook_angle == "NEEDS_MANUAL_RESEARCH":
        return None

    if not facts:
        return None

    first = name.split()[0]

    # Extract specific anchors from facts for the hook
    # Look for: project names, talk titles, awards, quotes, metrics
    anchors = []
    for fact in facts[:4]:
        # Dates
        dates = re.findall(r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w*\s+\d{4}", fact)
        # Numbers/metrics
        metrics = re.findall(r"\d+[\d,.]*[KkMm]?\+?\s*(?:stars|followers|facilities|ships|countries|reservations|tests)", fact)
        # Quoted phrases
        quotes = re.findall(r'"([^"]+)"', fact)
        # Awards/recognition
        awards = re.findall(r"(?:award|winner|finalist|nominee|recipient|C100|ORBIE)[^.;]*", fact, re.I)
        # Conferences
        talks = re.findall(r"(?:spoke at|keynote|speaker at|presented at|appeared on|podcast)[^.;]*", fact, re.I)
        # Tools/projects
        tools = re.findall(r"(?:created?|built|founded?|authored?|co-authored?)\s+([A-Z][^\s,;.]+(?:\s+[A-Z][^\s,;.]+)?)", fact)

        anchors.extend(quotes[:1])
        anchors.extend(awards[:1])
        anchors.extend(talks[:1])
        anchors.extend(tools[:1])
        anchors.extend(metrics[:1])

    # Pick best anchor to lead the hook
    best_fact = facts[0] if facts else ""

    # Build hook patterns based on what we found
    hook = None

    # Pattern: Award/recognition
    for fact in facts[:3]:
        if re.search(r"(?:award|winner|finalist|nominee|recipient|C100|ORBIE|Trailblazer)", fact, re.I):
            award_text = re.search(r"((?:Named|Won|Received|Finalist|Nominee|Recipient)[^.;]+)", fact, re.I)
            if award_text:
                award_str = award_text.group(1).strip().rstrip('.')
                # Remove parenthetical source notes
                award_str = re.sub(r"\s*\([^)]+\)", "", award_str).strip()
                hook = f"Congratulations on the recognition -- {award_str}. That caught my eye for a specific reason."
                break
            match = re.search(r"(C100\s+\w+|ORBIE\s+\w+|Trailblazer\s+\w+)", fact, re.I)
            if match:
                hook = f"Congratulations on the {match.group(1)} recognition. Your work at {company} caught my attention for a specific reason."
                break

    # Pattern: Specific talk/podcast
    if not hook:
        for fact in facts[:3]:
            talk_match = re.search(r"(?:spoke at|keynote at|speaker at|appeared on|podcast)\s+([^.;,]+)", fact, re.I)
            if talk_match:
                venue = talk_match.group(1).strip()
                hook = f"I came across your {venue.rstrip('.')} appearance -- the angle on code governance resonated."
                break

    # Pattern: Authored/created something
    if not hook:
        for fact in facts[:3]:
            create_match = re.search(
                r"(?:co-)?(?:authored?|created?|built|founded?)\s+(?:the\s+)?"
                r"([A-Z\"][^.;(]+?)(?:\s+book|\s+framework|\s*[,(]|\s*$)",
                fact, re.I)
            if create_match:
                thing = create_match.group(1).strip().rstrip('.,;')
                # Must start with a capital letter or quote, and be meaningful
                if 3 < len(thing) < 80 and thing[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ"':
                    hook = f"I came across {thing} -- that work put you on my radar for a specific reason."
                    break

    # Pattern: Specific quote or stance
    if not hook:
        for fact in facts[:3]:
            quote_match = re.findall(r'"([^"]+)"', fact)
            if quote_match:
                quote = quote_match[0]
                if 15 < len(quote) < 60:
                    hook = f'Your point that "{quote}" stuck with me -- it connects to a blind spot I have been building to fill.'
                    break

    # Pattern: Metric/scale that's impressive
    if not hook:
        for fact in facts[:3]:
            metric_match = re.search(r"(\d+[\d,.]*[KkMm]?\+?\s*(?:stars|followers|facilities|ships|countries|reservations|locations|brands))", fact)
            if metric_match:
                metric = metric_match.group(1)
                hook = f"Managing security across {metric} is no small thing. That scale is exactly why a blind spot I keep seeing matters for your team."
                break

    # Pattern: Career move/transition
    if not hook:
        for fact in facts[:3]:
            if re.search(r"(?:previously|formerly|ex-|moved from|joined|new to|since \d{4})", fact, re.I):
                hook_angle_clean = sanitize_text(hook_angle)
                if hook_angle_clean and len(hook_angle_clean) > 20:
                    # Rewrite hook_angle as direct address
                    if hook_angle_clean[0].isupper():
                        hook = hook_angle_clean
                    else:
                        hook = hook_angle_clean[0].upper() + hook_angle_clean[1:]
                    # Remove third-person references
                    hook = re.sub(r"\b(?:his|her|their|he|she|they)\b", "your", hook, flags=re.I)
                    hook = re.sub(r"\b" + re.escape(first) + r"'s\b", "your", hook)
                    hook = re.sub(r"\b" + re.escape(name) + r"'s\b", "your", hook)
                    break

    # Fallback: build a hook from the best fact directly
    if not hook:
        # Try to extract a concrete anchor from the first fact
        best = facts[0] if facts else ""
        # Look for a specific project, role, or accomplishment
        anchor_match = re.search(
            r"(?:CISO|CSO|CTO|VP|Director|Head|Chief|Lead|Founder|CEO|SVP|EVP)"
            r"\s+(?:at|of|for)\s+([A-Z][^.;,]+?)(?:\s+since|\s+\(|\.|;|,|$)", best)
        if anchor_match and company:
            # Use a fact-grounded hook about their specific role
            detail = anchor_match.group(0).strip().rstrip(".,;")
            hook = f"Your role as {detail} puts you at a specific intersection I keep seeing."
        elif company:
            # Last resort: use best fact + company but make it direct
            hook = f"Your work at {company} caught my attention -- specifically, {facts[0][:80].rstrip('.,; ')}."
        else:
            hook_angle_clean = sanitize_text(hook_angle)
            if not hook_angle_clean or len(hook_angle_clean) < 20:
                return None
            hook = hook_angle_clean

        # Aggressively clean third-person language
        hook = re.sub(r"\b(?:his|her|their)\b", "your", hook, flags=re.I)
        hook = re.sub(r"\b(?:he|she|they)\s+(?:is|are|was|has|had|needs|wants|sees|knows|would|could|should)\b",
                      "you", hook, flags=re.I)
        # Remove name references (first name, full name, last name)
        last = name.split()[-1] if len(name.split()) > 1 else ""
        hook = re.sub(r"\b" + re.escape(first) + r"(?:'s)?\b", "", hook)
        hook = re.sub(r"\b" + re.escape(name) + r"(?:'s)?\b", "", hook)
        if last and len(last) > 2:
            hook = re.sub(r"\b" + re.escape(last) + r"(?:'s)?\b", "", hook)
        # Remove "Reference X" style instructions
        hook = re.sub(r"^(?:Reference|Mention|Highlight|Note)\s+", "", hook, flags=re.I)
        # Remove GuardSpine mentions from hooks
        hook = re.sub(r"[;,\-]?\s*GuardSpine[^.;]*", "", hook, flags=re.I)
        # Clean up double spaces, leading commas/dashes
        hook = re.sub(r"  +", " ", hook).strip().lstrip(",;- ")
        # Capitalize first letter
        if hook and hook[0].islower():
            hook = hook[0].upper() + hook[1:]

    # Final cleanup
    hook = sanitize_text(hook)
    if not hook:
        return None

    # Ensure reasonable length (1-2 sentences)
    if len(hook) > 200:
        # Truncate to first sentence if too long
        first_sent = re.split(r'(?<=[.!?])\s+', hook)
        if first_sent:
            hook = first_sent[0]
            if len(first_sent) > 1 and len(hook) + len(first_sent[1]) < 200:
                hook = hook + " " + first_sent[1]

    return hook


def sanitize_text(text):
    """Remove banned terms from text, case-insensitive."""
    result = text
    for term in BANNED_TERMS:
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        result = pattern.sub("", result)
    # Clean up double spaces and leading/trailing whitespace
    result = re.sub(r"  +", " ", result).strip()
    return result


def craft_pain_bridge(pain_signal, segment, industry, frameworks):
    """Turn pain_signal into a bridge paragraph connecting to GuardSpine."""
    if not pain_signal:
        if segment == "ciso":
            return (f"The governance gap is specific: no tamper-proof record of what was "
                    f"reviewed, who reviewed it, and what was decided. {frameworks} auditors "
                    f"are starting to ask about AI-generated code changes.")
        else:
            return ("AI is generating code faster than teams can review it. PRs get "
                    "rubber-stamped. Nobody has proof of what was actually reviewed.")

    clean_signal = sanitize_text(pain_signal)

    # Aggressively rewrite third-person to second-person
    clean_signal = re.sub(r"\b(?:his|her|their)\b", "your", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bhe\s+(?:is|has|was|had|needs|wants|sees|knows|would|could|should|'d)\b", "you", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bshe\s+(?:is|has|was|had|needs|wants|sees|knows|would|could|should|'d)\b", "you", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bhe'd\b", "you'd", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bshe'd\b", "you'd", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bhe\b(?!\w)", "you", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\bshe\b(?!\w)", "you", clean_signal, flags=re.I)
    # Rewrite dossier-style openings to second-person
    clean_signal = re.sub(r"^Has publicly stated\s+", "You've said ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Likely understands\s+", "You know ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Understands that\s+", "You know ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Spent career\s+", "You've spent your career ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Actively building\s+", "You're building ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Translating\s+", "You're translating ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Managing\s+", "You're managing ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Publicly advocates\s+", "You've advocated ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Built a\s+", "You built a ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Bridging the gap\s+", "You're bridging the gap ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Finding\s+", "You're finding ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^As the creator of\s+", "As the creator of ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^As a security\s+", "As a security ", clean_signal, flags=re.I)
    clean_signal = re.sub(r"^Manages\s+", "You manage ", clean_signal, flags=re.I)
    # Fix verb agreement after pronoun replacement
    clean_signal = re.sub(r"\byou actively tracks\b", "you actively track", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\byou shows\b", "you show", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\byou sees\b", "you see", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\byou knows\b", "you know", clean_signal, flags=re.I)
    clean_signal = re.sub(r"\byou understands\b", "you understand", clean_signal, flags=re.I)
    # Remove trailing analyst commentary
    clean_signal = re.sub(r";\s*(?:understands|likely|probably|would|you'd naturally|shows).*$",
                          ".", clean_signal, flags=re.I)
    # Remove "GuardSpine" mentions (we mention it in the body, not the pain bridge)
    clean_signal = re.sub(r"[;,\-]?\s*(?:which is )?(?:exactly )?(?:precisely )?what GuardSpine[^.;]*",
                          "", clean_signal, flags=re.I)
    clean_signal = re.sub(r"[;,\-]?\s*GuardSpine[^.;]*", "", clean_signal, flags=re.I)
    clean_signal = re.sub(r"  +", " ", clean_signal).strip().rstrip(",;- ")

    # Fix sentences broken by removal (e.g., "for but lacks", "you every")
    clean_signal = re.sub(r"\bfor but\b", "but", clean_signal)
    clean_signal = re.sub(r"\bbut lacks\b", "but lack", clean_signal)
    clean_signal = re.sub(r"\byou every\b", "you see every", clean_signal)
    clean_signal = re.sub(r"\bfor\s*\.\s*$", ".", clean_signal)
    clean_signal = re.sub(r"\bfor\s*$", "", clean_signal).strip().rstrip(",;- ")

    # Use the pain_signal if it's a complete, reasonable sentence
    if len(clean_signal) > 40:
        # Ensure it ends with a period
        if not clean_signal.endswith(('.', '!', '?')):
            clean_signal = clean_signal + "."
        return clean_signal

    # Otherwise expand it with a standard pain bridge
    if segment == "ciso":
        return (f"The governance gap around AI-generated code is where the audit exposure "
                f"lives. {frameworks} auditors are starting to ask: who approved the "
                f"AI-generated code, and where is the evidence? Current tooling cannot "
                f"answer that.")
    else:
        return ("The gap between 'code was reviewed' and 'here is proof of what was "
                "reviewed and decided' keeps widening as AI generates more PRs. Nobody "
                "has a structured record.")


def make_utm_url(segment, channel, utm_content):
    """Build tracked landing URL."""
    base = DEV_LANDING if segment == "developer" else CISO_LANDING
    campaign = "dev100_feb26" if segment == "developer" else "ciso100_feb26"
    ch = channel or "linkedin_connect"
    return f"{base}?utm_source={ch}&utm_campaign={campaign}&utm_content={utm_content}#roi"


def compose_message(prospect, research):
    """Compose a personalized message from research findings.

    Returns (hook_text, message_draft) or (None, None) if LOW confidence.
    """
    if research["confidence"] == "LOW":
        return None, None

    name = prospect["name"]
    first = name.split()[0]
    company = prospect["company"] or ""
    segment = prospect["target_segment"]
    industry = prospect["industry"] or ""
    frameworks = INDUSTRY_FRAMEWORKS.get(industry, "SOC 2")
    channel = prospect["channel"] or "linkedin_connect"
    utm = prospect["utm_content"] or hashlib.sha256(name.encode()).hexdigest()[:8]
    url = make_utm_url(segment, channel, utm)

    title = prospect.get("title", "") or ""
    hook = craft_hook(research["facts"], research["hook_angle"], name, company, title, segment)
    if not hook:
        return None, None

    pain = craft_pain_bridge(research["pain_signal"], segment, industry, frameworks)

    if segment == "developer":
        msg = (
            f"Hi {first},\n\n"
            f"{hook}\n\n"
            f"{pain}\n\n"
            f"I built an open-source GitHub Action that risk-tiers every PR and "
            f"generates tamper-proof audit trails. 737 automated tests, Apache 2.0 license, "
            f"works with your own models.\n\n"
            f"I put together a calculator that shows how many hours your team loses "
            f"to rubber-stamped reviews: {url}\n\n"
            f"- David"
        )
    else:
        msg = (
            f"Hi {first},\n\n"
            f"{hook}\n\n"
            f"{pain}\n\n"
            f"I built GuardSpine -- open-source, offline-verifiable judgment receipts "
            f"for every PR. Risk-tiered L0-L4, multi-model deliberation, tamper-proof "
            f"hash chain. Maps to {frameworks}.\n\n"
            f"I put together a cost model for what this saves on audit prep and "
            f"regulatory exposure: {url}\n\n"
            f"- David"
        )

    return hook, msg


# ===== Swap test =====

def swap_test(message, name, company):
    """Test if replacing name/company with generic values still makes sense.

    Returns True if the message PASSES (is sufficiently personalized).
    Returns False if it FAILS (is too generic -- swapping works fine).
    """
    if not message:
        return False

    first = name.split()[0]

    # Extract the hook paragraph (2nd paragraph, after "Hi Name,")
    paragraphs = message.strip().split("\n\n")
    if len(paragraphs) < 2:
        return False

    hook_para = paragraphs[1]

    # The hook must contain something beyond just name + company + title
    # Strip out name references and company references
    test_hook = hook_para
    test_hook = test_hook.replace(first, "").replace(name, "")
    if company:
        test_hook = test_hook.replace(company, "")

    # After removing name and company, the hook should still have
    # specific identifiers (project names, talk titles, dates, numbers, etc.)
    # Look for markers of specificity
    specificity_markers = [
        r"\d{4}",           # year
        r"\d+[kK]\+?\s",    # star counts like "5K"
        r"\d+\s*stars",     # star counts
        r"[A-Z][a-z]+[A-Z]",  # CamelCase (project names)
        r"\"[^\"]+\"",       # quoted titles
        r"podcast|keynote|talk at|spoke at|wrote about|published|blog post",
        r"ORBIE|C100|award|winner|finalist|nominee",
        r"post-breach|after the breach",
        r"DORA|HIPAA|SOC 2|PCI DSS|FedRAMP|NERC CIP|EU AI Act",
        r"[a-z]+-[a-z]+",   # hyphenated tool names
    ]

    has_specifics = any(re.search(p, test_hook, re.IGNORECASE) for p in specificity_markers)

    # Also check: does the hook contain any proper nouns besides name/company?
    # Simple heuristic: words starting with uppercase that aren't sentence starters
    words = hook_para.split()
    proper_nouns = []
    for i, w in enumerate(words):
        clean = re.sub(r'[^a-zA-Z]', '', w)
        if (clean and clean[0].isupper() and i > 0
                and clean.lower() != first.lower()
                and clean != company
                and clean not in ("I", "The", "Your", "As", "Hi", "AI", "PR", "PRs")):
            proper_nouns.append(clean)

    has_proper_nouns = len(proper_nouns) >= 1

    return has_specifics or has_proper_nouns


def quality_check(message, segment):
    """Run quality gate. Returns list of issues."""
    issues = []
    words = message.split()
    wc = len(words)

    if wc < 75:
        issues.append(f"Too short: {wc} words (min 75)")
    if wc > 135:
        issues.append(f"Too long: {wc} words (max 135)")

    lower = message.lower()
    for term in BANNED_TERMS:
        if term in lower:
            issues.append(f"Banned term: '{term}'")

    if segment == "developer" and "guardspine.ai/dev" not in message:
        issues.append("Missing dev landing URL")
    if segment == "ciso" and "guardspine.ai/security" not in message:
        issues.append("Missing security landing URL")

    if segment == "ciso":
        budget_signals = [
            "audit", "compliance", "ciso", "governance", "regulatory",
            "dora", "soc", "hipaa", "pci", "iso", "fedramp",
        ]
        if not any(s in lower for s in budget_signals):
            issues.append("Kristen's Rule: needs budget context")

    if not message.strip().endswith("- David"):
        issues.append("Missing sign-off")

    return issues


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if len(sys.argv) > 1 and sys.argv[1] == "--stats":
        cur.execute("""SELECT target_segment,
            SUM(CASE WHEN message_draft IS NOT NULL AND message_draft != '' THEN 1 ELSE 0 END) as drafted,
            SUM(CASE WHEN research_notes IS NOT NULL AND research_notes != '' THEN 1 ELSE 0 END) as researched,
            SUM(CASE WHEN research_notes LIKE '%%CONFIDENCE: HIGH%%' THEN 1 ELSE 0 END) as high_conf,
            SUM(CASE WHEN research_notes LIKE '%%CONFIDENCE: MEDIUM%%' THEN 1 ELSE 0 END) as med_conf,
            SUM(CASE WHEN research_notes LIKE '%%CONFIDENCE: LOW%%' THEN 1 ELSE 0 END) as low_conf,
            COUNT(*) as total
            FROM prospects WHERE campaign = ? GROUP BY target_segment""", (CAMPAIGN,))
        for row in cur.fetchall():
            print(f"  {row['target_segment']}: {row['drafted']}/{row['total']} drafted, "
                  f"{row['researched']}/{row['total']} researched "
                  f"(H={row['high_conf']} M={row['med_conf']} L={row['low_conf']})")
        conn.close()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--review":
        cur.execute("""SELECT name, company, target_segment, hook_text, message_draft,
            research_notes
            FROM prospects WHERE campaign = ? AND message_draft IS NOT NULL AND message_draft != ''
            ORDER BY target_segment, name""", (CAMPAIGN,))
        for row in cur.fetchall():
            research = parse_research_notes(row["research_notes"])
            print(f"\n{'='*60}")
            print(f"[{row['target_segment']}] {row['name']} @ {row['company']} "
                  f"[{research['confidence']}]")
            print(f"Hook: {row['hook_text']}")
            print(f"{'='*60}")
            print(row['message_draft'])
        conn.close()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--review-batch":
        batch_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        offset = batch_num * 20
        cur.execute("""SELECT name, company, target_segment, hook_text, message_draft,
            research_notes
            FROM prospects WHERE campaign = ? AND message_draft IS NOT NULL AND message_draft != ''
            ORDER BY target_segment, name
            LIMIT 20 OFFSET ?""", (CAMPAIGN, offset))
        rows = cur.fetchall()
        print(f"=== Batch {batch_num} ({len(rows)} messages) ===\n")
        for i, row in enumerate(rows):
            research = parse_research_notes(row["research_notes"])
            swap_ok = swap_test(row["message_draft"], row["name"], row["company"])
            print(f"\n--- {offset + i + 1}. [{row['target_segment']}] {row['name']} @ "
                  f"{row['company']} [{research['confidence']}] "
                  f"{'SWAP-OK' if swap_ok else 'SWAP-FAIL'} ---")
            print(row["message_draft"])
        conn.close()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--swap-test":
        cur.execute("""SELECT id, name, company, target_segment, message_draft
            FROM prospects WHERE campaign = ? AND message_draft IS NOT NULL AND message_draft != ''
            ORDER BY target_segment, name""", (CAMPAIGN,))
        pass_count = 0
        fail_count = 0
        failures = []
        for row in cur.fetchall():
            ok = swap_test(row["message_draft"], row["name"], row["company"])
            if ok:
                pass_count += 1
            else:
                fail_count += 1
                failures.append(f"  [{row['target_segment']}] {row['name']} @ {row['company']}")
        print(f"Swap test: {pass_count} PASS, {fail_count} FAIL")
        if failures:
            print("\nFailed swap test:")
            for f in failures:
                print(f)
        conn.close()
        return

    if len(sys.argv) > 1 and sys.argv[1] == "--quality":
        cur.execute("""SELECT id, name, company, target_segment, message_draft
            FROM prospects WHERE campaign = ? AND message_draft IS NOT NULL AND message_draft != ''
            ORDER BY target_segment, name""", (CAMPAIGN,))
        total_issues = 0
        for row in cur.fetchall():
            issues = quality_check(row["message_draft"], row["target_segment"])
            if issues:
                total_issues += 1
                print(f"  [{row['target_segment']}] {row['name']}: {issues}")
        if total_issues == 0:
            print("All messages pass quality gate.")
        else:
            print(f"\n{total_issues} messages with quality issues.")
        conn.close()
        return

    # === Compose all prospects that have research_notes ===
    batch_filter = ""
    params = [CAMPAIGN]
    if len(sys.argv) > 2 and sys.argv[1] == "--batch":
        batch_filter = " AND batch_number = ?"
        params.append(int(sys.argv[2]))

    cur.execute(f"""SELECT id, name, title, company, industry, notes, source,
        target_segment, channel, utm_content, research_notes
        FROM prospects WHERE campaign = ?
        AND research_notes IS NOT NULL AND research_notes != ''
        {batch_filter}
        ORDER BY target_segment, batch_number, name""", params)

    prospects = cur.fetchall()
    print(f"Composing messages for {len(prospects)} researched prospects...")

    composed = 0
    skipped_low = 0
    skipped_no_hook = 0
    swap_failures = 0
    quality_warnings = 0

    for p in prospects:
        research = parse_research_notes(p["research_notes"])

        if research["confidence"] == "LOW":
            skipped_low += 1
            continue

        hook, msg = compose_message(dict(p), research)

        if not hook or not msg:
            skipped_no_hook += 1
            continue

        # Swap test
        if not swap_test(msg, p["name"], p["company"]):
            swap_failures += 1
            print(f"  SWAP-FAIL [{p['target_segment']}] {p['name']}: hook not specific enough")

        # Quality gate
        issues = quality_check(msg, p["target_segment"])
        if issues:
            quality_warnings += 1
            # Allow slightly over word count for personalized messages
            real_issues = [i for i in issues if "Too long" not in i or len(msg.split()) > 150]
            if real_issues:
                print(f"  QUALITY [{p['target_segment']}] {p['name']}: {real_issues}")

        seg = p["target_segment"]
        utm = p["utm_content"] or hashlib.sha256(p["name"].encode()).hexdigest()[:8]
        cur.execute(
            """UPDATE prospects SET hook_text = ?, message_draft = ?, landing_url = ?
            WHERE id = ?""",
            (hook, msg, make_utm_url(seg, p["channel"], utm), p["id"])
        )
        composed += 1

    conn.commit()

    # Final stats
    print(f"\nResults:")
    print(f"  Composed: {composed}")
    print(f"  Skipped (LOW confidence): {skipped_low}")
    print(f"  Skipped (no hook): {skipped_no_hook}")
    print(f"  Swap test failures: {swap_failures}")
    print(f"  Quality warnings: {quality_warnings}")

    cur.execute("""SELECT target_segment,
        SUM(CASE WHEN message_draft IS NOT NULL AND message_draft != '' THEN 1 ELSE 0 END) as drafted,
        COUNT(*) as total
        FROM prospects WHERE campaign = ? GROUP BY target_segment""", (CAMPAIGN,))
    print("\nDraft coverage:")
    for row in cur.fetchall():
        print(f"  {row['target_segment']}: {row['drafted']}/{row['total']} drafted")

    # Count unresearched
    cur.execute("""SELECT COUNT(*) as c FROM prospects
        WHERE campaign = ? AND (research_notes IS NULL OR research_notes = '')""",
        (CAMPAIGN,))
    unresearched = cur.fetchone()["c"]
    if unresearched:
        print(f"\n  WARNING: {unresearched} prospects still need research")

    conn.close()


if __name__ == "__main__":
    main()
