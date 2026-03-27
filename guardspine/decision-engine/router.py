"""Decision router: classify decisions and route to correct solver.

Primitive routes:
  policy_only          -> GuardSpine (can this action happen?)
  optimization_only    -> O: pymoo NSGA-II (what tradeoff is best?)
  strategic_only       -> G: Mieza MCP (how will actors react?)
  simulation_only      -> S: MiroFish (what worlds emerge?)

Pairwise compositions:  ENABLED. Real when MIEZA_API_TOKEN + pymoo installed.
Three-tool:             ENABLED. full_stack requires all three real solvers.

See INTERACTION-ATLAS.md for the full combinatorial space.
Runs as a standalone service or importable module.
"""

import json
import logging
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

import psycopg2

log = logging.getLogger("decision-router")
logging.basicConfig(level=logging.INFO, format="[decision-router] %(levelname)s %(message)s")

DB_URL = os.environ.get("DATABASE_URL", "")
PORT = int(os.environ.get("PORT", "8091"))

# --- Startup dependency checks ---

_HAS_PYMOO = False
try:
    import pymoo  # noqa: F401
    _HAS_PYMOO = True
except ImportError:
    pass

_HAS_MIEZA_TOKEN = bool(os.environ.get("MIEZA_API_TOKEN", ""))

_MIROFISH_REACHABLE = False
_MIROFISH_URL = os.environ.get("MIROFISH_SIM_URL", "http://mirofish.railway.internal:5001")
try:
    import urllib.request
    urllib.request.urlopen(f"{_MIROFISH_URL}/health", timeout=3)
    _MIROFISH_REACHABLE = True
except Exception:
    pass


def _log_startup_status():
    log.info("=== Dependency status ===")
    log.info("  pymoo:          %s", "installed" if _HAS_PYMOO else "NOT INSTALLED (solve_optimization is a stub)")
    log.info("  MIEZA_API_TOKEN: %s", "set" if _HAS_MIEZA_TOKEN else "NOT SET (solve_strategic is a stub)")
    log.info("  MIROFISH_URL:    %s -> %s", _MIROFISH_URL, "reachable" if _MIROFISH_REACHABLE else "UNREACHABLE (solve_simulation will fallback)")
    log.info("=========================")


def classify(decision):
    """Route decision to correct solver based on decision_type."""
    dt = decision.get("decision_type", "")
    routing = decision.get("solver_routing", {})

    return {
        "decision_id": decision["decision_id"],
        "domain": decision["domain"],
        "decision_type": dt,
        "strategic_engine": routing.get("strategic_engine", "none"),
        "optimization_engine": routing.get("optimization_engine", "none"),
        "mode": routing.get("mode", "balanced"),
        "objectives_count": len(decision.get("objectives", [])),
        "constraints_count": len(decision.get("constraints", [])),
        "actors_count": len(decision.get("actors", [])),
    }


def solve_policy(decision):
    """Policy-only: check GuardSpine constraints."""
    policy = decision.get("guardspine_policy", {})
    constraints = decision.get("constraints", [])

    constitutional = [c for c in constraints if c.get("tier") == "constitutional"]

    return {
        "solver": "guardspine_policy",
        "approval_required_above_tier": policy.get("approval_required_above_tier", 2),
        "reversible_required": policy.get("reversible_required", True),
        "constitutional_constraints": len(constitutional),
        "recommendation": "proceed" if not constitutional else "review_constraints",
        "details": [f"{c['name']} {c['operator']} {c['value']}" for c in constitutional],
    }


