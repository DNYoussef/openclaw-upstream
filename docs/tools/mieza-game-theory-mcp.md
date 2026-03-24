---
summary: "Use Mieza's game-theory API and MCP server from OpenClaw for equilibrium-grounded strategic reasoning"
read_when:
  - Evaluating external MCP servers for OpenClaw
  - Wanting game-theoretic reasoning in an agent workflow
  - Deciding when to model a problem as a game instead of using generic LLM judgment
title: "Mieza Game Theory MCP"
---

# Mieza Game Theory MCP

## One-sentence recommendation

Use Mieza as an **external strategy engine** for well-defined competitive or repeated interactions, and connect it to OpenClaw through the MCP bridge model OpenClaw already prefers.

That means:

- do **not** treat Mieza as a generic planning LLM
- do **not** pull it into OpenClaw core as a first-class runtime
- do use it when the problem can be stated as a game with explicit players, actions, payoffs, and repeated play history

OpenClaw's MCP stance is already clear: use `mcporter` as the bridge layer instead of building first-class MCP runtime into core. See [OpenClaw Vision](../../VISION.md).

## What Mieza is

Mieza is a game-theory / strategic-reasoning platform built around what it calls **Optimal Strategic Reasoning (OSR)**.

The documentation emphasizes:

- robustness against adversaries in well-defined games
- provability and verification
- interpretability through explicit game structure and utilities

Source:

