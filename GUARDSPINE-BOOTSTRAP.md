# GuardSpine Fork: Bootstrap & Test Guide

This document catalogs every local addition to our OpenClaw fork,
how to verify each one works after an upstream merge, and how to
bootstrap them from scratch if something breaks.

Fork: `DNYoussef/openclaw-upstream` (based on `openclaw/openclaw`)
Last upstream merge: v2026.3.8 (2026-03-10)
Local additions: 57 commits, ~500 files

---

## 1. Railway Deployment Infrastructure

### Files

- `Dockerfile.railway` -- Custom multi-stage Docker build for Railway
- `docker/entrypoint.sh` -- Permission fix (chown volume dirs, drop to non-root)
- `docker/railway-entrypoint.sh` -- Alternative entrypoint with config seeding
- `docker/railway-config.json` -- Gateway config (models, auth, Slack, extensions)
- `.railwayignore` -- Reduces build context size

### Environment Variables (Railway dashboard)

```
OPENCLAW_GATEWAY_TOKEN=<shared secret for Control UI auth>
OPENCLAW_STATE_DIR=/app/.openclaw
LITELLM_BASE_URL=http://litellm.railway.internal:4000
LITELLM_API_KEY=<litellm master key>
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...
```

### Test: Docker build

```bash
docker build -f Dockerfile.railway -t openclaw-railway .
```

### Test: Config loads

```bash
# Inside container or locally:
node -e "const c = require('./docker/railway-config.json'); console.log(c.gateway.port, c.agents.defaults.model.primary)"
# Expected: 18789 litellm/openrouter/anthropic/claude-sonnet-4.5
```

### Test: Health check (live)

```bash
curl -s -o /dev/null -w "%{http_code}" https://openclaw-production-4349.up.railway.app/
# Expected: 200
```

### Bootstrap from scratch

1. Create Railway project with 3 services: litellm, n8n, openclaw
2. Set env vars listed above
3. Connect GitHub repo `DNYoussef/openclaw-upstream`, branch `main`
4. Railway auto-detects `Dockerfile.railway`
5. Verify: gateway logs show `listening on ws://0.0.0.0:18789`

---

## 2. Gateway Auth & Control UI

### Files

- `docker/railway-config.json` -- `controlUi.allowedOrigins`, `dangerouslyDisableDeviceAuth`

### Config keys

```json
{
  "gateway": {
    "controlUi": {
      "allowedOrigins": ["https://openclaw-production-4349.up.railway.app"],
      "dangerouslyDisableDeviceAuth": true
    }
  }
}
```

### Test: Control UI connects

1. Open `https://openclaw-production-4349.up.railway.app/chat?session=main`
2. Verify: chat interface loads, no "origin not allowed" or "pairing required" errors
3. Send a test message, verify AI responds

### Test: Token auth

```bash
# Gateway logs should show:
# [ws] webchat connected conn=... client=openclaw-control-ui webchat vdev
# NOT: unauthorized ... reason=token_missing
```

### If broken after merge

- Check `docker/railway-config.json` still has `dangerouslyDisableDeviceAuth: true`
- Check `OPENCLAW_GATEWAY_TOKEN` env var is set in Railway dashboard
- Check browser localStorage key `openclaw.control.settings.v1` has matching token
- Auth flow: `src/gateway/credentials.ts:50` reads `OPENCLAW_GATEWAY_TOKEN` from env
- Pairing bypass: `src/gateway/server/ws-connection/connect-policy.ts:25`

---

## 3. AI Model Configuration

### Files

- `docker/railway-config.json` -- `agents.defaults.model`, `models.providers.litellm`

### Models configured

| Model             | Role             | Cost (in/out per 1M) |
| ----------------- | ---------------- | -------------------- |
| Claude Sonnet 4.5 | Primary          | $3 / $15             |
| DeepSeek V3.2     | Budget fallback  | $0.25 / $0.40        |
| Gemini 2.5 Flash  | Fast + reasoning | $0.30 / $2.50        |
| Qwen3 Coder       | Code specialist  | $0.22 / $1.00        |
| Claude Opus 4.6   | High-complexity  | $5 / $25             |

### Test: End-to-end inference

```
# In Control UI, send: "What model are you? Reply in one sentence."
# Expected: Response mentioning Claude Sonnet 4.5
```

### Test: Model routing

```bash
# Gateway logs should show:
# [gateway] agent model: litellm/openrouter/anthropic/claude-sonnet-4.5
```

### If broken after merge