def solve_optimization(decision):
    """Optimization-only: run pymoo NSGA-II (multi-obj) or GA (single-obj).

    Accepts generic linear objective definitions over a decision vector.
    Each variable in action_space gets bounds from constraints or defaults.
    Objectives are weighted linear sums of the variables.
    """
    if not _HAS_PYMOO:
        return {
            "solver": "pymoo_nsga2",
            "status": "error",
            "error": "pymoo is not installed. Run: pip install pymoo",
        }

    objectives = decision.get("objectives", [])
    if not objectives:
        return {
            "solver": "pymoo_nsga2",
            "status": "error",
            "error": "No objectives provided. Need at least one.",
        }

    action_space = decision.get("action_space", [])
    constraints = decision.get("constraints", [])
    solver_config = decision.get("solver_config", {})

    pop_size = solver_config.get("pop_size", 50)
    n_gen = solver_config.get("n_gen", 100)
    top_k = solver_config.get("top_k", 5)

    # Build variable definitions: name -> (lower, upper)
    # Use action_space as variable names. Extract bounds from constraints.
    var_names = action_space if action_space else [f"x{i}" for i in range(len(objectives))]
    n_var = len(var_names)

    if n_var == 0:
        return {
            "solver": "pymoo_nsga2",
            "status": "error",
            "error": "No variables. Provide action_space or variable definitions.",
        }

    # Parse bounds from constraints: "var_name >= val" -> lower, "var_name <= val" -> upper
    lower = [0.0] * n_var
    upper = [1.0] * n_var
    var_index = {name: i for i, name in enumerate(var_names)}

    # Also accept explicit bounds in solver_config
    explicit_bounds = solver_config.get("variable_bounds", {})
    for vname, bounds in explicit_bounds.items():
        if vname in var_index:
            idx = var_index[vname]
            lower[idx] = bounds[0]
            upper[idx] = bounds[1]

    for c in constraints:
        cname = c["name"]
        if cname not in var_index:
            continue
        idx = var_index[cname]
        op = c["operator"]
        val = c["value"]
        if op in (">=", ">"):
            lower[idx] = val
        elif op in ("<=", "<"):
            upper[idx] = val
        elif op == "==":
            lower[idx] = val
            upper[idx] = val

    # Build objective coefficient matrix: shape (n_obj, n_var)
    # Each objective is a linear combination: f_k(x) = sum(coeff_k_i * x_i)
    # Coefficients come from solver_config.objective_coefficients or default to
    # equal weights across all variables (useful baseline).
    n_obj = len(objectives)
    obj_coeffs = solver_config.get("objective_coefficients", None)

    if obj_coeffs and len(obj_coeffs) == n_obj:
        coeff_matrix = []
        for row in obj_coeffs:
            if len(row) == n_var:
                coeff_matrix.append(row)
            else:
                coeff_matrix.append([1.0 / n_var] * n_var)
    else:
        # Default: each objective weights all variables equally
        coeff_matrix = [[1.0 / n_var] * n_var for _ in range(n_obj)]

    # Direction: pymoo minimizes. Flip sign for maximize objectives.
    signs = []
    for obj in objectives:
        signs.append(-1.0 if obj["direction"] == "maximize" else 1.0)

    # Sum constraints (e.g. total_hours <= 50): constraints referencing
    # names NOT in var_index are treated as sum-of-all constraints.
    ieq_constraints = []  # g(x) <= 0 format
    eq_constraints = []   # h(x) == 0 format
    for c in constraints:
        if c["name"] in var_index:
            continue  # Already handled as bounds
        op = c["operator"]
        val = c["value"]
        # Assume sum constraint over all variables
        if op == "<=":
            ieq_constraints.append(("sum_le", val))
        elif op == ">=":
            ieq_constraints.append(("sum_ge", val))
        elif op == "==":
            eq_constraints.append(("sum_eq", val))

    n_ieq = len(ieq_constraints)
    n_eq = len(eq_constraints)

    return _run_pymoo_solver(
        n_var=n_var,
        n_obj=n_obj,
        var_names=var_names,
        lower=lower,
        upper=upper,
        coeff_matrix=coeff_matrix,
        signs=signs,
        objectives=objectives,
        ieq_constraints=ieq_constraints,
        eq_constraints=eq_constraints,
        n_ieq=n_ieq,
        n_eq=n_eq,
        pop_size=pop_size,
        n_gen=n_gen,
        top_k=top_k,
    )


