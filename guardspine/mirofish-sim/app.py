"""MiroFish Simulation Service -- OASIS social simulation wrapper.

Thin HTTP API that runs OASIS agent simulations for the decision engine.
Receives archetype profiles + seed content, returns engagement analysis.

Routes:
  POST /simulate   -- start a simulation (async, returns job_id)
  GET  /simulate/{job_id} -- poll for results
  GET  /health     -- health check
"""

import asyncio
import json
import os
import sqlite3
import threading
import time
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = int(os.environ.get("PORT", "5001"))
LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "http://litellm.railway.internal:4000/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "deepseek-chat")
TRACE_DIR = os.environ.get("TRACE_DIR", "/tmp/mirofish-traces")
MAX_AGENTS = 200
MAX_TIMESTEPS = 20

# In-memory job store
jobs = {}

Path(TRACE_DIR).mkdir(parents=True, exist_ok=True)


def create_agent_profiles(archetypes):
    """Convert archetype list to OASIS-compatible agent profile dicts."""
    profiles = []
    for arch in archetypes:
        count = min(arch.get("count", 5), 50)
        base = arch.get("base_profile", arch)
        for i in range(count):
            profile = {
                "user_name": base.get("user_name", f"agent_{i}").replace("{i}", str(i)),
                "name": base.get("name", f"Agent {i}").replace("{i}", str(i)),
                "bio": base.get("bio", ""),
                "description": base.get("description", "A social media user."),
            }
            profiles.append(profile)
    return profiles[:MAX_AGENTS]


async def run_oasis_simulation(job_id, config):
    """Run an OASIS simulation. Updates jobs[job_id] with results."""
    try:
        from camel.models import ModelFactory
        from camel.types import ModelPlatformType, ModelType
        import oasis
        from oasis import ActionType, LLMAction, ManualAction

        jobs[job_id]["status"] = "running"
        jobs[job_id]["started_at"] = time.time()

        # Set up LLM model via CAMEL (OpenAI-compatible endpoint)
        os.environ["OPENAI_API_KEY"] = LLM_API_KEY
        os.environ["OPENAI_API_BASE_URL"] = LLM_BASE_URL

        model = ModelFactory.create(
            model_platform=ModelPlatformType.OPENAI,
            model_type=LLM_MODEL,
        )

        # Build agent profiles
        profiles = create_agent_profiles(config.get("archetypes", []))
        if not profiles:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No agent profiles provided"
            return

        # Define action space
        actions = [
            ActionType.CREATE_POST,
            ActionType.LIKE_POST,
            ActionType.CREATE_COMMENT,
            ActionType.REPOST,
            ActionType.FOLLOW,
            ActionType.DO_NOTHING,
        ]

        # Create agent graph
        from oasis import generate_twitter_agent_graph
        db_path = os.path.join(TRACE_DIR, f"{job_id}.db")

        # Write profiles to temp JSON for OASIS
        profile_path = os.path.join(TRACE_DIR, f"{job_id}_profiles.json")
        with open(profile_path, "w") as f:
            json.dump(profiles, f)

        agent_graph = await generate_twitter_agent_graph(
            profile_path=profile_path,
            model=model,
            available_actions=actions,
        )

        # Create environment
        env = oasis.make(
            agent_graph=agent_graph,
            platform=oasis.DefaultPlatformType.TWITTER,
            database_path=db_path,
        )
        await env.reset()

        # Seed content via ManualAction
        seed_content = config.get("seed_content", "Hello world")
        seed_agent = env.agent_graph.get_agent(0)
        await env.step({
            seed_agent: ManualAction(
                action_type=ActionType.CREATE_POST,
                action_args={"content": seed_content},
            )
        })

        # Run LLM-driven timesteps
        timesteps = min(config.get("timesteps", 5), MAX_TIMESTEPS)
        for step in range(timesteps):
            agents_dict = {
                agent: LLMAction()
                for _, agent in env.agent_graph.get_agents()
            }
            await env.step(agents_dict)
            jobs[job_id]["progress"] = f"{step + 1}/{timesteps}"

        await env.close()

        # Extract results from SQLite trace
        results = extract_results(db_path, len(profiles))

        jobs[job_id]["status"] = "completed"
        jobs[job_id]["results"] = results
        jobs[job_id]["finished_at"] = time.time()
        jobs[job_id]["duration_s"] = jobs[job_id]["finished_at"] - jobs[job_id]["started_at"]
        jobs[job_id]["agent_count"] = len(profiles)
        jobs[job_id]["timesteps"] = timesteps

        # Cleanup profile file
        try:
            os.remove(profile_path)
        except OSError:
            pass

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["finished_at"] = time.time()


