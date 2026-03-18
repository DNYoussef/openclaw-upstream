"""Decision router: classify decisions and route to correct solver.

Primitive routes:
  policy_only          -> GuardSpine (can this action happen?)
  optimization_only    -> O: pymoo NSGA-II (what tradeoff is best?)
  strategic_only       -> G: Mieza MCP (how will actors react?)
  simulation_only      -> S: MiroFish (what worlds emerge?)

Pairwise compositions:
  strategic_optimization -> G -> O (posture then plan -- enterprise GTM)
  simulation_optimization -> S -> O (scenario then robust action -- weekly planning)
  simulation_strategic   -> S -> G (discover world then solve interaction -- category strategy)
  strategic_simulation   -> G -> S (discipline agents then simulate -- verification)

Three-tool:
  full_stack           -> S -> G -> O (discover -> solve -> choose -- major moves)
  verify_stack         -> G -> O -> S (solve -> optimize -> stress-test -- validation)

See INTERACTION-ATLAS.md for the full combinatorial space.
Runs as a standalone service or importable module.
"""

import json
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timezone

import psycopg2

DB_URL = os.environ.get("DATABASE_URL", "")
PORT = int(os.environ.get("PORT", "8091"))


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
    """Optimization-only: run local pymoo NSGA-II."""
    objectives = decision.get("objectives", [])
    constraints = decision.get("constraints", [])
    action_space = decision.get("action_space", [])

    # For MVP, return a structured recommendation without running pymoo
    # (pymoo requires numpy which adds container size)
    maximize = [o for o in objectives if o["direction"] == "maximize"]
    minimize = [o for o in objectives if o["direction"] == "minimize"]

    return {
        "solver": "pymoo_nsga2_stub",
        "status": "schema_validated",
        "objectives_maximize": [o["name"] for o in maximize],
        "objectives_minimize": [o["name"] for o in minimize],
        "counter_kpis": {
            o["name"]: o.get("counter_metric", "none")
            for o in objectives if o.get("counter_metric")
        },
        "action_space": action_space,
        "recommendation": "Use pymoo locally: from pymoo.algorithms.moo.nsga2 import NSGA2",
        "note": "Full solver requires pymoo install. This stub validates the schema.",
    }


def solve_strategic(decision):
    """Strategic-only: prepare Mieza MCP call."""
    actors = decision.get("actors", [])
    uncertainties = decision.get("uncertainties", [])

    return {
        "solver": "mieza_mcp_stub",
        "status": "schema_validated",
        "actors": [{"name": a["name"], "role": a["role"]} for a in actors],
        "uncertainties": [u["name"] for u in uncertainties],
        "recommendation": "Call Mieza MCP at https://mieza.ai/mcp with game matrix",
        "note": "Requires Mieza API token. This stub validates the schema.",
    }


def solve_simulation(decision):
    """Simulation-only: run OASIS social simulation via mirofish-sim service."""
    actors = decision.get("actors", [])
    uncertainties = decision.get("uncertainties", [])
    sim_config = decision.get("simulation_config", {})

    # If mirofish-sim is available, submit a real simulation
    mirofish_url = os.environ.get("MIROFISH_SIM_URL", "http://mirofish-sim.railway.internal:5001")

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
        "status": "schema_validated",
        "flow": "G -> O: Mieza strategic posture -> pymoo Pareto frontier",
        "stage_1_strategic": strategic,
        "stage_2_optimization": optimization,
    }


def solve_simulation_optimization(decision):
    """S -> O: Scenario uncertainty then robust action choice."""
    simulation = solve_simulation(decision)
    optimization = solve_optimization(decision)

    return {
        "solver": "mirofish_then_pymoo",
        "status": "schema_validated",
        "flow": "S -> O: MiroFish scenarios -> pymoo robust optimization",
        "stage_1_simulation": simulation,
        "stage_2_optimization": optimization,
    }


def solve_simulation_strategic(decision):
    """S -> G: Discover world then solve interaction."""
    simulation = solve_simulation(decision)
    strategic = solve_strategic(decision)

    return {
        "solver": "mirofish_then_mieza",
        "status": "schema_validated",
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
        "status": "schema_validated",
        "flow": "S -> G -> O: Full stack (major positioning moves only)",
        "stage_1_simulation": simulation,
        "stage_2_strategic": strategic,
        "stage_3_optimization": optimization,
    }


def solve_verify_stack(decision):
    """G -> O -> S: Solve -> optimize -> stress-test."""
    strategic = solve_strategic(decision)
    optimization = solve_optimization(decision)
    simulation = solve_simulation(decision)

    return {
        "solver": "mieza_pymoo_mirofish",
        "status": "schema_validated",
        "flow": "G -> O -> S: Solve strategic -> optimize plan -> stress-test in simulation",
        "stage_1_strategic": strategic,
        "stage_2_optimization": optimization,
        "stage_3_verification": simulation,
    }


SOLVERS = {
    # Primitives
    "policy_only": solve_policy,
    "optimization_only": solve_optimization,
    "strategic_only": solve_strategic,
    "simulation_only": solve_simulation,
    # Pairwise
    "strategic_optimization": solve_strategic_optimization,
    "simulation_optimization": solve_simulation_optimization,
    "simulation_strategic": solve_simulation_strategic,
    # Three-tool
    "full_stack": solve_full_stack,
    "verify_stack": solve_verify_stack,
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

    # Log to decision_journal if DB is available
    if DB_URL:
        try:
            log_decision(decision, output)
        except Exception as e:
            output["journal_error"] = str(e)

    return output


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
            self._json(200, {"status": "ok", "solvers": list(SOLVERS.keys())})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/decide":
            self._json(404, {"error": "not found"})
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

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, fmt, *args):
        print(f"[decision-router] {self.command} {self.path} {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[decision-router] listening on 0.0.0.0:{PORT}")
    print(f"[decision-router] solvers: {list(SOLVERS.keys())}")
    print(f"[decision-router] journal: {'enabled' if DB_URL else 'disabled'}")
    server.serve_forever()
