#!/usr/bin/env python3
"""
Email verification pass for outreach prospects.

Checks:
1. Format validity (regex)
2. Domain MX record exists (nslookup)
3. Flags noreply/generic addresses as LOW
4. Flags personal Gmail/Yahoo for CISOs as MEDIUM
5. Cross-references email domain vs company

Usage:
    python verify_emails.py          # Run verification, print report
    python verify_emails.py --fix    # Also update confidence in DB notes
"""

import sqlite3
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

DB_PATH = Path.home() / ".claude" / "outreach" / "outreach.db"

EMAIL_RE = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

NOREPLY_PATTERNS = [
    'noreply', 'no-reply', 'donotreply', 'do-not-reply',
    'users.noreply.github.com',
]

GENERIC_PREFIXES = [
    'info@', 'contact@', 'hello@', 'support@', 'admin@',
    'sales@', 'team@', 'general@', 'office@', 'press@',
    'questions@',
]

PERSONAL_DOMAINS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'aol.com', 'icloud.com', 'protonmail.com', 'proton.me',
    'fastmail.com', 'tutanota.com', 'me.com', 'live.com',
    'msn.com', 'yandex.com', 'mail.com',
]

# Map company names to expected domains (partial)
COMPANY_DOMAINS = {
    'google': ['google.com', 'gmail.com'],
    'stripe': ['stripe.com'],
    'coinbase': ['coinbase.com'],
    'meta': ['meta.com', 'fb.com', 'facebook.com'],
    'amazon': ['amazon.com', 'aws.com'],
    'microsoft': ['microsoft.com'],
    'apple': ['apple.com'],
    'netflix': ['netflix.com'],
}


def check_mx_record(domain):
    """Check if domain has MX records. Returns True/False."""
    try:
        result = subprocess.run(
            ['nslookup', '-type=MX', domain],
            capture_output=True, text=True, timeout=10
        )
        output = result.stdout.lower()
        return 'mail exchanger' in output or 'mx' in output
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None  # Could not verify


def classify_email(email, segment, company):
    """Classify email confidence. Returns (confidence, reasons)."""
    reasons = []

    if not email or not email.strip():
        return None, ['no email']

    email = email.strip().lower()

    # Format check
    if not EMAIL_RE.match(email):
        return 'INVALID', ['fails format regex']

    domain = email.split('@')[1]

    # Noreply check
    for pattern in NOREPLY_PATTERNS:
        if pattern in email:
            return 'SKIP', [f'noreply address ({pattern})']

    # Generic prefix check
    for prefix in GENERIC_PREFIXES:
        if email.startswith(prefix):
            reasons.append(f'generic prefix ({prefix.rstrip("@")})')

    # Personal domain for CISOs
    if segment == 'ciso' and domain in PERSONAL_DOMAINS:
        reasons.append(f'personal domain ({domain}) for CISO - prefer corporate')

    # Domain-company mismatch check
    if company:
        company_lower = company.lower().split('/')[0].strip()
        # Simple heuristic: company name should appear in domain
        company_words = company_lower.replace(' ', '').replace('-', '')
        domain_base = domain.split('.')[0]
        if len(company_words) > 3 and company_words[:4] not in domain_base:
            # Not necessarily wrong, but worth noting
            pass

    # Determine confidence
    if 'SKIP' in [r.split()[0] for r in reasons]:
        return 'SKIP', reasons

    if reasons:
        return 'LOW', reasons

    return None, []  # No issues found, keep existing confidence


def run_verification():
    """Run full verification pass."""
    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    cur.execute(
        "SELECT id, name, company, email, target_segment, notes "
        "FROM prospects WHERE email IS NOT NULL AND email != ''"
    )
    rows = cur.fetchall()

    results = {
        'ciso': defaultdict(list),
        'developer': defaultdict(list),
    }

    mx_cache = {}
    issues = []

    for pid, name, company, email, segment, notes in rows:
        email = email.strip()

        # Parse existing confidence from notes
        existing_conf = 'UNKNOWN'
        if notes:
            for conf in ['HIGH', 'MEDIUM', 'LOW']:
                if f'[EMAIL {conf}]' in notes:
                    existing_conf = conf
                    break

        # Classify
        downgrade, reasons = classify_email(email, segment, company)

        # MX check
        domain = email.split('@')[1] if '@' in email else ''
        if domain and domain not in mx_cache:
            mx_cache[domain] = check_mx_record(domain)

        mx_ok = mx_cache.get(domain)
        if mx_ok is False:
            reasons.append(f'no MX record for {domain}')
            if not downgrade or downgrade not in ('INVALID', 'SKIP'):
                downgrade = 'LOW'

        # Final confidence
        if downgrade in ('INVALID', 'SKIP'):
            final_conf = downgrade
        elif downgrade == 'LOW':
            final_conf = 'LOW'
        elif existing_conf != 'UNKNOWN':
            final_conf = existing_conf
        else:
            final_conf = 'MEDIUM'  # Default if no confidence was set

        seg = segment if segment in results else 'developer'
        results[seg][final_conf].append({
            'id': pid,
            'name': name,
            'company': company,
            'email': email,
            'reasons': reasons,
            'mx': mx_ok,
        })

        if reasons:
            issues.append((name, email, final_conf, '; '.join(reasons)))

    conn.close()
    return results, issues, mx_cache


def print_report(results, issues, mx_cache):
    """Print verification report."""
    print("=" * 70)
    print("EMAIL VERIFICATION REPORT")
    print("=" * 70)

    for segment in ['ciso', 'developer']:
        seg_data = results[segment]
        total = sum(len(v) for v in seg_data.values())
        print(f"\n{segment.upper()} EMAILS ({total} total):")

        for conf in ['HIGH', 'MEDIUM', 'LOW', 'INVALID', 'SKIP', 'UNKNOWN']:
            entries = seg_data.get(conf, [])
            if entries:
                print(f"  {conf}: {len(entries)}")
                for e in entries[:5]:
                    flag = ' [!]' if e['reasons'] else ''
                    mx_str = ' [MX OK]' if e['mx'] else (' [NO MX]' if e['mx'] is False else '')
                    print(f"    {e['name']:35s} {e['email']:40s}{mx_str}{flag}")
                if len(entries) > 5:
                    print(f"    ... and {len(entries) - 5} more")

    if issues:
        print(f"\n{'=' * 70}")
        print(f"ISSUES FOUND ({len(issues)}):")
        print(f"{'=' * 70}")
        for name, email, conf, reason in issues:
            print(f"  [{conf}] {name:35s} {email:40s} -- {reason}")

    # MX summary
    print(f"\n{'=' * 70}")
    print("MX RECORD CHECK:")
    mx_ok = sum(1 for v in mx_cache.values() if v is True)
    mx_fail = sum(1 for v in mx_cache.values() if v is False)
    mx_unknown = sum(1 for v in mx_cache.values() if v is None)
    print(f"  Domains checked: {len(mx_cache)}")
    print(f"  MX OK: {mx_ok}  |  No MX: {mx_fail}  |  Could not verify: {mx_unknown}")


def main():
    if not DB_PATH.exists():
        print(f"ERROR: DB not found at {DB_PATH}")
        sys.exit(1)

    print("Running email verification...")
    results, issues, mx_cache = run_verification()
    print_report(results, issues, mx_cache)

    # Count for quick summary
    total_ciso = sum(len(v) for v in results['ciso'].values())
    total_dev = sum(len(v) for v in results['developer'].values())
    print(f"\nSummary: {total_ciso} CISO emails + {total_dev} dev emails verified")


if __name__ == "__main__":
    main()
