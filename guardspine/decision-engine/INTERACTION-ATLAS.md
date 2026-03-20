# Decision Engine Interaction Atlas (Formal)

## The Three Operators

- **S = MiroFish**: swarm/world simulation (emergent dynamics, scenario generation)
- **G = Mieza**: formal game-solving / repeated-game policy (equilibrium, next-action)
- **O = globalMOO/pymoo**: multi-objective inverse optimization (Pareto frontier, tradeoffs)

## 1. Single-Tool Modes

| Tool | Inputs                                            | Outputs                                             | Use when                                  | Do not use when                                 |
| ---- | ------------------------------------------------- | --------------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| S    | seed materials, archetypes, environment, horizon  | scenario set, emergent reactions, instability flags | main uncertainty is social/emergent       | problem is already a clean game or optimization |
| G    | players, actions, payoffs or repeated-game state  | equilibrium candidates, policy, next action         | main uncertainty is strategic interaction | latent world dynamics dominate                  |
| O    | objectives, constraints, variables, forward model | Pareto frontier, candidate operating points         | main uncertainty is tradeoff balancing    | world structure or strategy space unclear       |

## 2. Pairwise Modes

### S -> G: Simulation discovers/refines the formal game

- Inputs: MiroFish outputs, candidate actors, observed branches
- Outputs: refined player list, new strategies, updated payoff asymmetries
- Use: game framing likely underspecified, hidden actors emerging
- Example: simulate buyer committee, discover "delay for internal review" is a real strategy

### G -> S: Game logic disciplines simulation agents

- Inputs: Mieza equilibrium/policy, agent-role mapping in MiroFish
- Outputs: strategically coherent agents in simulated world
- Use: procurement/competitor/partner agents should behave strategically
- Example: inject equilibrium pricing policy into competitor agents

### S -> O: Simulation parameterizes optimization

- Inputs: scenario distributions from MiroFish, KPI mapping rules
- Outputs: scenario-weighted coefficients, uncertainty bands, risk penalties
- Use: uncertain world response, but final problem is choosing efficient action
- Example: three plausible buyer-response worlds, pick best-across-all action

### O -> S: Optimization tunes the simulator

- Inputs: candidate sim configs (swarm size, archetypes, memory depth, cost)
- Outputs: selected config on Pareto frontier of calibration vs cost
- Use: calibrating MiroFish for stable, affordable forecasting
- Highest-value non-obvious use. globalMOO should choose minimum effective swarm.

### G -> O: Strategic outputs constrain optimization (MOST COMMON)

- Inputs: Mieza strategic postures, policy recommendations
- Outputs: frontier over business plans conditional on those postures
- Use: first right strategic move, then best business plan around it
- Example: hold price vs concession -> choose which balances ACV, trust, cycle time

### O -> G: Optimization reshapes the game

- Inputs: internal objectives, acceptable tradeoff ranges, hard constraints
- Outputs: constrained payoff assumptions or allowed move set for Mieza
- Use: company doctrine should narrow strategic space before solving
- Example: margin discipline removes "deep discount" from seller strategy space

## 3. Three-Tool Modes

### S -> G -> O: Discover -> solve -> choose (major moves)

- Full stack for simultaneously emergent + strategic + constrained decisions
- Canonical use: major pricing/positioning shift

### G -> O -> S: Solve -> optimize -> stress-test (verification)

- Most practical verification route. MiroFish as late-stage robustness test.
- Use: chosen plan needs simulation validation before execution

### G -> S -> O: Solve core -> simulate spillovers -> optimize rollout

- Strong for category strategy. Core interaction clear, spillovers uncertain.
- Example: pricing posture -> simulate buyer discourse -> optimize rollout timing

### S -> O -> G: Discover -> optimize targets -> solve interaction

- Fix internal target region from scenarios, then solve strategic move within it
- Less common but valid when internal operating target must be fixed first

### O -> S -> G: Optimize -> simulate -> solve subgame

- Internal constraints dominate, strategic interaction emerges within envelope
- Rarer use case

### O -> G -> S: Optimize -> solve -> stress-test

- Constitutional priorities first, then constrained game, then simulation validation
- Use when doctrine is primary and simulation is final check

## 4. Feedback Loops

### S <-> G: World-model/game co-calibration

- S reveals hidden actors/strategies missing from G
- G disciplines unrealistic simulation agents
- Track: disagreement records, root-cause tags

### S <-> O: Simulation/optimization co-calibration

- S outputs scenarios, O selects robust decisions + retunes sim config
- Track: forecast-vs-reality metrics, cost metrics

### G <-> O: Strategy/optimization co-calibration

- G gives postures, O chooses among them, outcomes revise payoffs
- Track: payoff revisions, KPI bundle, next-round policy update

### S <-> G <-> O <-> Reality: Full empirical learning loop

- Complete case trace, forecast errors, root-cause analysis, updated priors
- Only for decisions that recur enough to justify cumulative learning

## 5. Routing Doctrine

| Case structure                               | Recommended combo          |
| -------------------------------------------- | -------------------------- |
| Emergent social uncertainty only             | S                          |
| Formal negotiation/repeated interaction only | G                          |
| Internal tradeoff only                       | O                          |
| World uncertainty then strategy              | S -> G                     |
| World uncertainty then robust plan           | S -> O                     |
| Strategic posture then business-plan choice  | G -> O                     |
| Game informs simulation realism              | G -> S                     |
| Simulation tuning                            | O -> S                     |
| Major coupled decision                       | S -> G -> O or G -> O -> S |

## 6. Memory Write-Back Contract

Every pass appends a structured trace:

```yaml
case_id:
timestamp:
route_taken:
inputs_snapshot:
  substrate_refs:
  human_request:
  relevant_history:
tool_passes:
  - tool: mirofish | mieza | globalmoo
    input_object:
    output_object:
    confidence:
    config:
decision_artifacts:
  candidate_actions:
  chosen_action:
  governance_status:
execution_artifacts:
  workflow_id:
  owner_role:
  action_status:
outcomes:
  projected_metrics:
  actual_metrics:
  variance:
disagreement_analysis:
  mirofish_vs_mieza:
  mirofish_vs_reality:
  mieza_vs_reality:
  globalmoo_vs_reality:
  root_cause_tags:
learning_updates:
  archetype_updates:
  payoff_updates:
  objective_updates:
  routing_updates:
```

## 7. Root-Cause Tags (Fixed Vocabulary)

- missing_player
- missing_strategy
- bad_payoff_estimate
- simulation_instability
- archetype_homogenization
- objective_misspecification
- missing_constraint
- overfit_to_recent_data
- execution_noise
- governance_intervention_changed_outcome

## 8. GuardSpine Priority Order

1. G -> O (pricing, procurement, partnerships)
2. S -> O (messaging, positioning, category moves)
3. S <-> G (improving world realism and game framing)
4. O -> S (simulator-cost calibration)
5. S -> G -> O (high-stakes coupled moves only)