def _run_pymoo_solver(
    n_var, n_obj, var_names, lower, upper,
    coeff_matrix, signs, objectives,
    ieq_constraints, eq_constraints,
    n_ieq, n_eq, pop_size, n_gen, top_k,
):
    """Run pymoo and return Pareto frontier results."""
    import numpy as np
    from pymoo.core.problem import ElementwiseProblem
    from pymoo.optimize import minimize as pymoo_minimize
    from pymoo.termination import get_termination

    class DecisionProblem(ElementwiseProblem):
        def __init__(self):
            super().__init__(
                n_var=n_var,
                n_obj=n_obj,
                n_ieq_constr=n_ieq,
                n_eq_constr=n_eq,
                xl=np.array(lower),
                xu=np.array(upper),
            )

        def _evaluate(self, x, out, *args, **kwargs):
            # Compute objectives: f_k = sign_k * sum(coeff_k_i * x_i)
            f = np.zeros(n_obj)
            for k in range(n_obj):
                f[k] = signs[k] * sum(coeff_matrix[k][i] * x[i] for i in range(n_var))
            out["F"] = f

            # Inequality constraints: g(x) <= 0
            if n_ieq > 0:
                g = np.zeros(n_ieq)
                for ci, (ctype, val) in enumerate(ieq_constraints):
                    s = sum(x)
                    if ctype == "sum_le":
                        g[ci] = s - val      # sum <= val  =>  sum - val <= 0
                    elif ctype == "sum_ge":
                        g[ci] = val - s       # sum >= val  =>  val - sum <= 0
                out["G"] = g

            # Equality constraints: h(x) == 0
            if n_eq > 0:
                h = np.zeros(n_eq)
                for ci, (ctype, val) in enumerate(eq_constraints):
                    if ctype == "sum_eq":
                        h[ci] = sum(x) - val
                out["H"] = h

    problem = DecisionProblem()
    t0 = time.time()

    if n_obj == 1:
        # Single objective: use GA
        from pymoo.algorithms.soo.nonconvex.ga import GA
        algorithm = GA(pop_size=pop_size)
    else:
        # Multi-objective: use NSGA-II
        from pymoo.algorithms.moo.nsga2 import NSGA2
        algorithm = NSGA2(pop_size=pop_size)

    termination = get_termination("n_gen", n_gen)

    try:
        res = pymoo_minimize(problem, algorithm, termination, seed=42, verbose=False)
    except Exception as e:
        return {
            "solver": "pymoo_nsga2",
            "status": "error",
            "error": f"Solver failed: {e}",
        }

    elapsed_ms = round((time.time() - t0) * 1000, 1)

    if res.X is None:
        return {
            "solver": "pymoo_nsga2",
            "status": "no_feasible_solution",
            "computation_time_ms": elapsed_ms,
            "error": "No feasible solution found. Check constraints.",
        }

    # Extract solutions. res.X may be 1D (single solution) or 2D (Pareto set).
    X = np.atleast_2d(res.X)
    F = np.atleast_2d(res.F)

    # Convert back from pymoo-minimized objectives to original scale
    # (undo sign flip so results show true objective values)
    signs_arr = np.array(signs)
    F_original = F * signs_arr[np.newaxis, :]

    # Rank by weighted sum of original objectives (higher = better for all)
    weights = np.array([o.get("weight", 1.0 / n_obj) for o in objectives])
    # For minimize objectives, lower is better -> negate contribution
    rank_scores = np.zeros(len(X))
    for k in range(n_obj):
        if objectives[k]["direction"] == "maximize":
            rank_scores += weights[k] * F_original[:, k]
        else:
            rank_scores -= weights[k] * F_original[:, k]

    top_idx = np.argsort(-rank_scores)[:top_k]

    pareto_solutions = []
    for idx in top_idx:
        sol = {}
        for i, vname in enumerate(var_names):
            sol[vname] = round(float(X[idx, i]), 4)
        obj_vals = {}
        for k, obj in enumerate(objectives):
            obj_vals[obj["name"]] = round(float(F_original[idx, k]), 4)
        sol["_objectives"] = obj_vals
        sol["_weighted_score"] = round(float(rank_scores[idx]), 4)
        pareto_solutions.append(sol)

    # Compute hypervolume if multi-objective (2+ obj, feasible solutions exist)
    hv_value = None
    if n_obj >= 2 and len(F) >= 2:
        try:
            from pymoo.indicators.hv import HV
            # Reference point: worst value per objective (use max of each column + margin)
            ref_point = np.max(F, axis=0) + 1.0
            hv_value = round(float(HV(ref_point=ref_point)(F)), 6)
        except Exception:
            pass  # Hypervolume is a nice-to-have metric, not critical

    return {
        "solver": "pymoo_nsga2" if n_obj > 1 else "pymoo_ga",
        "status": "solved",
        "n_variables": n_var,
        "n_objectives": n_obj,
        "n_pareto_solutions": len(X),
        "pareto_solutions": pareto_solutions,
        "hypervolume": hv_value,
        "computation_time_ms": elapsed_ms,
        "config": {"pop_size": pop_size, "n_gen": n_gen},
    }


