# GuardSpine Autonomous Operations

Operational scripts for daily synthesis, decision tracking, health monitoring,
and workflow maturity assessment.

## Scripts

| Script                  | Purpose                                            | Entry Point                              |
| ----------------------- | -------------------------------------------------- | ---------------------------------------- |
| `run_autonomous_ops.py` | Orchestrator -- combines all modules               | `python run_autonomous_ops.py <command>` |
| `daily_synthesis.py`    | Morning state briefing (pipeline, git, priorities) | Imported by runner                       |
| `decision_journal.py`   | Log and analyze manual decisions                   | Imported by runner                       |
| `workflow_health.py`    | Health checks + maturity level tracking            | Imported by runner                       |
| `morning.bat`           | Windows launcher for morning briefing              | Double-click or CLI                      |

## Commands

```
python run_autonomous_ops.py morning    # Synthesis + health + recent decisions
python run_autonomous_ops.py health     # Health checks only
python run_autonomous_ops.py report     # Full report (all modules + maturity + 30d decisions)
python run_autonomous_ops.py status     # Quick one-liner status
python run_autonomous_ops.py help       # Show usage
```

## Quick Start

```bash
# One-liner status
python scripts/autonomous/run_autonomous_ops.py status

# Morning briefing
python scripts/autonomous/run_autonomous_ops.py morning

# Or use the bat file (Windows)
scripts\autonomous\morning.bat
```

## Slack Integration

Set the `SLACK_WEBHOOK_URL` environment variable to auto-post briefings:

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/T.../B.../xxx"
python run_autonomous_ops.py morning
```

## Scheduling (Windows Task Scheduler)

1. Open Task Scheduler (`taskschd.msc`)
2. Create Basic Task: "GuardSpine Morning Briefing"
3. Trigger: Daily at 08:00
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\Users\17175\scripts\autonomous\run_autonomous_ops.py morning`
   - Start in: `C:\Users\17175\scripts\autonomous`
5. Optionally set `SLACK_WEBHOOK_URL` in the task environment

For Git Bash cron (if available):

```
# crontab -e
0 8 * * 1-5 python /c/Users/17175/scripts/autonomous/run_autonomous_ops.py morning
```

## Database

All operational data lives in `~/.claude/autonomous/ops.db` (SQLite).

### Schema Overview

**decisions** -- manual decisions logged via decision_journal.py:

- id, timestamp, category, decision, context, alternatives, automatable (bool)

**health_snapshots** -- periodic health check results:

- id, timestamp, check_name, status (ok/warn/crit), message

**workflow_maturity** -- maturity level per workflow:

- id, workflow_name, current_level (0-5), last_assessed, notes

**daily_summaries** -- daily synthesis snapshots:

- id, date, pipeline_stats, git_stats, priorities, raw_json

## Architecture

```
                    +---------------------+
                    |  run_autonomous_ops |
                    |    (orchestrator)   |
                    +-----+------+-------+
                          |      |       |
               +----------+    |    +----------+
               |               |               |
    +----------v--+  +---------v---+  +--------v-------+
    | daily_      |  | decision_   |  | workflow_      |
    | synthesis   |  | journal     |  | health         |
    +------+------+  +------+------+  +-------+--------+
           |                |                  |
           +--------+-------+------------------+
                    |
              +-----v------+
              |   ops.db   |
              |  (SQLite)  |
              +-----+------+
                    |
         +----------+----------+
         |                     |
   +-----v------+     +-------v-------+
   | outreach.db |     | memory-mcp   |
   | (read-only) |     | agent_kv.db  |
   +-----------+       | (read-only)  |
                       +--------------+
```

The runner imports each module and calls its public functions. If a module
is missing or fails, the runner skips it with a `[SKIP]` or `[WARN]` message
and continues with the remaining modules.

## Dependencies

Pure Python 3 standard library. No pip install required.

- sqlite3 (stdlib) for database access
- urllib.request (stdlib) for Slack webhook
- importlib (stdlib) for dynamic module loading
- subprocess (stdlib) for git commands
