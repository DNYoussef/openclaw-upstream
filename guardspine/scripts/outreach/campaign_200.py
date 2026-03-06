#!/usr/bin/env python3
"""
campaign_200.py -- 200-Person Landing Page Outreach Campaign

Manages the full lifecycle: source prospects, compose messages,
review batches, plan sends, and track attribution.

Subcommands:
    python campaign_200.py status           Show campaign dashboard
    python campaign_200.py source           Import/reclassify prospects into campaign
    python campaign_200.py compose          Draft messages for a batch
    python campaign_200.py review           Review a batch (table format)
    python campaign_200.py send-plan        Generate send plan for approval
    python campaign_200.py track            Update tracking from Plausible/Clarity
    python campaign_200.py export           Export messages for a batch (copy-paste ready)

DB: ~/.claude/outreach/outreach.db
Landing pages: guardspine.ai/dev (developers), guardspine.ai/security (CISOs)
"""

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"
CAMPAIGN_ID = "landing_page_200_feb26"

DEV_LANDING = "https://guardspine.ai/dev"
CISO_LANDING = "https://guardspine.ai/security"

# Messaging discipline (from 02-messaging-reframe.md)
# SAY THIS / NOT THIS enforcement
BANNED_TERMS = [
    # Slop phrases (from CLAUDE.md 26+ banned list)
    "delve", "leverage", "paradigm shift", "synergy", "synergize",
    "revolutionize", "transform", "unlock", "supercharge", "empower",
    "game-changing", "cutting-edge", "disruptive", "next-generation",
    "best-in-class", "thought leader", "deep dive", "holistic",
    "scalable solution", "ecosystem", "move the needle", "circle back",
    "low-hanging fruit", "boil the ocean", "at the end of the day",
    "it goes without saying",
    # Messaging discipline violations (from 02-messaging-reframe.md)
    "ai code review",       # say "code governance"
    "ai governance",        # say "artifact governance"
    "ai tool",              # say "governance tool"
    "cryptographic proof",  # say "tamper-proof audit trail"
    "evidence bundle",      # say "judgment receipt" for non-technical
    "multi-model consensus",  # say "independent verification"
    "leverage",             # never
]

# Word count bounds for outreach messages
MSG_MIN_WORDS = 70
MSG_MAX_WORDS = 140

# UTM parameter templates
UTM_TEMPLATE = (
    "utm_source={channel}&utm_campaign={campaign}&utm_content={pid}"
)

# Compliance frameworks by industry (for CISO hook personalization)
INDUSTRY_FRAMEWORKS = {
    "finance":    ["DORA", "SOC 2", "PCI DSS"],
    "banking":    ["DORA", "SOC 2", "PCI DSS"],
    "insurance":  ["DORA", "SOC 2"],
    "healthcare": ["HIPAA", "SOC 2"],
    "legal":      ["SOC 2", "ISO 27001"],
    "tech":       ["SOC 2", "EU AI Act"],
    "government": ["ISO 27001", "EU AI Act"],
    "defense":    ["ISO 27001"],
    "retail":     ["PCI DSS", "SOC 2"],
    "default":    ["SOC 2", "DORA", "HIPAA", "EU AI Act"],
}


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def prospect_id_short(prospect_id: str) -> str:
    """First 8 chars of prospect ID for UTM content tag."""
    return prospect_id[:8]


def make_utm_url(
    segment: str,
    channel: str,
    prospect_id: str,
) -> str:
    """Build a tracked landing URL with UTM params and #roi anchor."""
    base = DEV_LANDING if segment == "developer" else CISO_LANDING
    pid = prospect_id_short(prospect_id)
    campaign = "dev100_feb26" if segment == "developer" else "ciso100_feb26"
    params = UTM_TEMPLATE.format(channel=channel, campaign=campaign, pid=pid)
    return f"{base}?{params}#roi"


def generate_prospect_id(name: str, company: str) -> str:
    """Deterministic ID from name+company."""
    raw = f"{name.strip().lower()}|{(company or '').strip().lower()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