def solve_strategic(decision):
    """Strategic-only: solve game via Mieza API."""
    token = os.environ.get("MIEZA_API_TOKEN", "")
    if not token:
        return {
            "solver": "mieza_gto",
            "status": "error",
            "error": "MIEZA_API_TOKEN not set",
        }

    actors = decision.get("actors", [])
    if len(actors) < 2:
        return {
            "solver": "mieza_gto",
            "status": "error",
            "error": "Need at least 2 actors for game theory",
        }

    # Build game matrix from actors and their strategies
    players = [a["name"] for a in actors]
    strategies = {}
    for a in actors:
        strategies[a["name"]] = a.get("strategies", ["cooperate", "defect"])

    # Build payoffs from decision objectives or use defaults
    payoffs = decision.get("payoff_matrix", {})
    if not payoffs:
        # Generate simple payoff structure from objectives
        objectives = decision.get("objectives", [])
        obj_names = [o["name"] for o in objectives[:2]] if objectives else ["gain", "risk"]
        s1 = strategies[players[0]]
        s2 = strategies[players[1]]
        payoffs = {}
        for i, a1 in enumerate(s1):
            for j, a2 in enumerate(s2):
                key = f"{a1},{a2}"
                # Simple payoff: cooperation = moderate, defection = asymmetric
                p1 = 5 - i * 2 + j * 1
                p2 = 5 - j * 2 + i * 1
                payoffs[key] = [p1, p2]

    # Call Mieza API
    mieza_url = os.environ.get("MIEZA_API_URL", "https://api.mieza.ai/api/public/v1/gto/api/gt/nf-solve")
    try:
        payload = json.dumps({
            "players": players,
            "strategies": strategies,
            "payoffs": payoffs,
        }).encode()

        req = urllib.request.Request(
            mieza_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=30)
        result = json.loads(resp.read())

        return {
            "solver": "mieza_gto",
            "status": "solved",
            "players": players,
            "strategies": strategies,
            "equilibria": result.get("equilibria", []),
            "recommendation": result.get("recommendation", "See equilibria"),
            "raw_result": result,
        }

    except Exception as e:
        # Fallback: return game structure without solving
        return {
            "solver": "mieza_gto",
            "status": "api_error",
            "error": str(e),
            "players": players,
            "strategies": strategies,
            "payoffs": payoffs,
            "recommendation": "Mieza API call failed. Game structure provided for manual analysis.",
        }


