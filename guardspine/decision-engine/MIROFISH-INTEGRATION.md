# MiroFish Integration Specification

## Architecture Decision

Deploy stock MiroFish backend as a Railway service. Do NOT wrap OASIS directly.

Rationale: MiroFish already has a 30+ endpoint REST API covering the full pipeline
(upload -> ontology -> graph -> simulate -> report). Writing our own OASIS wrapper
would duplicate this work. R9: incremental improvement over rewrites.

## Service Configuration

```
Railway service: mirofish
Port: 5001 (internal only)
Image: Python 3.11 (from MiroFish Dockerfile)
Volume: /app/backend/uploads (simulation state, reports)

Environment:
  LLM_BASE_URL=http://litellm.railway.internal:4000/v1
  LLM_API_KEY=sk-gs-...  (LiteLLM master key)
  LLM_MODEL_NAME=deepseek-chat
  ZEP_API_KEY=...  (Zep Cloud free tier)
  OASIS_DEFAULT_MAX_ROUNDS=10
```

## Integration Flow (S-operator)

### For simulation_only route:

1. Decision router receives decision with decision_type=simulation_only
2. Router calls MiroFish API:

```
Step 1: POST /api/graph/ontology/generate
  - Upload seed content as text file
  - simulation_requirement: "Simulate how CISOs react to this positioning"

Step 2: POST /api/graph/build
  - project_id from step 1
  - Builds Zep knowledge graph from seed materials

Step 3: POST /api/simulation/create
  - Links project + graph

Step 4: POST /api/simulation/prepare
  - Generates agent profiles from graph entities
  - Generates simulation config via LLM

Step 5: POST /api/simulation/start
  - Runs OASIS simulation (subprocess)
  - Poll GET /api/simulation/run/status

Step 6: POST /api/report/generate
  - ReACT agent analyzes simulation traces
  - Returns structured prediction report
```

3. Router converts report to case_trace format
4. Writes to case_traces + telemetry_events tables

### For simulation_optimization (S -> O):

Same as above, then:

- Extract scenario distributions from MiroFish report
- Convert to pymoo objective coefficients
- Run Pareto optimization
- Return combined result

### For full_stack (S -> G -> O):

Same as above, then:

- Extract actors/strategies from MiroFish report -> Mieza game framing
- Mieza computes equilibrium
- Equilibrium constrains pymoo optimization
- Return three-stage result

## Cost Model

Per simulation (50 agents, 10 rounds):

- Graph building: ~5 LLM calls = ~$0.01
- Profile generation: ~50 LLM calls = ~$0.05
- Config generation: ~3 LLM calls = ~$0.01
- Simulation: 50 agents x 10 rounds = 500 LLM calls = ~$0.11
- Report generation: ~10 LLM calls = ~$0.02
- Total: ~$0.20 per simulation
- Budget: max 50 simulations/day = $10 (within LiteLLM ceiling)

## Prerequisites

1. Fork MiroFish to DNYoussef/mirofish (private)
2. Sign up for Zep Cloud (https://app.getzep.com) -- free tier
3. Get Zep API key

## MiroFish API Quick Reference

### Graph Blueprint (/api/graph/)

- POST /ontology/generate -- upload files, generate ontology
- POST /build -- build Zep knowledge graph (async)
- GET /task/{task_id} -- poll async task
- GET /data/{graph_id} -- get graph nodes + edges

### Simulation Blueprint (/api/simulation/)

- POST /create -- create simulation
- POST /prepare -- generate profiles + config (async)
- POST /start -- run OASIS simulation
- GET /run/status -- poll simulation progress
- POST /interview -- interview a specific agent
- GET /{sim_id}/profiles -- get generated agent profiles
- GET /{sim_id}/config -- get generated simulation config

### Report Blueprint (/api/report/)

- POST /generate -- ReACT agent analysis (async)
- GET /generate/status -- poll report generation
- GET /{report_id} -- get report
- POST /chat -- chat with ReportAgent

### Health

- GET /health -- returns {"status": "ok", "service": "MiroFish Backend"}

## Alternative: Custom OASIS Wrapper (Tier 1 fallback)

If MiroFish proves too heavy or Zep dependency is unwanted, fall back to
the custom mirofish-sim/app.py wrapper that calls OASIS directly.
This loses: graph building, LLM-generated profiles, report generation.
It keeps: basic simulation with predefined archetype profiles.

The custom wrapper is already built at guardspine/mirofish-sim/app.py.
