---
summary: "PlateSpinner as a sidecar Kanban UI for OpenClaw repo-agent workflows"
read_when:
  - Evaluating external orchestration UIs for OpenClaw
  - Wanting a visual control surface outside Slack and n8n
  - Deciding whether to embed or reimplement PlateSpinner concepts
title: "PlateSpinner Sidecar UI"
---

# PlateSpinner Sidecar UI

## One-sentence recommendation

Use PlateSpinner as a **sidecar UI next to OpenClaw first**, not as a day-one core subsystem.

That is the right starting point because PlateSpinner is a **full separate app** with its own server, WebSocket layer, state store, route surface, plugin runtime, and coding-agent execution model. It is useful, but it is not a drop-in widget.

This also matches OpenClaw's own architectural guardrail against pulling **heavy orchestration layers that duplicate existing agent and tool infrastructure** into core. See [OpenClaw Vision](../../VISION.md).

## What PlateSpinner is

PlateSpinner is a Kanban board for orchestrating **local coding-agent workflows**. You point it at a local repo, describe a task, and it runs a three-stage flow:

1. **Propose**: a read-only AI session analyzes the repo and generates candidate tasks.
2. **Plan**: a second read-only session produces a concrete implementation plan.
3. **Execute**: a write-capable session edits code, runs tests, and commits changes.

Source:

- [PlateSpinner README](https://github.com/moridinamael/platespinner/blob/main/README.md)

It also has an **autoclicker** mode that continuously judges the current state and decides whether to propose, plan, or execute next.

Source:

- [PlateSpinner README](https://github.com/moridinamael/platespinner/blob/main/README.md)

## Why it is relevant to OpenClaw

For OpenClaw, the useful part is not "another agent runtime."

The useful part is the **control surface**:

- a visible board of repo work
- queued work instead of pure chat streams
- real-time execution telemetry
- diff review
- replay of prior agent runs
- per-task cost tracking

That gives you a UI surface outside Slack and n8n where you can **see work moving** and **interact with repo automation visually**.

Good fit for OpenClaw:

- coding/backlog workflows
- repo maintenance
- planned refactors
- test-fix loops
- branch-per-task review

Bad fit for OpenClaw:

- chat-first messaging workflows
- channel-native support operations
- general-purpose multi-channel assistant interaction

PlateSpinner is repo-centric. OpenClaw is broader than that.

## What PlateSpinner is not

PlateSpinner is **not**:

- an OpenClaw plugin today
- a native OpenClaw UI module
- a messaging surface
- a generic session inspector for all OpenClaw channels
- a drop-in React component you can import into OpenClaw UI

Why that matters:

- it ships its own **Express backend** and **WebSocket server**
- it persists state in **JSON on disk**
- it has its own REST routes
- it shells out directly to `claude`, `codex`, and `gemini`

Sources:

- [server/index.js](https://github.com/moridinamael/platespinner/blob/main/server/index.js)
- [server/ws.js](https://github.com/moridinamael/platespinner/blob/main/server/ws.js)
- [server/state.js](https://github.com/moridinamael/platespinner/blob/main/server/state.js)
- [server/agents/cli.js](https://github.com/moridinamael/platespinner/blob/main/server/agents/cli.js)

## Source-backed architecture snapshot

### Runtime

- Node.js `>=18`
- frontend: Vite + React
- backend: Express + WebSocket

Sources:

- [package.json](https://github.com/moridinamael/platespinner/blob/main/package.json)
- [vite.config.js](https://github.com/moridinamael/platespinner/blob/main/vite.config.js)
- [server/index.js](https://github.com/moridinamael/platespinner/blob/main/server/index.js)

### Default ports

- frontend dev server: `5173`
- backend/server: `3001`

Sources:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [vite.config.js](https://github.com/moridinamael/platespinner/blob/main/vite.config.js)
- [.env.example](https://github.com/moridinamael/platespinner/blob/main/.env.example)

### State model

PlateSpinner keeps:

- projects
- tasks
- running processes
- project locks
- execution queues
- notification settings
- autoclicker config and audit log

Source:

- [server/state.js](https://github.com/moridinamael/platespinner/blob/main/server/state.js)

### Task states

The source shows task lifecycle states including:

- `proposed`
- `planning`
- `planned`
- `queued`
- `executing`
- `done` / post-execution flows via validators and task updates

Sources:

- [server/routes/tasks.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/tasks.js)
- [server/state.js](https://github.com/moridinamael/platespinner/blob/main/server/state.js)

### Local coding-agent execution

PlateSpinner builds commands for:

- `claude`
- `codex`
- `gemini`

Generation is read-only. Execution includes write/edit/bash permissions.

Source:

- [server/agents/cli.js](https://github.com/moridinamael/platespinner/blob/main/server/agents/cli.js)

## The right OpenClaw framing

The right question is not:

> "How do we absorb PlateSpinner into OpenClaw core?"

The right question is:

> "How do we use PlateSpinner as a repo-work sidecar and expose it cleanly from OpenClaw UI?"

That distinction prevents a bad architecture decision.

## Recommended integration modes

### Mode A: External sidecar with OpenClaw launch link

This is the recommended first move.

What it means:

- run PlateSpinner as its own service
- add an OpenClaw UI entry like `Kanban`, `Board`, or `Repo Ops`
- clicking it opens PlateSpinner in a new tab or embedded webview

Why this is the best first move:

- lowest coupling
- no forced merge of state models
- no need to rewrite PlateSpinner internals
- lets you validate whether the workflow is actually useful

Use this mode first.

### Mode B: Embedded sidecar inside OpenClaw UI shell

This is feasible after Mode A works.

What it means:

- OpenClaw UI hosts PlateSpinner under a proxied route or embedded frame
- OpenClaw provides navigation and auth context around it

What to watch:

- auth boundary
- frame/csp behavior
- localhost/service discovery
- state ownership

Important source detail:

PlateSpinner already includes an `/api/proxy` route for iframe previews and strips frame-blocking headers while rejecting private/internal IP targets. That is useful context, but it is **not** the same thing as a production-grade OpenClaw embedding strategy.

Source:

- [server/index.js](https://github.com/moridinamael/platespinner/blob/main/server/index.js)

### Mode C: Native OpenClaw reimplementation of the useful ideas

This is the long-term option, not the first step.

What to borrow:

- kanban task lifecycle
- queue view
- replay view
- diff review
- cost panel
- project/test/deploy control panel

What not to borrow blindly:

- its full local process orchestration model
- its JSON-file persistence
- its direct coupling to local coding CLIs

## OpenClaw-specific recommendation

For upstream OpenClaw, the best sequence is:

1. **Run PlateSpinner as a sidecar** against local repos
2. **Expose it from OpenClaw UI** as a companion screen
3. **Bridge metadata**, not full control, at first
4. **Promote only proven concepts** into native OpenClaw UI later

This preserves OpenClaw's architecture while giving you the UI you want now.

## Bootstrap checklist

### 1. Clone and run PlateSpinner

```bash
git clone https://github.com/moridinamael/platespinner.git
cd platespinner
npm install
npm run dev
```

Or production-style:

```bash
npm start
```

Sources:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [package.json](https://github.com/moridinamael/platespinner/blob/main/package.json)

### 2. Ensure at least one coding CLI is installed

PlateSpinner expects one or more of:

- Claude Code
- Codex CLI
- Gemini CLI

Source:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)

### 3. Add the target repo as a project

Open PlateSpinner and point it at a **local codebase directory**.

Source:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)

### 4. Use safe defaults first

For OpenClaw evaluation, start with:

- `branch-per-task`
- autoclicker **off**
- auto-push **off**
- auto-merge **off**
- moderate budget limit
- test command explicitly configured

Why:

- you want visibility first
- not blind autonomy first

Sources:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [server/routes/projects.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/projects.js)

### 5. Use Propose and Plan before Execute

Do not enable full autonomous execution before you have validated:

- task quality
- plan quality
- branch strategy
- test detection
- replay/diff review flow

This is the difference between evaluation and self-harm.

## The API and event surface that matter

If OpenClaw wants to interact with PlateSpinner programmatically, the useful surface is:

### REST routes

- `/api/projects`
- `/api/tasks`
- `/api/generate`
- `/api/tasks/:id/plan`
- `/api/tasks/:id/execute`
- `/api/tasks/queue`
- `/api/projects/:id/test`
- `/api/projects/:id/check-railway`

Sources:

- [server/index.js](https://github.com/moridinamael/platespinner/blob/main/server/index.js)
- [server/routes/projects.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/projects.js)
- [server/routes/tasks.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/tasks.js)

### WebSocket events

The source shows broadcast-driven updates for things like:

- project creation / updates
- execution queued / dequeued
- queue updates
- test started / completed
- railway status

Sources:

- [server/ws.js](https://github.com/moridinamael/platespinner/blob/main/server/ws.js)
- [server/routes/projects.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/projects.js)
- [server/routes/tasks.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/tasks.js)

This means OpenClaw can integrate at three levels:

- dumb link
- embedded UI
- partial API/WS bridge

## Safety and risk notes

These are the reasons not to collapse PlateSpinner into OpenClaw core blindly.

### 1. Full-access execution is real

Execution mode gives coding agents write access and shell access.

Source:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [server/agents/cli.js](https://github.com/moridinamael/platespinner/blob/main/server/agents/cli.js)

### 2. Autonomous loop is real

Autoclicker is not "assistive UI." It is an autonomous propose/plan/execute loop.

Source:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [server/state.js](https://github.com/moridinamael/platespinner/blob/main/server/state.js)

### 3. Direct git/deploy actions exist

The project route surface includes push, merge, revert, create-PR, and Railway health-check flows.

Source:

- [server/routes/projects.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/projects.js)

### 4. Plugins extend execution behavior

PlateSpinner plugins can register:

- pre/post execution hooks
- post-planning hooks
- task validators
- custom tools
- custom parsers

Source:

- [plugins/README.md](https://github.com/moridinamael/platespinner/blob/main/plugins/README.md)

### 5. Persistence is simple

State is JSON-file based, which is fine for a local sidecar but not automatically the persistence model OpenClaw should standardize on.

Source:

- [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- [server/state.js](https://github.com/moridinamael/platespinner/blob/main/server/state.js)

## Best near-term use inside the OpenClaw ecosystem

Use PlateSpinner for:

- OpenClaw repo maintenance
- extension/plugin development queues
- bug-fix and refactor pipelines
- visual supervision of coding-agent runs
- diff/replay review outside chat

Do not use it as:

- the new core OpenClaw runtime
- the main UI for all OpenClaw channels
- the canonical source of truth for OpenClaw conversations

## Recommended phased adoption

### Phase 0: Evaluation

- run PlateSpinner locally
- attach it to `openclaw-upstream`
- use propose/plan only
- validate diff/replay usefulness

### Phase 1: Sidecar UI

- add an OpenClaw UI nav entry that opens PlateSpinner
- keep state ownership inside PlateSpinner
- do not sync tasks back into OpenClaw yet

### Phase 2: Metadata bridge

- mirror selected project/task summaries into OpenClaw
- surface queue state and run status in OpenClaw UI
- keep execution in PlateSpinner

### Phase 3: Native product decisions

- only after real usage, decide which ideas belong in OpenClaw proper:
  - board
  - queue panel
  - replay panel
  - cost and test widgets

## Bottom line

PlateSpinner is a strong candidate for the **UI layer around repo-centric coding work**.

For OpenClaw, the right move is:

- **adopt it as a sidecar first**
- **link or embed it second**
- **copy concepts into core only after they prove value**

That gives you a visual Kanban control surface outside Slack and n8n without forcing OpenClaw into an unnecessary architectural merge.

## Direct sources

- PlateSpinner repo:
  - [github.com/moridinamael/platespinner](https://github.com/moridinamael/platespinner)
- Product overview and quick start:
  - [README.md](https://github.com/moridinamael/platespinner/blob/main/README.md)
- Runtime metadata:
  - [package.json](https://github.com/moridinamael/platespinner/blob/main/package.json)
  - [.env.example](https://github.com/moridinamael/platespinner/blob/main/.env.example)
- Backend entry and WebSocket:
  - [server/index.js](https://github.com/moridinamael/platespinner/blob/main/server/index.js)
  - [server/ws.js](https://github.com/moridinamael/platespinner/blob/main/server/ws.js)
- Agent command execution:
  - [server/agents/cli.js](https://github.com/moridinamael/platespinner/blob/main/server/agents/cli.js)
- Routes and operational surface:
  - [server/routes/projects.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/projects.js)
  - [server/routes/tasks.js](https://github.com/moridinamael/platespinner/blob/main/server/routes/tasks.js)
- Plugin model:
  - [plugins/README.md](https://github.com/moridinamael/platespinner/blob/main/plugins/README.md)