- Verify LiteLLM service is running: `curl http://litellm.railway.internal:4000/health`
- Verify OpenRouter API key is set in LiteLLM env vars
- Model ID format: `openrouter/anthropic/claude-sonnet-4.5` (NOT `anthropic/claude-4.5-sonnet`)
- LiteLLM routes `openrouter/*` prefix to OpenRouter API automatically

---

## 4. GuardSpine Extension (OpenClaw Plugin)

### Files

- `guardspine/extensions/guardspine/plugin.js` -- Main plugin (~2300 lines)
- `guardspine/extensions/guardspine/test-slack-smoke.js` -- Smoke tests
- `guardspine/extensions/n8n-pipeline/plugin.js` -- n8n integration plugin

### What it does

- Intercepts AI tool calls for governance review (L0-L4 risk tiers)
- Produces evidence packs with cryptographic seals
- Slack approval cards for L4 escalations
- Shadow mode (observe-only) vs enforce mode

### Test: Plugin loads

```bash
# Gateway logs should show:
# [gateway] [plugins] ... discovered non-bundled plugins: guardspine, n8n-pipeline
# [gateway] auto-enabled plugins: Slack configured
```

### Known issue: Config corruption

The guardspine extension writes a `"guardspine"` key into `openclaw.json` at runtime.
This fails OpenClaw's Zod schema validation on restart, crashing the gateway.

**Workaround**: Redeploy to get a fresh baked config.
**Proper fix needed**: Store guardspine state in a separate file, not `openclaw.json`.

### If broken after merge

- Check upstream didn't change the plugin SDK import paths
- `src/gateway/server/ws-connection/connect-policy.ts` -- plugin loading
- Extension directory: `/app/.openclaw/extensions/guardspine/`
- Verify `plugin.js` exports match expected OpenClaw plugin interface

---

## 5. GuardSpine Governance Extension (Bundled)

### Files

- `extensions/guardspine-governance/` -- Full governance extension
  - `plugin.js` -- Plugin implementation (1252 lines)
  - `openclaw.plugin.json` -- Plugin manifest
  - `evidence-evaluator/` -- Python evidence evaluation scripts
  - `redteam/` -- Prompt injection test harness
  - `rlm-docsync/` -- Document sync with crypto proofs

### Test: Plugin manifest valid

```bash
node -e "const m = require('./extensions/guardspine-governance/openclaw.plugin.json'); console.log(m.id, m.version)"
```

### Test: Evidence evaluator

```bash
cd extensions/guardspine-governance/evidence-evaluator
python evaluate_evidence.py sample-evidence-pack.json
```

### If broken after merge

- Check `openclaw.plugin.json` schema matches upstream plugin manifest format
- If upstream changed plugin SDK, update `plugin.js` imports accordingly
- The `index.ts` has a known TS error (missing type declaration for plugin.js) -- non-blocking

---

## 6. n8n Workflow Infrastructure

### Files

- `guardspine/n8n-workflows/*.json` -- Workflow definitions
- `guardspine/scripts/deploy-n8n-workflows.sh` -- Deploy script
- `.github/workflows/backup-n8n.yml` -- Automated backup
- `guardspine/extensions/n8n-pipeline/plugin.js` -- OpenClaw plugin

### Test: n8n service running

```bash
curl -s -o /dev/null -w "%{http_code}" https://n8n-production-32ffd.up.railway.app/
# Expected: 200
```

### Test: Deploy workflows

```bash
cd guardspine/scripts
bash deploy-n8n-workflows.sh
```

### If broken after merge

- n8n is a separate Railway service, not affected by OpenClaw merge
- Workflow JSON files are standalone, no upstream dependencies
- Deploy script uses n8n REST API (PUT for updates, POST for creates)

---

## 7. CodeGuard CI/CD

### Files

- `.github/workflows/codeguard.yml` -- GitHub Actions workflow
- `.guardspine/config.yml` -- CodeGuard configuration

### Test: Workflow syntax valid

```bash
# Push any PR to trigger the codeguard workflow
# Or validate locally:
actionlint .github/workflows/codeguard.yml
```

### What it does

- Runs on every PR
- Calls GuardSpine kernel for AI code review
- Produces evidence bundles per review
- Blocks merge if L3+ risk detected (configurable)

### If broken after merge

- Check `.github/workflows/codeguard.yml` still references valid action versions
- Verify `guardspine_api_key` and `guardspine_api_url` secrets are set in GitHub repo
- Action: `codeguard-action` (separate repo `DNYoussef/codeguard-action`)

