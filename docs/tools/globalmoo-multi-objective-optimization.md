---
summary: "Use globalMOO as an external multi-objective optimization engine for OpenClaw agent workflows"
read_when:
  - Evaluating external optimization engines for OpenClaw
  - Wanting inverse or constraint-based optimization in an agent workflow
  - Deciding when to use globalMOO instead of Mieza or generic LLM planning
title: "globalMOO Multi-Objective Optimization"
---

# globalMOO Multi-Objective Optimization

## One-sentence recommendation

Use globalMOO as an **external optimization engine** when OpenClaw has a real function, simulator, or evaluable system with explicit inputs and measurable outputs.

That means:

- do **not** treat globalMOO as a chat-native reasoning tool
- do **not** treat it as an MCP server
- do **not** wire it into OpenClaw core before proving a narrow wrapper
- do use it for inverse problems, multi-objective targeting, and constrained search over mixed variable types

## What globalMOO is

globalMOO is a multi-objective optimization platform focused on **inverse problems**: you define inputs, outputs, and objectives, then globalMOO suggests input values that should drive the outputs toward the desired targets.

The official example suite describes it as useful for:

- finding input parameters that achieve desired outputs
- working with continuous, integer, logical, and categorical variables
- handling multiple objective types and constrained optimization

Sources:

