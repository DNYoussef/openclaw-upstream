# Handoff Context

> **USAGE:** Copy this template to `handoff-{TIMESTAMP}.md` before spawning a sub-agent.
> The sub-agent's first action should be to read this file.
> Delete handoff files older than 24 hours.

---

- **From:** [session ID, max 20 chars]
- **Timestamp:** [ISO8601 UTC, e.g., 2026-02-03T16:00:00Z]
- **Task:** [max 100 chars - what we're trying to accomplish]

## Key Facts (MAX 5 bullets, MAX 50 chars each)

1.
2.
3.
4.
5.

## Active Files (MAX 3 most relevant)

-
-
-

## Next Action (MAX 100 chars)

[What the sub-agent should do first upon reading this]

---

## Example (filled in)

- **From:** gs-session-abc123
- **Timestamp:** 2026-02-03T16:30:00Z
- **Task:** Fix authentication bug in Discord gateway

## Key Facts

1. Bug: token refresh fails after 24h
2. File: plugin.js line 180-220
3. Root cause: missing retry logic
4. Tests passing locally
5. Need to verify on staging

## Active Files

- ~/.openclaw/extensions/guardspine/plugin.js
- ~/.openclaw/guardspine-logs/debug.log

## Next Action

Add exponential backoff to token refresh in refreshDiscordToken()