# ---------------------------------------------------------------------------
# Quality gate
# ---------------------------------------------------------------------------

def quality_check(message: str, segment: str) -> list[str]:
    """Run quality gate on a draft message. Returns list of issues."""
    issues = []
    words = message.split()
    wc = len(words)

    # Word count
    if wc < MSG_MIN_WORDS:
        issues.append(f"Too short: {wc} words (min {MSG_MIN_WORDS})")
    if wc > MSG_MAX_WORDS:
        issues.append(f"Too long: {wc} words (max {MSG_MAX_WORDS})")

    # Banned terms
    lower = message.lower()
    for term in BANNED_TERMS:
        if term in lower:
            issues.append(f"Banned term: '{term}'")

    # UTM validation
    if segment == "developer" and "guardspine.ai/dev" not in message:
        issues.append("Missing dev landing URL (guardspine.ai/dev)")
    if segment == "ciso" and "guardspine.ai/security" not in message:
        issues.append("Missing security landing URL (guardspine.ai/security)")

    # Kristen's Rule: must reference budget/buyer context for CISOs
    if segment == "ciso":
        budget_signals = [
            "audit", "compliance", "ciso", "governance", "$499",
            "drata", "vanta", "devsecops",
        ]
        if not any(s in lower for s in budget_signals):
            issues.append(
                "Kristen's Rule: CISO message must reference budget context "
                "(audit, compliance, $499, Drata comparison, etc.)"
            )

    # Sign-off check
    if not message.strip().endswith("- David"):
        issues.append("Missing sign-off '- David'")

    return issues


# ---------------------------------------------------------------------------
# Subcommand: status
# ---------------------------------------------------------------------------