---

## 8. Slack Integration

### Files

- `docker/railway-config.json` -- `channels.slack` config
- `guardspine/extensions/guardspine/plugin.js` -- Slack approval cards

### Config

```json
{
  "channels": {
    "slack": {
      "botToken": "${SLACK_BOT_TOKEN}",
      "appToken": "${SLACK_APP_TOKEN}"
    }
  }
}
```

### Test: Slack connects

```bash
# Gateway logs should show:
# Slack configured, enabled automatically.
# NOT: Slack connection failed
```

### If broken after merge

- Reinstall Slack app at https://api.slack.com/apps/A0AF1015DK7
- Regenerate bot token (xoxb-) and app token (xapp-)
- Set in Railway env vars
- Slack bot needs `chat:write`, `channels:read`, `connections:write` scopes

---

## 9. GuardSpine Operational Artifacts

### Files

- `guardspine/ops/` -- Operational scripts (health check, decision journal, synthesis)
- `guardspine/data/` -- Migration SQL, schema definitions
- `guardspine/workspace/` -- Workspace configuration
- `guardspine/skills/` -- Content drafter, morning brief skills

### These are documentation/scripts, not runtime code.

No upstream dependencies. Safe across merges.

---

## 10. GuardSpine Business Documents

### Files

- `guardspine/reference/` -- Product docs, evidence packs
- `guardspine/assessment/` -- Security assessments
- `guardspine/investor/` -- Pitch deck, outreach materials
- `guardspine/legal/` -- Legal documents
- `guardspine/financial/` -- Financial models
- `guardspine/eric-prep/` -- Investor meeting prep

### These are static documents. No code dependencies. Safe across merges.

---

## 11. Dependabot Bumps

### Commits

- `08f1e4db3` -- androidx.test.uiautomator (Android)
- `87012fee7` -- actions/labeler 5.0.0 -> 6.0.1
- `c84c73d92` -- actions/download-artifact 4 -> 8
- `eaba44471` -- orchetect/menubarextraaccess (macOS)
- `4a5c9ba3d` -- apple/swift-testing (Swabble)
- `e8a2eccec` -- docker-images group

### Risk: These may conflict with upstream's own dependency bumps.

After merge, verify no duplicate or conflicting versions in:

- `.github/workflows/*.yml` (action versions)
- `apps/android/app/build.gradle.kts`
- `Swabble/Package.swift`

---

## Quick Smoke Test Checklist (Post-Merge)

```
[ ] Docker build: docker build -f Dockerfile.railway -t test .
[ ] Gateway starts: logs show "listening on ws://0.0.0.0:18789"
[ ] Plugins load: logs show guardspine and n8n-pipeline discovered
[ ] Slack connects: logs show "Slack configured, enabled automatically"
[ ] Control UI: https://openclaw-production-4349.up.railway.app/chat?session=main loads
[ ] Auth works: no "token_missing" or "pairing required" errors
[ ] AI inference: send message, get response from Claude Sonnet 4.5
[ ] n8n running: https://n8n-production-32ffd.up.railway.app/ returns 200
[ ] LiteLLM running: https://litellm-production-f6f2.up.railway.app/ returns 200
[ ] CodeGuard: push a test PR, verify codeguard workflow triggers
```

---

## Upstream Merge Process

When merging future upstream releases:

```bash
cd D:/Projects/openclaw-upstream
git fetch origin --tags
git checkout -b merge/upstream-vX.Y.Z dnyoussef/main
git merge vX.Y.Z

# Resolve conflicts (usually in Dockerfiles, vitest configs)
# Our files are isolated in guardspine/, extensions/, docker/
# Take upstream for core OpenClaw code

git push dnyoussef merge/upstream-vX.Y.Z
# Create PR, run smoke test checklist, merge to main
```

### High-conflict areas to watch

- `Dockerfile` / `Dockerfile.sandbox*` -- upstream rewrites these often
- `vitest.config.ts` -- upstream adds test patterns
- `package.json` / `pnpm-lock.yaml` -- dependency changes
- `src/config/zod-schema.ts` -- if we ever add guardspine config keys
- `src/gateway/server/ws-connection/` -- auth flow changes

### Low-conflict areas (all ours, no upstream equivalent)

- `guardspine/` -- entire directory
- `extensions/guardspine-governance/` -- our extension
- `docker/railway-*.json` -- our Railway config
- `Dockerfile.railway` -- our custom Dockerfile
- `.github/workflows/codeguard.yml` -- our CI
