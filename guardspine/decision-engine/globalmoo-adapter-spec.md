# globalMOO Adapter Specification

## What globalMOO is

Decision intelligence platform for multi-objective optimization. Model-agnostic -- works with any simulation, ML model, or spreadsheet. Returns Pareto frontier of viable solutions, not one "optimal" answer.

Site: https://globalmoo.com
Integration: 4 weeks, 5 API endpoints. No public docs yet.

## Integration approach

### Option A: globalMOO API (when available)

1. Contact globalMOO sales for API access
2. Implement 5-endpoint adapter
3. Submit decision_schema.json objectives/constraints -> get Pareto frontier back

### Option B: Local NSGA-II solver (immediate, no vendor dependency)

For MVP, we can run a local multi-objective optimizer using pymoo (Python):

```python
# pip install pymoo
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
import numpy as np

class FounderTimeAllocation(Problem):
    def __init__(self):
        super().__init__(
            n_var=4,    # h_sales, h_marketing, h_product, h_partnerships
            n_obj=3,    # maximize pipeline, minimize burn, maximize learning
            n_constr=1, # total hours <= 50
            xl=np.array([0, 0, 10, 0]),   # min hours per activity
            xu=np.array([25, 15, 25, 15]), # max hours per activity
        )

    def _evaluate(self, X, out, *args, **kwargs):
        h_sales, h_marketing, h_product, h_partnerships = X.T

        # Objective 1: maximize pipeline (negative for minimization)
        f1 = -(0.3 * h_sales + 0.2 * h_marketing + 0.1 * h_partnerships)

        # Objective 2: minimize founder burn
        f2 = 0.4 * (h_sales + h_marketing) + 0.1 * h_product

        # Objective 3: maximize learning (negative for minimization)
        f3 = -(0.2 * h_product + 0.15 * h_partnerships + 0.05 * h_marketing)

        out["F"] = np.column_stack([f1, f2, f3])

        # Constraint: total hours <= 50
        out["G"] = np.column_stack([
            (h_sales + h_marketing + h_product + h_partnerships) - 50
        ])

problem = FounderTimeAllocation()
algorithm = NSGA2(pop_size=100)
res = minimize(problem, algorithm, ('n_gen', 200), seed=42, verbose=False)

# res.X = Pareto-optimal decision vectors
# res.F = corresponding objective values
```

This gives us a working Pareto optimizer TODAY without waiting for globalMOO access.

### Option C: Hybrid

Use local pymoo for weekly planning (fast, free, no API dependency).
Use globalMOO for complex multi-model scenarios when API access arrives.

## Adapter interface

Regardless of backend (globalMOO API or local pymoo), the adapter accepts our decision_schema.json and returns:

```json
{
  "decision_id": "ds_2026_03_17_002",
  "solver": "pymoo_nsga2",
  "solutions": [
    {
      "id": "frontier_A",
      "mode": "growth",
      "variables": { "h_sales": 20, "h_marketing": 12, "h_product": 12, "h_partnerships": 6 },
      "objectives": { "pipeline": 0.92, "burn": 0.48, "learning": 0.64 }
    },
    {
      "id": "frontier_B",
      "mode": "balanced",
      "variables": { "h_sales": 15, "h_marketing": 10, "h_product": 18, "h_partnerships": 7 },
      "objectives": { "pipeline": 0.78, "burn": 0.32, "learning": 0.81 }
    }
  ],
  "pareto_size": 2,
  "compute_time_ms": 450
}
```

## Recommended first deployment

Option B (local pymoo). Zero vendor dependency. Deploy as a Python function inside the decision-engine service. Swap to globalMOO API later if warranted.