def cmd_status(args):
    """Show campaign dashboard."""
    conn = get_conn()

    total = conn.execute(
        "SELECT COUNT(*) FROM prospects WHERE campaign = ?",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    by_segment = conn.execute(
        "SELECT target_segment, COUNT(*) FROM prospects "
        "WHERE campaign = ? GROUP BY target_segment",
        (CAMPAIGN_ID,),
    ).fetchall()

    with_draft = conn.execute(
        "SELECT COUNT(*) FROM prospects "
        "WHERE campaign = ? AND message_draft IS NOT NULL AND message_draft != ''",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    sent = conn.execute(
        "SELECT COUNT(*) FROM prospects "
        "WHERE campaign = ? AND message_sent_at IS NOT NULL",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    visited = conn.execute(
        "SELECT COUNT(*) FROM prospects "
        "WHERE campaign = ? AND page_visited_at IS NOT NULL",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    signups = conn.execute(
        "SELECT COUNT(*) FROM prospects "
        "WHERE campaign = ? AND signup_completed = 1",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    responses = conn.execute(
        "SELECT COUNT(*) FROM prospects "
        "WHERE campaign = ? AND response_received = 1",
        (CAMPAIGN_ID,),
    ).fetchone()[0]

    by_channel = conn.execute(
        "SELECT channel, COUNT(*) FROM prospects "
        "WHERE campaign = ? AND channel IS NOT NULL GROUP BY channel",
        (CAMPAIGN_ID,),
    ).fetchall()

    by_batch = conn.execute(
        "SELECT batch_number, COUNT(*) FROM prospects "
        "WHERE campaign = ? AND batch_number IS NOT NULL GROUP BY batch_number "
        "ORDER BY batch_number",
        (CAMPAIGN_ID,),
    ).fetchall()

    conn.close()

    print(f"\n=== Campaign: {CAMPAIGN_ID} ===\n")
    print(f"  Total prospects:  {total}/200")
    for row in by_segment:
        seg = row[0] or "unclassified"
        print(f"    {seg:12s}  {row[1]}")
    print()
    print(f"  Drafts written:   {with_draft}/{total}")
    print(f"  Messages sent:    {sent}/{total}")
    print(f"  Page visits:      {visited}")
    print(f"  Signups:          {signups}")
    print(f"  Responses:        {responses}")

    if by_channel:
        print("\n  By channel:")
        for row in by_channel:
            print(f"    {row[0]:15s}  {row[1]}")

    if by_batch:
        print("\n  By batch:")
        for row in by_batch:
            print(f"    Batch {row[0]:2d}:  {row[1]} prospects")

    print()


# ---------------------------------------------------------------------------
# Subcommand: source
# ---------------------------------------------------------------------------

def cmd_source(args):
    """Import or reclassify prospects into the campaign."""
    conn = get_conn()

    if args.action == "reclassify":
        # Tag existing builder-lane prospects as developer
        dev_tagged = conn.execute(
            "UPDATE prospects SET campaign = ?, target_segment = 'developer' "
            "WHERE lane = 'builder' AND (campaign IS NULL OR campaign = '')",
            (CAMPAIGN_ID,),
        ).rowcount

        # Tag existing buyer-lane security prospects as CISO
        ciso_tagged = conn.execute(
            "UPDATE prospects SET campaign = ?, target_segment = 'ciso' "
            "WHERE lane = 'buyer' AND (campaign IS NULL OR campaign = '') "
            "AND (title LIKE '%CISO%' OR title LIKE '%Chief Information Security%' "
            "OR title LIKE '%VP Security%' OR title LIKE '%Head of AppSec%' "
            "OR title LIKE '%Chief Security%' OR title LIKE '%Chief Compliance%' "
            "OR title LIKE '%Chief Risk%' OR title LIKE '%VP, Security%' "
            "OR title LIKE '%Director of Security%' OR title LIKE '%Director, Security%')",
            (CAMPAIGN_ID,),
        ).rowcount

        conn.commit()
        print(f"Reclassified: {dev_tagged} developers, {ciso_tagged} CISOs")
        print("Run 'status' to see totals.")

    elif args.action == "import-csv":
        # Import from a CSV file: name,title,company,industry,linkedin_url,email,segment,channel
        csv_path = Path(args.file)
        if not csv_path.exists():
            print(f"File not found: {csv_path}")
            sys.exit(1)

        import csv
        added = 0
        skipped = 0
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid = generate_prospect_id(row["name"], row.get("company", ""))
                segment = row.get("segment", "developer").strip().lower()
                channel = row.get("channel", "linkedin_dm").strip().lower()
                landing = DEV_LANDING if segment == "developer" else CISO_LANDING
                utm = prospect_id_short(pid)

                try:
                    conn.execute(
                        """INSERT INTO prospects
                        (id, name, title, company, industry, linkedin_url, email,
                         source, created_at, lane, campaign, target_segment,
                         landing_url, channel, utm_content)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            pid,
                            row["name"].strip(),
                            row.get("title", "").strip(),
                            row.get("company", "").strip(),
                            row.get("industry", "").strip(),
                            row.get("linkedin_url", "").strip(),
                            row.get("email", "").strip() or None,
                            f"campaign_200_csv_{csv_path.name}",
                            datetime.now().isoformat(),
                            "builder" if segment == "developer" else "buyer",
                            CAMPAIGN_ID,
                            segment,
                            landing,
                            channel,
                            utm,
                        ),
                    )
                    added += 1
                except sqlite3.IntegrityError:
                    skipped += 1

        conn.commit()
        print(f"Imported {added} prospects, skipped {skipped} duplicates")

    elif args.action == "add":
        # Add a single prospect interactively
        name = input("Name: ").strip()
        title = input("Title: ").strip()
        company = input("Company: ").strip()
        industry = input("Industry: ").strip()
        linkedin = input("LinkedIn URL: ").strip()
        email = input("Email (optional): ").strip() or None
        segment = input("Segment (developer/ciso): ").strip().lower()
        channel = input("Channel (linkedin_dm/email/github): ").strip().lower()

        pid = generate_prospect_id(name, company)
        landing = DEV_LANDING if segment == "developer" else CISO_LANDING
        utm = prospect_id_short(pid)

        try:
            conn.execute(
                """INSERT INTO prospects
                (id, name, title, company, industry, linkedin_url, email,
                 source, created_at, lane, campaign, target_segment,
                 landing_url, channel, utm_content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    pid, name, title, company, industry, linkedin, email,
                    "campaign_200_manual",
                    datetime.now().isoformat(),
                    "builder" if segment == "developer" else "buyer",
                    CAMPAIGN_ID, segment, landing, channel, utm,
                ),
            )
            conn.commit()
            print(f"Added: {name} ({segment}) -- ID: {pid}")
        except sqlite3.IntegrityError:
            print(f"Duplicate: {name} at {company} already exists")

    else:
        print(f"Unknown source action: {args.action}")
        print("Valid actions: reclassify, import-csv, add")

    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: compose
# ---------------------------------------------------------------------------

DEV_TEMPLATE = """Hi {first_name},

{hook}

{pain_bridge}

I built an open-source GitHub Action that risk-tiers every PR and catches logic risks -- not syntax, the stuff linters miss. 5-minute install, works with your models.

I put together a calculator showing how many hours your team loses to rubber-stamped code: {landing_url}

Free forever. $499/mo if you want the dashboard, 30-day trial.

- David"""

CISO_TEMPLATE = """Hi {first_name},

{hook}

{pain_bridge}

I built GuardSpine -- tamper-proof judgment receipts for every code change. Risk-tiered L0-L4, maps to {frameworks}. Your engineers install a GitHub Action. You get the audit trail.

I put together a cost model for what this saves on audit prep and regulatory exposure: {landing_url}

Starts at $499/mo -- less than a Drata bill.

- David"""


def cmd_compose(args):
    """Draft messages for a batch of prospects."""
    conn = get_conn()
    batch = args.batch

    # Get prospects in this batch that don't have drafts yet
    rows = conn.execute(
        "SELECT * FROM prospects WHERE campaign = ? AND batch_number = ? "
        "AND (message_draft IS NULL OR message_draft = '')",
        (CAMPAIGN_ID, batch),
    ).fetchall()

    if not rows:
        # Maybe they haven't been assigned a batch yet
        # Assign next N unassigned prospects to this batch
        limit = args.size or 20
        unassigned = conn.execute(
            "SELECT id FROM prospects WHERE campaign = ? "
            "AND (batch_number IS NULL) "
            "AND (message_draft IS NULL OR message_draft = '') "
            "ORDER BY target_segment, name LIMIT ?",
            (CAMPAIGN_ID, limit),
        ).fetchall()

        if not unassigned:
            print(f"No unassigned prospects for batch {batch}.")
            conn.close()
            return

        for row in unassigned:
            conn.execute(
                "UPDATE prospects SET batch_number = ? WHERE id = ?",
                (batch, row["id"]),
            )
        conn.commit()

        rows = conn.execute(
            "SELECT * FROM prospects WHERE campaign = ? AND batch_number = ?",
            (CAMPAIGN_ID, batch),
        ).fetchall()

    print(f"\nBatch {batch}: {len(rows)} prospects to draft\n")
    print("Each prospect needs: hook_text, company_context")
    print("Then run 'review --batch {batch}' to see the full drafts.\n")

    for row in rows:
        segment = row["target_segment"] or "developer"
        name = row["name"]
        company = row["company"] or ""
        industry = (row["industry"] or "").lower()

        # Generate UTM landing URL
        channel = row["channel"] or "linkedin_dm"
        landing_url = make_utm_url(segment, channel, row["id"])

        # Update landing_url and utm_content
        conn.execute(
            "UPDATE prospects SET landing_url = ?, utm_content = ? WHERE id = ?",
            (landing_url, prospect_id_short(row["id"]), row["id"]),
        )

        hook = row["hook_text"] or ""
        context = row["company_context"] or ""

        if not hook or not context:
            print(f"  NEEDS RESEARCH: {name} | {row['title']} | {company} | {segment}")
        else:
            # Auto-compose from template
            first_name = name.split()[0] if name else "there"
            frameworks = ", ".join(
                INDUSTRY_FRAMEWORKS.get(industry, INDUSTRY_FRAMEWORKS["default"])
            )

            if segment == "developer":
                draft = DEV_TEMPLATE.format(
                    first_name=first_name,
                    hook=hook,
                    pain_bridge=context,
                    landing_url=landing_url,
                )
            else:
                draft = CISO_TEMPLATE.format(
                    first_name=first_name,
                    hook=hook,
                    pain_bridge=context,
                    frameworks=frameworks,
                    landing_url=landing_url,
                )

            # Quality check
            issues = quality_check(draft, segment)
            status = "PASS" if not issues else f"FAIL ({len(issues)} issues)"

            conn.execute(
                "UPDATE prospects SET message_draft = ? WHERE id = ?",
                (draft, row["id"]),
            )
            print(f"  DRAFTED: {name} | {segment} | {status}")
            if issues:
                for issue in issues:
                    print(f"           ! {issue}")

    conn.commit()
    conn.close()
    print(f"\nDone. Run: python campaign_200.py review --batch {batch}")


# ---------------------------------------------------------------------------
# Subcommand: review
# ---------------------------------------------------------------------------

def cmd_review(args):
    """Review a batch in table format."""
    conn = get_conn()

    if args.batch:
        rows = conn.execute(
            "SELECT * FROM prospects WHERE campaign = ? AND batch_number = ? "
            "ORDER BY target_segment, name",
            (CAMPAIGN_ID, args.batch),
        ).fetchall()
        header = f"Batch {args.batch}"
    else:
        rows = conn.execute(
            "SELECT * FROM prospects WHERE campaign = ? "
            "AND message_draft IS NOT NULL AND message_draft != '' "
            "ORDER BY batch_number, target_segment, name",
            (CAMPAIGN_ID,),
        ).fetchall()
        header = "All drafted messages"

    if not rows:
        print("No prospects found.")
        conn.close()
        return

    print(f"\n=== {header}: {len(rows)} prospects ===\n")

    for i, row in enumerate(rows, 1):
        segment = row["target_segment"] or "?"
        draft = row["message_draft"] or "(no draft)"
        wc = len(draft.split())
        issues = quality_check(draft, segment) if draft != "(no draft)" else []
        gate = "PASS" if not issues else "FAIL"
        sent = "SENT" if row["message_sent_at"] else ""

        print(f"--- [{i}] {row['name']} | {row['title'] or '?'} | "
              f"{row['company'] or '?'} | {segment} | {gate} {sent} ---")
        print(f"    Channel: {row['channel'] or '?'} | "
              f"Email: {row['email'] or 'none'} | "
              f"Words: {wc}")

        if row["hook_text"]:
            print(f"    Hook: {row['hook_text'][:100]}")

        if draft != "(no draft)":
            # Show abbreviated draft (first 3 lines)
            lines = draft.strip().split("\n")
            for line in lines[:5]:
                print(f"    | {line}")
            if len(lines) > 5:
                print(f"    | ... ({len(lines) - 5} more lines)")

        if issues:
            for issue in issues:
                print(f"    ! {issue}")
        print()

    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: send-plan
# ---------------------------------------------------------------------------

def cmd_send_plan(args):
    """Generate send plan for user approval (pre-flight checklist)."""
    conn = get_conn()
    batch = args.batch

    rows = conn.execute(
        "SELECT * FROM prospects WHERE campaign = ? AND batch_number = ? "
        "AND message_draft IS NOT NULL AND message_draft != '' "
        "AND message_sent_at IS NULL "
        "ORDER BY channel, target_segment, name",
        (CAMPAIGN_ID, batch),
    ).fetchall()

    if not rows:
        print(f"No unsent drafted messages in batch {batch}.")
        conn.close()
        return

    print(f"\n=== SEND PLAN: Batch {batch} ({len(rows)} messages) ===")
    print("Review each row. Approve with 'y', skip with 'n'.\n")

    # Group by channel
    by_channel: dict[str, list] = {}
    for row in rows:
        ch = row["channel"] or "unknown"
        by_channel.setdefault(ch, []).append(row)

    for channel, prospects in by_channel.items():
        print(f"\n--- {channel.upper()} ({len(prospects)} messages) ---\n")
        print(f"{'#':>3}  {'Name':25s}  {'Company':20s}  {'Segment':10s}  "
              f"{'Email':30s}  {'QG':5s}")
        print("-" * 100)

        for i, row in enumerate(prospects, 1):
            segment = row["target_segment"] or "?"
            email = row["email"] or "N/A"
            issues = quality_check(row["message_draft"], segment)
            gate = "PASS" if not issues else "FAIL"

            # Flag unverified emails
            email_flag = ""
            if channel == "email" and not row["email"]:
                email_flag = " [NO EMAIL]"
            elif channel == "email" and row["email"]:
                # Check for guessed patterns
                if row.get("source", "").startswith("pattern_"):
                    email_flag = " [GUESSED]"

            print(f"{i:3d}  {row['name']:25s}  {(row['company'] or ''):20s}  "
                  f"{segment:10s}  {email:30s}  {gate}{email_flag}")

    print(f"\n=== END SEND PLAN ===")
    print(f"Total: {len(rows)} messages")
    print("To mark as sent: python campaign_200.py mark-sent --batch", batch)

    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: mark-sent
# ---------------------------------------------------------------------------

def cmd_mark_sent(args):
    """Mark batch as sent (after manual sending)."""
    conn = get_conn()
    now = datetime.now().isoformat()

    updated = conn.execute(
        "UPDATE prospects SET message_sent_at = ? "
        "WHERE campaign = ? AND batch_number = ? "
        "AND message_draft IS NOT NULL AND message_sent_at IS NULL",
        (now, CAMPAIGN_ID, args.batch),
    ).rowcount

    conn.commit()
    conn.close()
    print(f"Marked {updated} messages as sent (batch {args.batch})")


# ---------------------------------------------------------------------------
# Subcommand: track
# ---------------------------------------------------------------------------

def cmd_track(args):
    """Update tracking data (page visits, signups, responses)."""
    conn = get_conn()

    if args.action == "visit":
        # Mark a prospect as having visited the landing page
        updated = conn.execute(
            "UPDATE prospects SET page_visited_at = ? WHERE id = ? OR utm_content = ?",
            (datetime.now().isoformat(), args.prospect_id, args.prospect_id),
        ).rowcount
        conn.commit()
        print(f"Marked {updated} prospect(s) as visited")

    elif args.action == "signup":
        updated = conn.execute(
            "UPDATE prospects SET signup_completed = 1 WHERE id = ? OR utm_content = ?",
            (args.prospect_id, args.prospect_id),
        ).rowcount
        conn.commit()
        print(f"Marked {updated} prospect(s) as signed up")

    elif args.action == "response":
        updated = conn.execute(
            "UPDATE prospects SET response_received = 1, signal_type = 'green', "
            "signal_notes = ? WHERE id = ?",
            (args.notes or "", args.prospect_id),
        ).rowcount
        conn.commit()
        print(f"Marked {updated} prospect(s) as responded")

    elif args.action == "summary":
        # Show tracking summary
        sent = conn.execute(
            "SELECT COUNT(*) FROM prospects WHERE campaign = ? AND message_sent_at IS NOT NULL",
            (CAMPAIGN_ID,),
        ).fetchone()[0]
        visits = conn.execute(
            "SELECT COUNT(*) FROM prospects WHERE campaign = ? AND page_visited_at IS NOT NULL",
            (CAMPAIGN_ID,),
        ).fetchone()[0]
        signups = conn.execute(
            "SELECT COUNT(*) FROM prospects WHERE campaign = ? AND signup_completed = 1",
            (CAMPAIGN_ID,),
        ).fetchone()[0]
        responses = conn.execute(
            "SELECT COUNT(*) FROM prospects WHERE campaign = ? AND response_received = 1",
            (CAMPAIGN_ID,),
        ).fetchone()[0]

        visit_rate = (visits / sent * 100) if sent else 0
        signup_rate = (signups / sent * 100) if sent else 0
        response_rate = (responses / sent * 100) if sent else 0

        print(f"\n=== ATTRIBUTION TRACKING ===\n")
        print(f"  Sent:       {sent}")
        print(f"  Visits:     {visits}  ({visit_rate:.1f}%)")
        print(f"  Signups:    {signups}  ({signup_rate:.1f}%)")
        print(f"  Responses:  {responses}  ({response_rate:.1f}%)")

        # By segment
        for seg in ("developer", "ciso"):
            seg_sent = conn.execute(
                "SELECT COUNT(*) FROM prospects WHERE campaign = ? "
                "AND target_segment = ? AND message_sent_at IS NOT NULL",
                (CAMPAIGN_ID, seg),
            ).fetchone()[0]
            seg_visits = conn.execute(
                "SELECT COUNT(*) FROM prospects WHERE campaign = ? "
                "AND target_segment = ? AND page_visited_at IS NOT NULL",
                (CAMPAIGN_ID, seg),
            ).fetchone()[0]
            vr = (seg_visits / seg_sent * 100) if seg_sent else 0
            print(f"\n  {seg:10s}:  {seg_sent} sent, {seg_visits} visits ({vr:.1f}%)")

        print()

    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: export
# ---------------------------------------------------------------------------

def cmd_export(args):
    """Export messages for copy-paste sending."""
    conn = get_conn()

    rows = conn.execute(
        "SELECT * FROM prospects WHERE campaign = ? AND batch_number = ? "
        "AND message_draft IS NOT NULL AND message_draft != '' "
        "ORDER BY channel, target_segment, name",
        (CAMPAIGN_ID, args.batch),
    ).fetchall()

    if not rows:
        print(f"No messages in batch {args.batch}")
        conn.close()
        return

    if args.format == "text":
        for i, row in enumerate(rows, 1):
            print(f"\n{'='*60}")
            print(f"TO: {row['name']} ({row['channel'] or 'linkedin_dm'})")
            if row["email"]:
                print(f"EMAIL: {row['email']}")
            if row["linkedin_url"]:
                print(f"LINKEDIN: {row['linkedin_url']}")
            print(f"{'='*60}")
            print(row["message_draft"])
            print()

    elif args.format == "json":
        out = []
        for row in rows:
            out.append({
                "id": row["id"],
                "name": row["name"],
                "channel": row["channel"],
                "email": row["email"],
                "linkedin_url": row["linkedin_url"],
                "segment": row["target_segment"],
                "message": row["message_draft"],
            })
        print(json.dumps(out, indent=2))

    conn.close()


# ---------------------------------------------------------------------------
# Subcommand: set-hook (batch update hook_text and company_context)
# ---------------------------------------------------------------------------

def cmd_set_hook(args):
    """Set hook_text and company_context for a prospect, then auto-compose."""
    conn = get_conn()

    row = conn.execute(
        "SELECT * FROM prospects WHERE id = ? OR name LIKE ?",
        (args.prospect_id, f"%{args.prospect_id}%"),
    ).fetchone()

    if not row:
        print(f"Prospect not found: {args.prospect_id}")
        conn.close()
        return

    print(f"Prospect: {row['name']} | {row['title']} | {row['company']}")
    print(f"Segment: {row['target_segment']}")

    hook = args.hook or input("Hook text (1-2 sentences): ").strip()
    context = args.context or input("Pain bridge / company context: ").strip()

    conn.execute(
        "UPDATE prospects SET hook_text = ?, company_context = ? WHERE id = ?",
        (hook, context, row["id"]),
    )

    # Auto-compose
    segment = row["target_segment"] or "developer"
    channel = row["channel"] or "linkedin_dm"
    landing_url = make_utm_url(segment, channel, row["id"])
    first_name = row["name"].split()[0] if row["name"] else "there"
    industry = (row["industry"] or "").lower()
    frameworks = ", ".join(
        INDUSTRY_FRAMEWORKS.get(industry, INDUSTRY_FRAMEWORKS["default"])
    )

    if segment == "developer":
        draft = DEV_TEMPLATE.format(
            first_name=first_name,
            hook=hook,
            pain_bridge=context,
            landing_url=landing_url,
        )
    else:
        draft = CISO_TEMPLATE.format(
            first_name=first_name,
            hook=hook,
            pain_bridge=context,
            frameworks=frameworks,
            landing_url=landing_url,
        )

    issues = quality_check(draft, segment)
    conn.execute(
        "UPDATE prospects SET message_draft = ?, landing_url = ?, utm_content = ? "
        "WHERE id = ?",
        (draft, landing_url, prospect_id_short(row["id"]), row["id"]),
    )
    conn.commit()

    print(f"\nDraft composed ({len(draft.split())} words):")
    print(draft)

    if issues:
        print(f"\nQuality gate issues ({len(issues)}):")
        for issue in issues:
            print(f"  ! {issue}")
    else:
        print("\nQuality gate: PASS")

    conn.close()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="200-person landing page outreach campaign",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Campaign dashboard")

    # source
    p_source = sub.add_parser("source", help="Import/reclassify prospects")
    p_source.add_argument(
        "action",
        choices=["reclassify", "import-csv", "add"],
        help="reclassify: tag existing DB prospects | import-csv: bulk import | add: single prospect",
    )
    p_source.add_argument("--file", help="CSV file path (for import-csv)")

    # compose
    p_compose = sub.add_parser("compose", help="Draft messages for a batch")
    p_compose.add_argument("--batch", type=int, required=True, help="Batch number")
    p_compose.add_argument("--size", type=int, default=20, help="Batch size (default 20)")

    # review
    p_review = sub.add_parser("review", help="Review batch messages")
    p_review.add_argument("--batch", type=int, help="Batch number (or all)")

    # send-plan
    p_send = sub.add_parser("send-plan", help="Generate send plan for approval")
    p_send.add_argument("--batch", type=int, required=True, help="Batch number")

    # mark-sent
    p_mark = sub.add_parser("mark-sent", help="Mark batch as sent")
    p_mark.add_argument("--batch", type=int, required=True, help="Batch number")

    # track
    p_track = sub.add_parser("track", help="Update tracking data")
    p_track.add_argument(
        "action",
        choices=["visit", "signup", "response", "summary"],
        help="Tracking action",
    )
    p_track.add_argument("--prospect-id", help="Prospect ID or UTM content tag")
    p_track.add_argument("--notes", help="Notes (for response)")

    # export
    p_export = sub.add_parser("export", help="Export messages for copy-paste")
    p_export.add_argument("--batch", type=int, required=True, help="Batch number")
    p_export.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format",
    )

    # set-hook
    p_hook = sub.add_parser("set-hook", help="Set hook + context for a prospect")
    p_hook.add_argument("prospect_id", help="Prospect ID or name substring")
    p_hook.add_argument("--hook", help="Hook text")
    p_hook.add_argument("--context", help="Pain bridge / company context")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "status": cmd_status,
        "source": cmd_source,
        "compose": cmd_compose,
        "review": cmd_review,
        "send-plan": cmd_send_plan,
        "mark-sent": cmd_mark_sent,
        "track": cmd_track,
        "export": cmd_export,
        "set-hook": cmd_set_hook,
    }

    dispatch[args.command](args)


if __name__ == "__main__":
    main()