def extract_results(db_path, agent_count):
    """Extract engagement metrics from OASIS SQLite trace."""
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Count actions by type
        cur.execute("SELECT action_type, COUNT(*) FROM trace GROUP BY action_type")
        action_counts = dict(cur.fetchall())

        # Count posts and comments
        cur.execute("SELECT COUNT(*) FROM post")
        post_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM comment")
        comment_count = cur.fetchone()[0]

        # Count follows
        cur.execute("SELECT COUNT(*) FROM relation WHERE relation_type = 'follow'")
        follow_count = cur.fetchone()[0]

        # Count likes
        cur.execute("SELECT COUNT(*) FROM relation WHERE relation_type = 'like'")
        like_count = cur.fetchone()[0]

        conn.close()

        engagement_rate = (post_count + comment_count + like_count) / max(agent_count, 1)

        return {
            "action_counts": action_counts,
            "posts": post_count,
            "comments": comment_count,
            "likes": like_count,
            "follows": follow_count,
            "engagement_rate": round(engagement_rate, 2),
            "trace_db": db_path,
        }
    except Exception as e:
        return {"error": str(e), "trace_db": db_path}


def start_simulation_thread(job_id, config):
    """Run simulation in a background thread with its own event loop."""
    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_oasis_simulation(job_id, config))
        loop.close()

    t = threading.Thread(target=runner, daemon=True)
    t.start()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self._json(200, {
                "status": "ok",
                "service": "mirofish-sim",
                "max_agents": MAX_AGENTS,
                "max_timesteps": MAX_TIMESTEPS,
                "llm_endpoint": LLM_BASE_URL,
                "active_jobs": sum(1 for j in jobs.values() if j["status"] == "running"),
            })
            return

        if self.path.startswith("/simulate/"):
            job_id = self.path.split("/simulate/")[1]
            if job_id in jobs:
                self._json(200, jobs[job_id])
            else:
                self._json(404, {"error": "Job not found"})
            return

        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/simulate":
            self._json(404, {"error": "not found"})
            return

        length = int(self.headers.get("Content-Length", 0))
        if length == 0 or length > 131072:
            self._json(400, {"error": "Body required (max 128KB)"})
            return

        try:
            config = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Invalid JSON"})
            return

        if not config.get("archetypes") and not config.get("agent_profiles"):
            self._json(400, {"error": "archetypes or agent_profiles required"})
            return

        job_id = str(uuid.uuid4())[:12]
        jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "created_at": time.time(),
            "config_summary": {
                "archetype_count": len(config.get("archetypes", [])),
                "timesteps": min(config.get("timesteps", 5), MAX_TIMESTEPS),
                "seed_content": (config.get("seed_content", ""))[:100],
            },
        }

        start_simulation_thread(job_id, config)
        self._json(202, {"job_id": job_id, "status": "queued", "poll_url": f"/simulate/{job_id}"})

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, fmt, *args):
        print(f"[mirofish-sim] {self.command} {self.path} {args[1] if len(args) > 1 else ''}", flush=True)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[mirofish-sim] listening on 0.0.0.0:{PORT}", flush=True)
    print(f"[mirofish-sim] LLM: {LLM_BASE_URL} model={LLM_MODEL}", flush=True)
    print(f"[mirofish-sim] traces: {TRACE_DIR}", flush=True)
    server.serve_forever()