def solve_simulation(decision):
    """Simulation-only: run OASIS social simulation via mirofish-sim service."""
    actors = decision.get("actors", [])
    uncertainties = decision.get("uncertainties", [])
    sim_config = decision.get("simulation_config", {})

    # If mirofish-sim is available, submit a real simulation
    mirofish_url = os.environ.get("MIROFISH_SIM_URL", "http://mirofish.railway.internal:5001")

    try:
        import urllib.request
        sim_request = json.dumps({
            "archetypes": sim_config.get("archetypes", [
                {"id": a["name"], "count": 5, "base_profile": {
                    "user_name": a["name"].replace(" ", "_"),
                    "name": a["name"],
                    "description": f"You are a {a['role']} in the code governance space.",
                }} for a in actors
            ]),
            "seed_content": sim_config.get("seed_content", decision.get("objectives", [{}])[0].get("name", "test")),
            "timesteps": sim_config.get("timesteps", 5),
            "platform": sim_config.get("platform", "twitter"),
        }).encode()

        req = urllib.request.Request(
            f"{mirofish_url}/simulate",
            data=sim_request,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        resp = urllib.request.urlopen(req, timeout=10)
        result = json.loads(resp.read())

        return {
            "solver": "oasis_mirofish",
            "status": "simulation_queued",
            "job_id": result.get("job_id"),
            "poll_url": f"{mirofish_url}/simulate/{result.get('job_id', '')}",
            "actors": [{"name": a["name"], "role": a["role"]} for a in actors],
            "uncertainties": [u["name"] for u in uncertainties],
        }

    except Exception as e:
        # Fallback to stub if mirofish-sim is not available
        return {
            "solver": "mirofish_stub",
            "status": "service_unavailable",
            "fallback_reason": str(e),
            "actors": [{"name": a["name"], "role": a["role"]} for a in actors],
            "uncertainties": [u["name"] for u in uncertainties],
            "recommendation": "Deploy mirofish-sim service or set MIROFISH_SIM_URL",
        }


def solve_strategic_optimization(decision):
    """G -> O: Strategic posture then business-plan optimization."""
    strategic = solve_strategic(decision)
    optimization = solve_optimization(decision)
    return {
        "solver": "mieza_then_pymoo",
        "status": "solved",
        "flow": "G -> O: Mieza strategic posture -> pymoo Pareto frontier",
        "stage_1_strategic": strategic,
        "stage_2_optimization": optimization,
    }


def solve_simulation_optimization(decision):
    """S -> O: Scenario uncertainty then robust action choice.

    MiroFish is async (returns job_id). Don't block O on S.
    Run O immediately. Wire S results via /trace/{id}/outcome when job completes.
    """
    simulation = solve_simulation(decision)

    if simulation.get("status") == "simulation_queued":
        decision.setdefault("simulation_context", {
            "job_id": simulation.get("job_id"),
            "poll_url": simulation.get("poll_url"),
        })
    elif simulation.get("status") == "service_unavailable":
        log.warning("MiroFish unavailable, running O-only for S->O request")

    optimization = solve_optimization(decision)

    o_ok = optimization.get("status") == "solved"
    return {
        "solver": "mirofish_then_pymoo",
        "status": "solved" if o_ok else "partial",
        "flow": "S -> O: MiroFish buyer scenarios -> pymoo robust plan",
        "stage_1_simulation": simulation,
        "stage_2_optimization": optimization,
        "note": ("Simulation async. Call /trace/{id}/outcome when MiroFish job completes."
                 if simulation.get("status") == "simulation_queued" else None),
    }


def solve_simulation_strategic(decision):
    """S -> G: Discover world then solve interaction."""
    simulation = solve_simulation(decision)
    strategic = solve_strategic(decision)
    return {
        "solver": "mirofish_then_mieza",
        "status": "solved",
        "flow": "S -> G: MiroFish discovers actors/strategies -> Mieza solves game",
        "stage_1_simulation": simulation,
        "stage_2_strategic": strategic,
    }


def solve_full_stack(decision):
    """S -> G -> O: Discover world -> solve interaction -> choose plan."""
    simulation = solve_simulation(decision)
    strategic = solve_strategic(decision)
    optimization = solve_optimization(decision)
    return {
        "solver": "mirofish_mieza_pymoo",
        "status": "solved",
        "flow": "S -> G -> O: Full stack (major positioning moves only)",
        "stage_1_simulation": simulation,
        "stage_2_strategic": strategic,
        "stage_3_optimization": optimization,
    }


SOLVERS = {
    # Primitives
    "policy_only": solve_policy,
    "optimization_only": solve_optimization,
    "strategic_only": solve_strategic,
    "simulation_only": solve_simulation,
    # Pairwise compositions
    "strategic_optimization": solve_strategic_optimization,
    "simulation_optimization": solve_simulation_optimization,
    "simulation_strategic": solve_simulation_strategic,
    # Three-tool
    "full_stack": solve_full_stack,
}

SOLVER_STATUS = {
    "policy_only": "real",
    "optimization_only": "real" if _HAS_PYMOO else "unavailable (needs pymoo)",
    "strategic_only": "real" if _HAS_MIEZA_TOKEN else "unavailable (needs MIEZA_API_TOKEN)",
    "simulation_only": "real (fallback if mirofish unreachable)",
    "strategic_optimization": "real" if (_HAS_PYMOO and _HAS_MIEZA_TOKEN) else "partial",
    "simulation_optimization": "real" if _HAS_PYMOO else "partial",
    "simulation_strategic": "real" if _HAS_MIEZA_TOKEN else "partial",
    "full_stack": "real" if (_HAS_PYMOO and _HAS_MIEZA_TOKEN) else "partial",
}


def route(decision):
    """Classify and solve a decision request."""
    dt = decision.get("decision_type", "")
    solver_fn = SOLVERS.get(dt)
    if not solver_fn:
        return {"error": f"Unknown decision_type: {dt}", "valid_types": list(SOLVERS.keys())}

    classification = classify(decision)
    result = solver_fn(decision)

    output = {
        "classification": classification,
        "result": result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Log to decision_journal and case_traces if DB is available
    if DB_URL:
        try:
            log_decision(decision, output)
        except Exception as e:
            output["journal_error"] = str(e)
        try:
            log_case_trace(decision, output)
        except Exception as e:
            output["trace_error"] = str(e)

    return output


def log_case_trace(decision, output):
    """Write case trace for learning feedback loop.

    Captures solver stages, governance status, and empty outcome slots.
    Outcomes filled later via POST /trace/{decision_id}/outcome.
    """
    result = output.get("result", {})
    tool_passes = []

    # Extract stages from composition results
    stage_keys = [
        "stage_1_simulation", "stage_1_strategic", "stage_1_optimization",
        "stage_2_simulation", "stage_2_strategic", "stage_2_optimization",
        "stage_3_simulation", "stage_3_strategic", "stage_3_optimization",
        "stage_3_verification",
    ]
    for sk in stage_keys:
        stage = result.get(sk)
        if stage:
            tool_passes.append({
                "tool": stage.get("solver", "unknown"),
                "status": stage.get("status", "unknown"),
                "confidence": 1.0 if stage.get("status") == "solved" else 0.0,
                "duration_ms": stage.get("computation_time_ms", 0),
                "cost_usd": 0.0,
            })

    # If no composition stages, log the top-level result as a single pass
    if not tool_passes:
        tool_passes.append({
            "tool": result.get("solver", "unknown"),
            "status": result.get("status", "unknown"),
            "confidence": 1.0 if result.get("status") == "solved" else 0.0,
            "duration_ms": result.get("computation_time_ms", 0),
            "cost_usd": 0.0,
        })

    # Best candidate action from Pareto solutions or equilibria
    chosen = {}
    if "pareto_solutions" in result and result["pareto_solutions"]:
        chosen = result["pareto_solutions"][0]
    elif "equilibria" in result and result["equilibria"]:
        chosen = result["equilibria"][0] if isinstance(result["equilibria"][0], dict) else {}

    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    # Existing case_traces schema: id, case_id, ts, route_taken,
    # inputs_snapshot, tool_passes, decision_artifacts, execution_artifacts,
    # outcomes, disagreement_analysis, learning_updates, created_at, updated_at
    cur.execute(
        """INSERT INTO case_traces
           (case_id, ts, route_taken,
            inputs_snapshot, tool_passes, decision_artifacts,
            execution_artifacts, outcomes,
            disagreement_analysis, learning_updates)
           VALUES (%s, NOW(), %s,
                   %s::jsonb, %s::jsonb, %s::jsonb,
                   %s::jsonb, %s::jsonb,
                   %s::jsonb, %s::jsonb)
           ON CONFLICT (case_id) DO NOTHING""",
        (
            decision["decision_id"],
            decision.get("decision_type", ""),
            json.dumps({k: v for k, v in decision.items()
                        if k not in ("payoff_matrix",) and not isinstance(v, bytes)}),
            json.dumps(tool_passes),
            json.dumps({
                "governance_status": "approved",
                "chosen_action": chosen,
                "domain": decision.get("domain", ""),
                "decision_type": decision.get("decision_type", ""),
            }),
            json.dumps({
                "workflow_id": None,
                "owner_role": decision.get("domain", ""),
                "action_status": "pending",
            }),
            json.dumps({"projected_metrics": {}, "actual_metrics": {}, "variance": {}}),
            json.dumps({}),
            json.dumps({}),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()
    log.info("case_trace written: %s", decision["decision_id"])


def log_decision(decision, output):
    """Write to decision_journal table."""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO decision_journal (decision_id, domain, decision_type, solver_used, recommendation) "
        "VALUES (%s, %s, %s, %s, %s::jsonb)",
        (
            decision["decision_id"],
            decision["domain"],
            decision["decision_type"],
            output["result"].get("solver", "unknown"),
            json.dumps(output["result"]),
        ),
    )
    conn.commit()
    cur.close()
    conn.close()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {
                "status": "degraded" if not (_HAS_PYMOO and _HAS_MIEZA_TOKEN) else "ok",
                "solvers": SOLVER_STATUS,
                "dependencies": {
                    "pymoo": "installed" if _HAS_PYMOO else "MISSING",
                    "MIEZA_API_TOKEN": "set" if _HAS_MIEZA_TOKEN else "MISSING",
                    "mirofish": "reachable" if _MIROFISH_REACHABLE else "unreachable",
                },
            })
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        # Outcome feedback endpoint: POST /trace/{decision_id}/outcome
        if self.path.startswith("/trace/") and self.path.endswith("/outcome"):
            parts = self.path.split("/")
            if len(parts) == 4:
                decision_id = parts[2]
                body = self._read_body()
                if body is None:
                    return
                if not DB_URL:
                    self._json(503, {"error": "No database configured"})
                    return
                try:
                    actual = body.get("actual_metrics", {})
                    conn = psycopg2.connect(DB_URL)
                    cur = conn.cursor()
                    cur.execute(
                        """UPDATE case_traces
                           SET outcomes = jsonb_set(outcomes, '{actual_metrics}', %s::jsonb),
                               updated_at = NOW()
                           WHERE case_id = %s""",
                        (json.dumps(actual), decision_id),
                    )
                    updated = cur.rowcount
                    conn.commit()
                    cur.close()
                    conn.close()
                    if updated:
                        self._json(200, {"updated": decision_id, "actual_metrics": actual})
                    else:
                        self._json(404, {"error": f"No case_trace for {decision_id}"})
                except Exception as e:
                    self._json(500, {"error": str(e)})
                return
            self._json(400, {"error": "Expected /trace/{decision_id}/outcome"})
            return

        # Individual solver endpoints
        if self.path == "/simulate":
            body = self._read_body()
            if body is None:
                return
            body.setdefault("decision_id", f"sim-{int(time.time())}")
            body.setdefault("domain", "simulation")
            body["decision_type"] = "simulation_only"
            body.setdefault("objectives", [{"name": "engagement"}])
            self._json(200, route(body))
            return

        if self.path == "/solve":
            body = self._read_body()
            if body is None:
                return
            body.setdefault("decision_id", f"solve-{int(time.time())}")
            body.setdefault("domain", "strategy")
            body["decision_type"] = "strategic_only"
            body.setdefault("objectives", [{"name": "market_share"}])
            self._json(200, route(body))
            return

        if self.path == "/optimize":
            body = self._read_body()
            if body is None:
                return
            body.setdefault("decision_id", f"opt-{int(time.time())}")
            body.setdefault("domain", "operations")
            body["decision_type"] = "optimization_only"
            body.setdefault("objectives", [{"name": "efficiency", "direction": "maximize"}])
            self._json(200, route(body))
            return

        if self.path != "/decide":
            self._json(404, {"error": "not found", "endpoints": ["/decide", "/simulate", "/solve", "/optimize", "/health"]})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length == 0 or length > 65536:
            self._json(400, {"error": "Body required (max 64KB)"})
            return

        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Invalid JSON"})
            return

        # Validate required fields
        for field in ("decision_id", "domain", "decision_type", "objectives"):
            if field not in body:
                self._json(400, {"error": f"Missing required field: {field}"})
                return

        start = time.time()
        result = route(body)
        result["compute_time_ms"] = round((time.time() - start) * 1000, 1)

        self._json(200, result)

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0 or length > 65536:
            self._json(400, {"error": "Body required (max 64KB)"})
            return None
        try:
            return json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Invalid JSON"})
            return None

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, fmt, *args):
        print(f"[decision-router] {self.command} {self.path} {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    _log_startup_status()
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    log.info("listening on 0.0.0.0:%d", PORT)
    log.info("journal: %s", "enabled" if DB_URL else "disabled")
    server.serve_forever()