- [Getting Started](https://mieza.ai/docs/getting-started)

The strongest claims are for settings with:

- clear rules
- known payoffs
- finite structure
- repeated strategic interaction where history matters

That is the correct lens for using it in OpenClaw.

## What Mieza exposes

Mieza exposes three useful surfaces:

1. **Web UI**
2. **HTTP API**
3. **MCP server**

Important negative fact:

- the public docs do **not** describe a separate local Mieza CLI binary

So if you are bootstrapping this from OpenClaw, the practical integration paths are:

- HTTP API
- MCP over Streamable HTTP

Not "install a local `mieza` executable."

Sources:

- [Getting Started](https://mieza.ai/docs/getting-started)
- [API Overview](https://mieza.ai/docs/api-overview)
- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [GTO MCP page](https://mieza.ai/gto/mcp)

## Why it matters for OpenClaw

Mieza gives OpenClaw something OpenClaw does not natively specialize in:

- equilibrium-grounded reasoning for structured strategic conflicts

That is useful for questions like:

- "If two competitors can both cut price, what equilibrium should we expect?"
- "If a vendor and a buyer interact every month, what repeated-game policy should guide our next move?"
- "If we introduce a program, incentive, or channel response, what is the likely stable strategic outcome?"

This is **not** the right tool for:

- vague product brainstorming
- open-ended UX judgment
- generic agent planning without explicit players and payoffs

## When the model should reach for Mieza

The model should use Mieza when all or most of these are true:

- there are identifiable players
- each player has explicit actions
- payoffs or utility rankings can be stated
- the problem is strategic, not purely descriptive
- the user wants equilibrium or policy guidance, not free-form advice

Good examples:

- pricing competition
- vendor negotiation
- marketplace incentives
- retention programs
- escalation / concession strategy in repeated interactions

Bad examples:

- "write me a roadmap"
- "which feature is cooler"
- "summarize this repo"

## Bootstrap path

### 1. Create a Mieza token

Mieza uses personal access tokens.

Documented flow:

1. go to **Settings → Access Tokens**
2. click **Create Token**
3. choose a name
4. choose permissions:
   - `read`
   - `write`
   - `admin`
5. choose expiration
6. copy the token immediately

Source:

- [API Access Tokens](https://mieza.ai/docs/api-tokens)

### 2. Know the base URLs

The docs state:

- API base: `https://mieza.ai/api/`
- GTO proxied endpoints: `https://mieza.ai/api/public/v1/gto/`
- MCP endpoint: `https://mieza.ai/mcp`

Sources:

- [API Overview](https://mieza.ai/docs/api-overview)
- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [GTO MCP page](https://mieza.ai/gto/mcp)

### 3. Decide whether you need ephemeral solving or persistent games

Use **ephemeral solving** when:

- you only need a one-shot equilibrium
- you do not need stored history
- you do not need assigned repeated-game policies

Use **persistent games** when:

- you want to save a game
- you want to record rounds over time
- you want to assign and query policies

Source:

- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

## MCP integration

Mieza documents an MCP server using **Streamable HTTP** transport.

Their documented config shape is:

```json
{
  "mcpServers": {
    "mieza": {
      "url": "https://mieza.ai/mcp",
      "headers": {
        "Authorization": "Bearer tt_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [GTO MCP page](https://mieza.ai/gto/mcp)

The docs explicitly call out config placement for:

- Cursor: `.cursor/mcp.json`
- Claude Desktop: `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS
- other Streamable-HTTP-compatible clients

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)

## OpenClaw-specific interpretation

OpenClaw does not want first-class MCP runtime in core when `mcporter` already solves the bridge problem.

So for OpenClaw, the right reading is:

- Mieza is an external MCP server
- OpenClaw should consume it through the existing MCP bridge model
- tool exposure should stay narrow and intentional

That keeps strategic-game tooling decoupled from the main assistant runtime.

## Mieza MCP tools

### Open tools

These do not require auth according to the docs and the public MCP page:

- `solve_game`
- `policy_catalog`

Descriptions from the public MCP page:

- `solve_game`: compute Nash equilibrium strategies for a normal-form game
- `policy_catalog`: list available repeated-game policies and metadata

Sources:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [GTO MCP page](https://mieza.ai/gto/mcp)

### Authenticated tools

The documented authenticated MCP tools are:

- `create_game`
- `get_game`
- `record_play`
- `assign_policy`
- `policy_next_action`

These are the tools that matter for persistent, history-aware workflows.

Sources:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [GTO MCP page](https://mieza.ai/gto/mcp)

## Tool semantics the model should understand

### `solve_game`

Use this for:

- one-shot equilibrium analysis of a 2-player normal-form game
- checking whether a strategic setup is a prisoner's dilemma, coordination game, etc.

Expected structure from the public MCP page:

- players
- strategies/actions per player
- payoff matrix

Source:

- [GTO MCP page](https://mieza.ai/gto/mcp)

### `policy_catalog`

Use this to:

- discover available repeated-game policies before assigning one
- inspect what policy families exist for long-running interactions

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

### `create_game`

Use this when:

- the interaction will happen repeatedly
- you want a persistent game ID
- you want later policy assignment and play recording

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

### `record_play`

Use this after each observed round.

The tutorial explicitly says the platform computes and stores realized payoffs and future policy queries incorporate the new history.

Source:

- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

### `assign_policy`

Use this to bind a player to a repeated-game policy such as tit-for-tat.

Source:

- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)
- [GTO MCP page](https://mieza.ai/gto/mcp)

### `policy_next_action`

Use this before the next round when you want a policy recommendation given the full play history.

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)
- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

## HTTP API bootstrap

If MCP is unavailable or you want direct integration, the HTTP API is documented and straightforward.

### Auth header

```bash
Authorization: Bearer tt_YOUR_TOKEN_HERE
```

Source:

- [API Overview](https://mieza.ai/docs/api-overview)

### Public endpoints called out in the docs

- `POST /api/public/v1/gto/api/gt/nf-solve`
- `GET /api/public/v1/gto/api/gt/policies/catalog`

These are public according to the API overview.

Source:

- [API Overview](https://mieza.ai/docs/api-overview)

### Persistent game examples from the tutorial

Create a game:

```bash
curl -X POST https://mieza.ai/api/public/v1/gto/api/gt/games/nf \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "game": {
      "players": ["Alice", "Bob"],
      "actions": {"Alice": ["Cooperate", "Defect"], "Bob": ["Cooperate", "Defect"]},
      "payoffs": {
        "Cooperate,Cooperate": [-1, -1],
        "Cooperate,Defect": [-3, 0],
        "Defect,Cooperate": [0, -3],
        "Defect,Defect": [-2, -2]
      }
    },
    "name": "Prisoner Dilemma",
    "description": "Classic cooperation vs. defection"
  }'
```

Assign a policy:

```bash
curl -X POST https://mieza.ai/api/public/v1/gto/api/gt/games/nf/GAME_ID/policies \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "player": "Alice",
    "policy_key": "tit-for-tat",
    "config": {"default-action": "Cooperate"}
  }'
```

Query next action:

```bash
curl -X POST https://mieza.ai/api/public/v1/gto/api/gt/games/nf/GAME_ID/policies/ASSIGNMENT_ID/next \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Record a round:

```bash
curl -X POST https://mieza.ai/api/public/v1/gto/api/gt/games/nf/GAME_ID/play \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "actions": {"Alice": "Cooperate", "Bob": "Cooperate"},
    "title": "Round 1"
  }'
```

Source:

- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

## Response and error conventions

The API overview documents:

- JSON request and response bodies
- pagination envelopes for list endpoints
- error shape with `error.cause` and `error.message`
- standard HTTP statuses like `400`, `401`, `403`, `404`, `409`, `422`, `429`, `500`

Source:

- [API Overview](https://mieza.ai/docs/api-overview)

It also documents:

- Swagger UI: `https://mieza.ai/swagger-ui`
- OpenAPI spec: `https://mieza.ai/openapi.yaml`

Source:

- [API Overview](https://mieza.ai/docs/api-overview)

## What the model should tell the user before using Mieza

The model should ask or infer:

1. Who are the players?
2. What actions does each player have?
3. What are the payoffs or utility rankings?
4. Is this one-shot or repeated?
5. Do we need equilibrium analysis or a policy recommendation over time?

If the user cannot answer those questions, the model should not force Mieza onto the problem.

## Good OpenClaw prompt patterns

### One-shot equilibrium

> Model this as a two-player normal-form game. Identify players, actions, and payoffs explicitly. Use Mieza only after the payoff table is concrete.

### Repeated interaction

> Treat this as a repeated game. Create a persistent game, inspect available policies, assign a policy only after confirming the default action and intended incentive structure, then query next action using recorded history.

### Safety check

> If payoffs are vague or invented, say so. Do not present Mieza output as authoritative unless the game definition is explicit and defensible.

## Example use cases for OpenClaw

Strong fits:

- recurring vendor negotiation
- pricing-response simulation
- loyalty program competition
- concession/escalation policy in repeated enterprise deals
- marketplace incentive design with small explicit action sets

Weak fits:

- broad org strategy
- ambiguous hiring decisions
- moral advice
- UX taste judgments

## Practical caveats

### 1. Normal-form scope is explicit

The public tooling and tutorial center on **2-player normal-form games** plus repeated-game policies layered on top.

Do not assume arbitrary strategic worlds are supported just because they feel game-theoretic.

Sources:

- [GTO MCP page](https://mieza.ai/gto/mcp)
- [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)

### 2. Guarantees depend on problem quality

Mieza's strongest claims depend on well-defined games, not messy prose disguised as math.

Source:

- [Getting Started](https://mieza.ai/docs/getting-started)

### 3. MCP auth is required for persistent workflows

The docs distinguish clearly between public tools and authenticated tools.

Source:

- [MCP Integration](https://mieza.ai/docs/mcp-integration)

## Recommended OpenClaw rollout

### Phase 1: Narrow tool introduction

- expose Mieza only to strategy-oriented agents
- keep invocation manual or tightly instructed
- use one-shot `solve_game` first

### Phase 2: Persistent repeated-game workflows

- add authenticated use for persistent games
- track `game_id` and policy assignment metadata externally
- record play only when real observations exist

### Phase 3: Native policy workflows

- build OpenClaw-side wrappers or skills for:
  - define game
  - create game
  - assign policy
  - record round
  - query next move

Only do this after the raw MCP/API workflow proves useful.

## Bottom line

Mieza is not a generic intelligence upgrade.

It is a **specialized strategic-reasoning tool** for problems that can actually be modeled as games.

For OpenClaw, the right use is:

- external MCP/API strategy engine
- narrow invocation discipline
- no core runtime merge
- explicit game formulation before use

That is how you get the value of equilibrium-grounded reasoning without turning every fuzzy question into fake math.

## Direct sources

- OpenClaw MCP position:
  - [VISION.md](../../VISION.md)
- Mieza docs:
  - [Getting Started](https://mieza.ai/docs/getting-started)
  - [API Overview](https://mieza.ai/docs/api-overview)
  - [API Access Tokens](https://mieza.ai/docs/api-tokens)
  - [MCP Integration](https://mieza.ai/docs/mcp-integration)
  - [Solving Your First Game](https://mieza.ai/docs/solving-your-first-game)
  - [Building Agents](https://mieza.ai/docs/building-agents)
- Mieza product pages:
  - [GTO MCP page](https://mieza.ai/gto/mcp)
  - [GTO Solve](https://mieza.ai/gto/solve)