- [globalMOO homepage](https://globalmoo.com/)
- [globalMOO SDK example suite](https://github.com/globalMOO/gmoo-sdk-suite)
- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)

## What globalMOO is not

globalMOO is **not**:

- an MCP server, at least not in the official public docs I found
- a general-purpose strategic game engine
- a Kanban or orchestration UI
- a drop-in replacement for OpenClaw planning or tool routing

I found official documentation for:

- the web product
- the HTTP API
- language SDKs
- example suites and an interactive notebook

I did **not** find official public docs for:

- a separate GlobalMOO MCP endpoint
- a standalone local CLI comparable to other agent tools

That matters because the right OpenClaw integration surface is **API/SDK**, not MCP.

Sources:

- [API Documents](https://globalmoo.com/api-documents/)
- [globalMOO Documentation](https://globalmoo.gitbook.io/globalmoo-documentation)
- [JavaScript SDK](https://github.com/globalMOO/gmoo-sdk-javascript)
- [Python SDK](https://github.com/globalMOO/gmoo-sdk-python)

## Why it matters for OpenClaw

OpenClaw does not natively specialize in numerical inverse optimization.

globalMOO gives OpenClaw a disciplined way to solve problems like:

- "What inputs satisfy these output targets?"
- "How do we maximize one metric while constraining others?"
- "What settings hit a feasible operating envelope?"
- "Which combination of continuous, integer, logical, and categorical controls best meets a multi-objective target?"

This is strongest when OpenClaw already has access to:

- a function
- a simulator
- a digital twin
- a service that can evaluate candidate inputs and return outputs

Without that evaluator, globalMOO has nothing real to optimize.

## The core workflow OpenClaw should understand

The official docs and SDKs converge on the same loop:

1. create a model
2. create a project with input definitions
3. evaluate the initial input cases globalMOO provides
4. load those output cases
5. load objectives
6. iterate:
   - request a suggested inverse step
   - run the external function or simulator on the suggested inputs
   - load the resulting outputs back into globalMOO
7. stop when the result reports satisfaction or another stop condition

Primary sources:

- [Create Model](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/models/create)
- [Create Project](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/projects/create)
- [Load Output Cases](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/outputs/load-cases)
- [Load Objectives](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/objectives/load)
- [Suggest Inverse Step](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/inverse/suggest)
- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)
- [JavaScript SDK README](https://github.com/globalMOO/gmoo-sdk-javascript/blob/main/README.md)
- [Python SDK README](https://github.com/globalMOO/gmoo-sdk-python/blob/main/README.md)

## Official endpoint and type surface

### 1. Create model

- Endpoint: `POST /models`
- Purpose: create a named model container

Source:

- [Create Model](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/models/create)

### 2. Create project

- Endpoint: `POST /models/{model_id}/projects`
- Purpose: define input count, bounds, types, and categories

The official project docs list these input types:

- `CONTINUOUS`
- `INTEGER`
- `CATEGORICAL`
- `LOGICAL`

Source:

- [Create Project](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/projects/create)

### 3. Load output cases

- Endpoint: `POST /models/{model_id}/projects/{project_id}/output-cases`
- Purpose: send back outputs for the generated learning cases

Source:

- [Load Output Cases](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/outputs/load-cases)

### 4. Load objectives

- Endpoint: `POST /models/{model_id}/projects/{project_id}/trials/{trial_id}/objectives`
- Purpose: define targets and objective types

Documented objective types include:

- `exact`
- `percent`
- `value`
- `lessthan`
- `lessthan_equal`
- `greaterthan`
- `greaterthan_equal`
- `minimize`
- `maximize`

Source:

- [Load Objectives](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/objectives/load)

### 5. Suggest inverse step

- Endpoint: `POST /models/{model_id}/projects/{project_id}/trials/{trial_id}/objectives/{objective_id}/inverses`
- Purpose: get the next candidate inputs to evaluate

Source:

- [Suggest Inverse Step](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/inverse/suggest)

### 6. Load the evaluated result

The SDK READMEs document `LoadInversedOutput` / `loadInversedOutput` as the final step in the optimization loop after evaluating the suggested input.

Source:

- [JavaScript SDK README](https://github.com/globalMOO/gmoo-sdk-javascript/blob/main/README.md)
- [Python SDK README](https://github.com/globalMOO/gmoo-sdk-python/blob/main/README.md)
- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)

## Bootstrap path for OpenClaw

### 1. Get credentials

The quickstart says you need a globalMOO API key and points users to:

- `https://api.globalmoo.ai/`

Source:

- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)

### 2. Install an SDK

Recommended official SDKs:

- Python: `pip install globalmoo-sdk`
- JavaScript: `npm install @globalmoo/globalmoo-sdk`

Sources:

- [Python SDK README](https://github.com/globalMOO/gmoo-sdk-python/blob/main/README.md)
- [JavaScript SDK README](https://github.com/globalMOO/gmoo-sdk-javascript/blob/main/README.md)

### 3. Set environment variables carefully

This is the first real integration trap.

The official sources are inconsistent about the base URI:

- the quickstart examples use `https://api.globalmoo.ai/api`
- the SDK READMEs use `https://app.globalmoo.com/api/`

The environment variable names are consistent:

- `GMOO_API_KEY`
- `GMOO_API_URI`

OpenClaw should therefore:

- make the base URI configurable
- never hardcode one host without verifying it against the account being used
- prefer a deployment-time env var over a source-level constant

Sources:

- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)
- [Python SDK README](https://github.com/globalMOO/gmoo-sdk-python/blob/main/README.md)
- [JavaScript SDK README](https://github.com/globalMOO/gmoo-sdk-javascript/blob/main/README.md)

### 4. Start with the example suite

The example suite is the cleanest way to learn how globalMOO behaves before putting OpenClaw in front of it.

It includes examples for:

- linear
- nonlinear
- integer
- logical
- categorical
- exact objective
- multiple objective types
- constrained maximization
- webhook-driven flows

Source:

- [globalMOO SDK example suite](https://github.com/globalMOO/gmoo-sdk-suite)

## The minimum OpenClaw mental model

OpenClaw should treat globalMOO as a **stateful optimization session**, not a one-shot function call.

At minimum, the wrapper needs to keep:

- `modelId`
- `projectId`
- `trialId`
- `objectiveId`
- current iteration status
- last suggested input
- last evaluated output

That is the real contract.

If OpenClaw loses that state, it cannot continue the optimization loop cleanly.

## OpenClaw-side wrapper shape

The right first wrapper is narrow:

1. accept a problem spec:
   - input schema
   - objective schema
   - evaluator hook
2. create model and project
3. run initial training cases
4. create trial and objectives
5. loop suggest/evaluate/load
6. return:
   - best found inputs
   - final outputs
   - satisfaction status
   - stop reason

The evaluator hook is the critical boundary. It can point to:

- a local function
- a Python service
- a digital twin
- a remote simulation endpoint

That keeps OpenClaw clean: OpenClaw orchestrates, globalMOO optimizes, the evaluator computes outputs.

## When the model should reach for globalMOO

Use globalMOO when all or most of these are true:

- the problem has explicit numeric or categorical inputs
- the outputs are measurable
- there is a real evaluator available
- the user wants constrained optimization, not prose advice
- multiple objectives or tradeoffs matter

Strong fits:

- process tuning
- digital twin optimization
- system calibration with real outputs
- operations and control parameter search
- engineering or scientific inverse problems

## When not to use globalMOO

Do **not** use globalMOO for:

- vague planning
- strategy games with explicit competitors and payoff matrices
- chat-first product ideation
- repo/task orchestration UI

Use other tools instead:

- Mieza for strategic equilibrium and repeated-game reasoning
- PlateSpinner for Kanban-style repo orchestration UI

Sources:

- [Mieza Game Theory MCP](/tools/mieza-game-theory-mcp)
- [PlateSpinner Sidecar UI](/tools/platespinner-sidecar-ui)

## Source inconsistencies OpenClaw must not ignore

This is the most important integration warning.

### 1. Base URI mismatch

Official sources currently disagree between:

- `https://api.globalmoo.ai/api`
- `https://app.globalmoo.com/api/`

Do not hardcode either one blindly.

### 2. SDK bootstrap mismatch

The current quickstart shows older-looking import/package examples in some language tabs, while the official SDK repos show:

- Python package: `globalmoo-sdk`
- Python import: `from globalmoo.client import Client`
- JavaScript package: `@globalmoo/globalmoo-sdk`
- JavaScript import: `import { Client } from '@globalmoo/globalmoo-sdk'`

For actual installation and imports, prefer the SDK repositories.

For endpoint semantics, prefer the GitBook endpoint docs.

Sources:

- [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)
- [Python SDK README](https://github.com/globalMOO/gmoo-sdk-python/blob/main/README.md)
- [JavaScript SDK README](https://github.com/globalMOO/gmoo-sdk-javascript/blob/main/README.md)

### 3. No official MCP or CLI docs found

That means any OpenClaw integration should assume:

- API/SDK first
- custom wrapper second
- MCP only if GlobalMOO later publishes an official interface

## Recommended rollout for OpenClaw

### Phase 1: prove the evaluator boundary

- wrap one known function or simulator
- run the official example-style loop end to end
- persist optimization state outside the model prompt

### Phase 2: add a narrow OpenClaw tool

- `globalmoo_create_session`
- `globalmoo_step`
- `globalmoo_status`
- `globalmoo_finalize`

Do not expose raw endpoint complexity to every agent by default.

### Phase 3: add domain adapters

- digital twin adapter
- calibration adapter
- constrained operations adapter

Only add these after the generic loop works.

## Bottom line

globalMOO is a real optimization engine, not a generic reasoning upgrade.

For OpenClaw, the right use is:

- external API/SDK engine
- explicit evaluator boundary
- stateful optimization loop
- narrow wrapper before broader adoption

That is how you get real multi-objective optimization without pretending a chat model can replace a solver.

## Direct sources

- Product and API landing:
  - [globalMOO homepage](https://globalmoo.com/)
  - [API Documents](https://globalmoo.com/api-documents/)
- Official quickstart:
  - [Your First Optimization with globalMOO](https://globalmoo.gitbook.io/globalmoo-documentation/quickstart/your_first_optimization)
- Official endpoint docs:
  - [Create Model](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/models/create)
  - [Create Project](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/projects/create)
  - [Load Output Cases](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/outputs/load-cases)
  - [Load Objectives](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/objectives/load)
  - [Suggest Inverse Step](https://globalmoo.gitbook.io/globalmoo-documentation/endpoints/inverse/suggest)
- Official SDKs:
  - [JavaScript SDK](https://github.com/globalMOO/gmoo-sdk-javascript)
  - [Python SDK](https://github.com/globalMOO/gmoo-sdk-python)
- Official examples:
  - [globalMOO SDK example suite](https://github.com/globalMOO/gmoo-sdk-suite)
