#!/usr/bin/env python3
"""
Generate the day-by-day send plan for the 200-person campaign.

Rate limits:
  - LinkedIn connection requests (no note): 80/week
  - LinkedIn personalized connection notes: 3/week
  - LinkedIn DMs to 1st connections: 20/day
  - Cold email via Gmail: 15/day

Output: a day-by-day schedule with specific names and channels.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.claude/outreach/outreach.db")
CAMPAIGN = "landing_page_200_feb26"

# Start date: Day 7 of campaign = Feb 28, 2026 (Friday)
# But we can start sending now since messages are ready
START_DATE = datetime(2026, 2, 23)  # Tomorrow (Sunday)


def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Get all campaign prospects grouped by channel
    cur.execute("""SELECT id, name, title, company, target_segment, channel, email,
        message_sent_at, batch_number
        FROM prospects WHERE campaign = ?
        ORDER BY channel, target_segment, batch_number, name""", (CAMPAIGN,))
    prospects = cur.fetchall()

    # Split by channel
    email_prospects = [p for p in prospects if p["channel"] == "email" and not p["message_sent_at"]]
    dm_prospects = [p for p in prospects if p["channel"] == "linkedin_dm" and not p["message_sent_at"]]
    connect_prospects = [p for p in prospects if p["channel"] == "linkedin_connect" and not p["message_sent_at"]]
    already_sent = [p for p in prospects if p["message_sent_at"]]

    print(f"=== SEND PLAN: {CAMPAIGN} ===")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"\nAlready sent: {len(already_sent)}")
    print(f"To send: {len(email_prospects)} email, {len(dm_prospects)} LinkedIn DM, {len(connect_prospects)} LinkedIn connect")
    print(f"Total remaining: {len(email_prospects) + len(dm_prospects) + len(connect_prospects)}")

    # === Day-by-day schedule ===
    day = 0
    email_idx = 0
    dm_idx = 0
    connect_idx = 0
    daily_plans = []

    # Phase A: Days 1-3 -- LinkedIn connects (batch of 40/day) + DMs (20/day) + emails (15/day)
    for d in range(3):
        date = START_DATE + timedelta(days=d)
        plan = {"date": date, "actions": []}

        # LinkedIn connects: 40/day (stay under 80/week)
        batch_connects = connect_prospects[connect_idx:connect_idx + 40]
        if batch_connects:
            plan["actions"].append(("LinkedIn Connect (no note)", batch_connects))
            connect_idx += len(batch_connects)

        # LinkedIn DMs: 20/day
        batch_dms = dm_prospects[dm_idx:dm_idx + 20]
        if batch_dms:
            plan["actions"].append(("LinkedIn DM", batch_dms))
            dm_idx += len(batch_dms)

        # Emails: 15/day
        batch_emails = email_prospects[email_idx:email_idx + 15]
        if batch_emails:
            plan["actions"].append(("Cold Email", batch_emails))
            email_idx += len(batch_emails)

        if plan["actions"]:
            daily_plans.append(plan)

    # Phase B: Days 4-7 -- DM newly accepted connections + remaining emails
    for d in range(3, 7):
        date = START_DATE + timedelta(days=d)
        plan = {"date": date, "actions": []}

        # Remaining connects
        batch_connects = connect_prospects[connect_idx:connect_idx + 20]
        if batch_connects:
            plan["actions"].append(("LinkedIn Connect (remaining)", batch_connects))
            connect_idx += len(batch_connects)

        # Remaining DMs
        batch_dms = dm_prospects[dm_idx:dm_idx + 15]
        if batch_dms:
            plan["actions"].append(("LinkedIn DM", batch_dms))
            dm_idx += len(batch_dms)

        # Remaining emails
        batch_emails = email_prospects[email_idx:email_idx + 5]
        if batch_emails:
            plan["actions"].append(("Cold Email", batch_emails))
            email_idx += len(batch_emails)

        if plan["actions"]:
            daily_plans.append(plan)

    # Phase C: Days 8-14 -- DM newly accepted from Phase A + catch-up
    for d in range(7, 14):
        date = START_DATE + timedelta(days=d)
        plan = {"date": date, "actions": []}

        remaining_connects = connect_prospects[connect_idx:connect_idx + 10]
        if remaining_connects:
            plan["actions"].append(("LinkedIn Connect (catch-up)", remaining_connects))
            connect_idx += len(remaining_connects)

        remaining_dms = dm_prospects[dm_idx:dm_idx + 10]
        if remaining_dms:
            plan["actions"].append(("LinkedIn DM (catch-up)", remaining_dms))
            dm_idx += len(remaining_dms)

        if plan["actions"]:
            daily_plans.append(plan)

    # Print the plan
    total_scheduled = 0
    for plan in daily_plans:
        date_str = plan["date"].strftime("%a %b %d")
        day_total = sum(len(batch) for _, batch in plan["actions"])
        total_scheduled += day_total
        print(f"\n--- {date_str} ({day_total} touches) ---")
        for channel_name, batch in plan["actions"]:
            print(f"  {channel_name} ({len(batch)}):")
            for p in batch[:5]:  # Show first 5
                seg = "DEV" if p["target_segment"] == "developer" else "CISO"
                print(f"    [{seg}] {p['name']} @ {p['company']}")
            if len(batch) > 5:
                print(f"    ... and {len(batch) - 5} more")

    # Unscheduled
    remaining = (len(connect_prospects) - connect_idx) + (len(dm_prospects) - dm_idx) + (len(email_prospects) - email_idx)
    print(f"\n=== SUMMARY ===")
    print(f"Total scheduled: {total_scheduled}")
    print(f"Already sent: {len(already_sent)}")
    print(f"Unscheduled (will DM after accepts): {remaining}")
    print(f"Grand total: {total_scheduled + len(already_sent) + remaining}/200")

    conn.close()


if __name__ == "__main__":
    main()
