"""Telemetry API + Postgres query proxy.

Routes:
  POST /telemetry       -- insert telemetry event
  POST /query           -- execute named query from registry, return JSON rows
  GET  /queries         -- list available query names and parameter schemas
  GET  /kpi/{view_name} -- query a KPI view by name
  GET  /health          -- health check
"""

import json
import logging
import os
import re
import secrets
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool

DB_URL = os.environ["DATABASE_URL"]
PORT = int(os.environ.get("PORT", "8090"))
SERVICE_TOKEN = (
    os.environ.get("TELEMETRY_SERVICE_TOKEN")
    or os.environ.get("TELEMETRY_API_KEY", "")
)

# Connection pool: reuse connections instead of per-request connect/close
_pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=DB_URL)

logger = logging.getLogger("telemetry-api")
logging.basicConfig(level=logging.INFO, format="[telemetry] %(message)s")

if os.environ.get("TELEMETRY_SERVICE_TOKEN"):
    logger.info("Telemetry auth configured via TELEMETRY_SERVICE_TOKEN")
elif os.environ.get("TELEMETRY_API_KEY"):
    logger.warning("Using legacy TELEMETRY_API_KEY for telemetry auth; migrate to TELEMETRY_SERVICE_TOKEN")
else:
    logger.warning("TELEMETRY_SERVICE_TOKEN not set -- auth disabled (migration mode)")

# ---------------------------------------------------------------------------
# Query registry -- closed set of allowed queries
# ---------------------------------------------------------------------------
QUERY_REGISTRY = {
    "recent_telemetry": {
        "sql": "SELECT id, ts, service, event_type FROM telemetry_events ORDER BY ts DESC LIMIT %(limit)s",
        "params": {"limit": {"type": "int", "default": 20, "max": 1000}},
    },
    # The only query that returns payload. Every other registry entry is a projection or a
    # KPI view, so retrieving a specific governing verdict was impossible without a bounded
    # scan - and a bounded scan that misses is indistinguishable from an absent verdict.
    # artifact_sha256 filters on a payload field so a caller retrieves EXACTLY the row it
    # means, never "probably that one".
    "events_lookup": {
        "sql": (
            "SELECT id, ts, service, event_type, payload FROM telemetry_events "
            "WHERE service = %(service)s AND event_type = %(event_type)s "
            "  AND ts > NOW() - (%(since_minutes)s * INTERVAL '1 minute') "
            "  AND (%(artifact_sha256)s = '' OR payload->>'artifact_sha256' = %(artifact_sha256)s) "
            "ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "service": {"type": "str", "required": True},
            "event_type": {"type": "str", "required": True},
            "since_minutes": {"type": "int", "default": 1440, "max": 43200},
            # Omit for "no filter". If supplied it must be a real sha256 - see bind_params.
            "artifact_sha256": {"type": "str", "default": "", "pattern": r"[0-9a-fA-F]{64}"},
            "limit": {"type": "int", "default": 50, "max": 500},
        },
    },
    "kpi_health": {
        "sql": "SELECT * FROM kpi_health",
        "params": {},
    },
    "kpi_automation": {
        "sql": "SELECT * FROM kpi_automation",
        "params": {},
    },
    "kpi_governance": {
        "sql": "SELECT * FROM kpi_governance",
        "params": {},
    },
    "kpi_content": {
        "sql": "SELECT * FROM kpi_content",
        "params": {},
    },
    "kpi_funnel": {
        "sql": "SELECT * FROM kpi_funnel",
        "params": {},
    },
    "kpi_outreach": {
        "sql": "SELECT * FROM kpi_outreach",
        "params": {},
    },
    "champion_leaderboard": {
        "sql": "SELECT * FROM champion_leaderboard",
        "params": {},
    },
    "agent_heartbeats": {
        "sql": (
            "SELECT a.name, hr.status, COUNT(*) FROM heartbeat_runs hr "
            "JOIN agents a ON hr.agent_id = a.id "
            "WHERE hr.started_at > NOW() - INTERVAL %(hours)s "
            "GROUP BY a.name, hr.status ORDER BY a.name"
        ),
        "params": {"hours": {"type": "interval", "default": "24 hours"}},
    },
    "agent_status": {
        "sql": "SELECT name, status FROM agents ORDER BY name",
        "params": {},
    },
    "telemetry_by_service": {
        "sql": (
            "SELECT * FROM telemetry_events "
            "WHERE service = %(service)s ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "service": {"type": "str", "required": True},
            "limit": {"type": "int", "default": 20, "max": 1000},
        },
    },
    "cost_summary": {
        "sql": (
            "SELECT "
            "  DATE_TRUNC('day', ts) AS day, "
            "  service, "
            "  COUNT(*) AS event_count, "
            "  SUM(CASE WHEN event_type LIKE '%%error%%' OR event_type LIKE '%%billing%%' THEN 1 ELSE 0 END) AS error_count, "
            "  SUM(CASE WHEN event_type = 'llm_request' THEN 1 ELSE 0 END) AS llm_requests "
            "FROM telemetry_events "
            "WHERE ts > NOW() - INTERVAL %(days)s "
            "GROUP BY day, service "
            "ORDER BY day DESC, service"
        ),
        "params": {"days": {"type": "interval", "default": "30 days"}},
    },
    "finance_bundles": {
        "sql": (
            "SELECT id, ts, service, event_type, "
            "  payload->>'bundle_id' AS bundle_id, "
            "  payload->>'risk_tier' AS risk_tier, "
            "  payload->>'file_type' AS file_type, "
            "  payload->>'repo' AS repo "
            "FROM telemetry_events "
            "WHERE event_type IN ('bundle_created', 'sheetguard_review', 'finance_review') "
            "  AND ts > NOW() - INTERVAL %(days)s "
            "ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "days": {"type": "interval", "default": "30 days"},
            "limit": {"type": "int", "default": 50, "max": 500},
        },
    },
    "recent_decisions": {
        "sql": (
            "SELECT case_id, route_taken, "
            "  decision_artifacts->>'domain' AS domain, "
            "  decision_artifacts->>'decision_type' AS decision_type, "
            "  decision_artifacts->>'governance_status' AS governance_status, "
            "  outcomes->>'actual_metrics' AS actual_metrics, "
            "  created_at "
            "FROM case_traces "
            "ORDER BY created_at DESC LIMIT %(limit)s"
        ),
        "params": {"limit": {"type": "int", "default": 20, "max": 100}},
    },
    "agent_recent_work": {
        "sql": (
            "SELECT ts, event_type, payload "
            "FROM telemetry_events "
            "WHERE service = %(agent)s "
            "  AND ts > NOW() - INTERVAL '7 days' "
            "ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "agent": {"type": "str", "required": True},
            "limit": {"type": "int", "default": 10, "max": 50},
        },
    },
    "prospect_contact_history": {
        "sql": (
            "SELECT ts, service, event_type, "
            "  payload->>'prospect_name' AS prospect_name, "
            "  payload->>'company' AS company, "
            "  payload->>'channel' AS channel "
            "FROM telemetry_events "
            "WHERE event_type IN ('prospect_discovered', 'outreach_drafted', "
            "  'signal_briefing', 'duplicate_skipped', 'llm_call_complete') "
            "  AND ts > NOW() - INTERVAL %(days)s "
            "ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "days": {"type": "interval", "default": "14 days"},
            "limit": {"type": "int", "default": 30, "max": 200},
        },
    },
    "decision_outcomes": {
        "sql": (
            "SELECT case_id, route_taken, "
            "  decision_artifacts->>'chosen_action' AS chosen_action, "
            "  outcomes->>'projected_metrics' AS projected, "
            "  outcomes->>'actual_metrics' AS actual, "
            "  created_at "
            "FROM case_traces "
            "WHERE outcomes->>'actual_metrics' != '{}' "
            "ORDER BY created_at DESC LIMIT %(limit)s"
        ),
        "params": {"limit": {"type": "int", "default": 10, "max": 50}},
    },
    "governance_recent": {
        "sql": (
            "SELECT ts, event_type, "
            "  payload->>'tool' AS tool, "
            "  payload->>'action' AS action, "
            "  payload->>'risk_tier' AS risk_tier, "
            "  payload->>'agreement_score' AS agreement_score "
            "FROM telemetry_events "
            "WHERE service = 'guardspine' "
            "  AND event_type IN ('council_decision', 'governance_decision', 'policy_violation') "
            "  AND ts > NOW() - INTERVAL %(days)s "
            "ORDER BY ts DESC LIMIT %(limit)s"
        ),
        "params": {
            "days": {"type": "interval", "default": "7 days"},
            "limit": {"type": "int", "default": 20, "max": 100},
        },
    },
}

# Allowed KPI views (whitelist to prevent SQL injection)
ALLOWED_VIEWS = {
    "kpi_outreach", "kpi_content", "kpi_automation",
    "kpi_governance", "kpi_funnel", "kpi_health",
    "kpi_costs",
    "champion_leaderboard",
}

# Valid champion event types and their point values
CHAMPION_EVENT_POINTS = {
    "install": 1,
    "activate": 3,
    "second_repo": 5,
    "paid_convert": 15,
}


def get_conn():
    """Get a connection from the pool."""
    return _pool.getconn()


def put_conn(conn):
    """Return a connection to the pool."""
    _pool.putconn(conn)


def safe_put_conn(conn):
    """Rollback then return connection to pool. Prevents poisoned connections."""
    try:
        conn.rollback()
    except Exception:
        pass
    put_conn(conn)


def serialize_row(row):
    """Make a dict JSON-serializable."""
    out = {}
    for k, v in row.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        elif isinstance(v, (dict, list)):
            out[k] = v
        else:
            out[k] = v
    return out


def bind_params(query_def, raw_params):
    """Validate and bind parameters for a registry query.

    Returns (bound_params_dict, error_string).
    error_string is None on success.
    """
    schema = query_def["params"]
    if not schema:
        return {}, None

    bound = {}
    for name, spec in schema.items():
        required = spec.get("required", False)

        # PRESENCE decides defaulting, never the VALUE. This used to key off `val is None`,
        # which made an explicitly supplied JSON null indistinguishable from an omitted key:
        # null fell through to the default, and for artifact_sha256 the default is '', the
        # very value that disables the predicate. Verified live - a null filter returned 2
        # rows where the correct hash returned 1, so a send-gate retrieving an approval by
        # hash could be handed another artifact's verdict. Same fail-open as the empty
        # string, reached through a different type.
        if name in raw_params:
            val = raw_params[name]
            if val is None:
                return None, f"Parameter {name} must not be null"
        else:
            if required:
                return None, f"Missing required parameter: {name}"
            val = spec.get("default")

        # A filter value that is SUPPLIED must be well-formed. Absent stays optional;
        # supplied must match, and neither empty nor null counts as absent.
        pattern = spec.get("pattern")
        if pattern is not None and name in raw_params:
            if not isinstance(val, str) or not re.fullmatch(pattern, val):
                return None, f"Parameter {name} must match {pattern}"

        ptype = spec.get("type", "str")
        if ptype == "int":
            try:
                val = int(val)
            except (TypeError, ValueError):
                return None, f"Parameter {name} must be an integer"
            max_val = spec.get("max")
            if max_val is not None and val > max_val:
                val = max_val
        elif ptype == "interval":
            # Interval params are passed as strings like "24 hours"
            if not isinstance(val, str):
                val = str(val)
        elif ptype == "str":
            if not isinstance(val, str):
                val = str(val)

        bound[name] = val
    return bound, None


def ensure_views():
    """Create or replace KPI views that aggregate from telemetry_events."""
    conn = None
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Drop first because CREATE OR REPLACE VIEW cannot change column types.
        # The original views used ts (timestamptz) for day; current SQL casts to date.
        cur.execute("DROP VIEW IF EXISTS kpi_health CASCADE")
        cur.execute("DROP VIEW IF EXISTS kpi_costs CASCADE")

        # kpi_health: daily aggregate of health_check events from soak-monitor.
        # Columns: day, checks_total, checks_passed, checks_failed, services_checked, crashes
        # W3 Health Dashboard reads checks_failed and crashes from this view.
        cur.execute("""
            CREATE VIEW kpi_health AS
            SELECT
                ts::date AS day,
                COUNT(*) AS checks_total,
                COUNT(*) FILTER (
                    WHERE (payload->>'checked')::int = jsonb_array_length(payload->'healthy')
                ) AS checks_passed,
                COUNT(*) FILTER (
                    WHERE (payload->>'checked')::int > jsonb_array_length(payload->'healthy')
                ) AS checks_failed,
                MAX((payload->>'checked')::int) AS services_checked,
                COALESCE(crash.crash_count, 0) AS crashes
            FROM telemetry_events te
            LEFT JOIN LATERAL (
                SELECT COUNT(*) AS crash_count
                FROM telemetry_events c
                WHERE c.event_type = 'service_crash'
                  AND c.ts::date = te.ts::date
            ) crash ON true
            WHERE te.event_type = 'health_check'
              AND te.service = 'soak-monitor'
            GROUP BY ts::date, crash.crash_count
            ORDER BY day DESC
        """)

        # kpi_costs: daily aggregate of cost-related events.
        # Tracks LLM requests, billing errors, and service-level spend signals.
        # CFO agent and W13 Cost Tracker read from this view.
        cur.execute("""
            CREATE VIEW kpi_costs AS
            SELECT
                ts::date AS day,
                service,
                COUNT(*) AS total_events,
                COUNT(*) FILTER (
                    WHERE event_type LIKE '%%error%%'
                       OR event_type LIKE '%%billing%%'
                       OR event_type = 'budget_alert'
                ) AS error_events,
                COUNT(*) FILTER (
                    WHERE event_type IN ('llm_request', 'model_request', 'heartbeat_summary')
                ) AS llm_events,
                COUNT(*) FILTER (
                    WHERE event_type IN ('bundle_created', 'sheetguard_review', 'finance_review')
                ) AS governance_events,
                COALESCE(
                    SUM((payload->>'cost_usd')::numeric),
                    0
                ) AS total_cost_usd
            FROM telemetry_events
            WHERE ts > NOW() - INTERVAL '90 days'
            GROUP BY ts::date, service
            ORDER BY day DESC, service
        """)

        conn.commit()
        cur.close()
        logger.info("kpi_health + kpi_costs views created/replaced")
    except Exception as exc:
        logger.error(f"ensure_views failed: {exc}")
    finally:
        if conn:
            safe_put_conn(conn)


class Handler(BaseHTTPRequestHandler):

    # ---- Auth helper ----

    def _check_service_token(self):
        """Check X-Service-Token header. Returns True if authorized."""
        if not SERVICE_TOKEN:
            # Migration mode: no token configured, allow with warning
            return True
        token = self.headers.get("X-Service-Token", "").strip()
        if not token:
            token = self.headers.get("X-API-Key", "").strip()
        if not token:
            auth = self.headers.get("Authorization", "").strip()
            if auth.lower().startswith("bearer "):
                token = auth[7:].strip()
        if token and secrets.compare_digest(token, SERVICE_TOKEN):
            return True
        self._json(401, {
            "error": "Unauthorized. Provide X-Service-Token, X-API-Key, or Authorization: Bearer <token>.",
        })
        return False

    # ---- GET routes ----

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/health":
            healthy = True
            db_status = "ok"
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
            except Exception:
                healthy = False
                db_status = "unreachable"
            finally:
                if conn:
                    safe_put_conn(conn)
            code = 200 if healthy else 503
            self._json(code, {
                "status": "ok" if healthy else "degraded",
                "db": db_status,
                "routes": [
                    "POST /telemetry", "POST /query", "POST /sync",
                    "POST /champion", "GET /queries",
                    "GET /kpi/{view}", "GET /champion/leaderboard",
                ],
            })
            return

        # GET /queries -- list available named queries
        if path == "/queries":
            if not self._check_service_token():
                return
            catalog = {}
            for name, defn in QUERY_REGISTRY.items():
                catalog[name] = {
                    "params": {
                        k: {pk: pv for pk, pv in v.items() if pk != "default"}
                        for k, v in defn["params"].items()
                    } if defn["params"] else {},
                }
            self._json(200, {"queries": catalog})
            return

        # GET /kpi/{view_name}?limit=10&weeks=4
        if path.startswith("/kpi/"):
            if not self._check_service_token():
                return
            view_name = path.split("/kpi/")[1]
            if view_name not in ALLOWED_VIEWS:
                self._json(400, {"error": f"Unknown view: {view_name}", "allowed": sorted(ALLOWED_VIEWS)})
                return

            params = parse_qs(parsed.query)
            limit = min(int(params.get("limit", ["20"])[0]), 100)
            weeks = min(int(params.get("weeks", ["4"])[0]), 52)

            query = f"SELECT * FROM {view_name}"
            query_params = []
            if "week" in view_name or view_name == "kpi_health":
                time_col = "day" if view_name == "kpi_health" else "week"
                query += f" WHERE {time_col} >= NOW() - INTERVAL %s"
                query_params.append(f"{weeks} weeks")
                query += f" ORDER BY {time_col} DESC"
            query += " LIMIT %s"
            query_params.append(limit)

            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query, query_params)
                rows = [serialize_row(r) for r in cur.fetchall()]
                cur.close()
                self._json(200, {"view": view_name, "rows": rows, "count": len(rows)})
            except Exception:
                req_id = uuid.uuid4().hex[:12]
                logger.error(f"KPI error req={req_id} view={view_name}")
                self._json(500, {"error": "Query failed", "request_id": req_id})
            finally:
                if conn:
                    safe_put_conn(conn)
            return

        # GET /champion/leaderboard
        if path == "/champion/leaderboard":
            if not self._check_service_token():
                return
            conn = None
            try:
                conn = get_conn()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("SELECT * FROM champion_leaderboard")
                rows = [serialize_row(r) for r in cur.fetchall()]
                cur.close()
                self._json(200, {"leaderboard": rows, "count": len(rows)})
            except Exception:
                req_id = uuid.uuid4().hex[:12]
                logger.error(f"champion leaderboard error req={req_id}")
                self._json(500, {"error": "Query failed", "request_id": req_id})
            finally:
                if conn:
                    safe_put_conn(conn)
            return

        self._json(404, {"error": "not found"})

    # ---- POST routes ----

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "/telemetry":
            if not self._check_service_token():
                return
            self._handle_telemetry()
            return

        if path == "/query":
            if not self._check_service_token():
                return
            self._handle_query()
            return

        if path == "/champion":
            if not self._check_service_token():
                return
            self._handle_champion()
            return

        if path == "/sync":
            if not self._check_service_token():
                return
            self._handle_sync()
            return

        self._json(404, {"error": "not found"})

    def _read_json_body(self):
        """Read and parse JSON body. Returns (body_dict, None) or (None, sent_error)."""
        raw_length = self.headers.get("Content-Length")
        if raw_length is None:
            self._json(400, {"error": "Content-Length header required"})
            return None, True

        length = int(raw_length)
        if length == 0 or length > 65536:
            self._json(400, {"error": "Body required (max 64KB)"})
            return None, True

        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Invalid JSON"})
            return None, True

        if not isinstance(body, dict):
            self._json(400, {"error": "Body must be a JSON object"})
            return None, True

        return body, None

    def _handle_champion(self):
        """Insert a champion score event."""
        body, err = self._read_json_body()
        if err:
            return

        github_user = (body.get("github_user") or "").strip()
        event_type = (body.get("event_type") or "").strip()
        if not github_user or not event_type:
            self._json(400, {"error": "Missing required fields: github_user, event_type"})
            return

        if event_type not in CHAMPION_EVENT_POINTS:
            self._json(400, {
                "error": f"Invalid event_type: {event_type}",
                "allowed": list(CHAMPION_EVENT_POINTS.keys()),
            })
            return

        org_name = (body.get("org_name") or "").strip() or None
        points = CHAMPION_EVENT_POINTS[event_type]

        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                "INSERT INTO champion_scores (github_user, org_name, event_type, points) "
                "VALUES (%s, %s, %s, %s) RETURNING id, created_at",
                (github_user, org_name, event_type, points),
            )
            row = cur.fetchone()
            conn.commit()
            cur.close()
            self._json(201, {
                "status": "created",
                "id": row["id"],
                "github_user": github_user,
                "event_type": event_type,
                "points": points,
                "created_at": row["created_at"].isoformat(),
            })
        except Exception:
            req_id = uuid.uuid4().hex[:12]
            logger.error(f"champion INSERT error req={req_id} user={github_user}")
            self._json(500, {"error": "Insert failed", "request_id": req_id})
        finally:
            if conn:
                safe_put_conn(conn)

    def _handle_telemetry(self):
        """Insert a telemetry event.

        Accepts both Content-Type: application/json bodies AND minimal
        bodies from error-handler nodes that may omit some fields.
        """
        raw_length = self.headers.get("Content-Length")

        # STRICT INGEST (plan v4 C1 / F7). The old behaviour accepted an empty body as a
        # "ping" returning 201 with id=None, and filled missing fields with
        # "unknown"/"untyped". A row that records an event nobody can attribute is not
        # evidence, and a 201 for a write that never happened is a lie told to the caller.
        # Checked against five months of live data before tightening: across 1,680 events
        # in the last 7 days the four live producers sent zero malformed rows, and the only
        # row in 30 days relying on the defaults was this gate's own negative probe.
        # A malformed or negative Content-Length must be a controlled 400, not an
        # unhandled ValueError inside a single-process HTTPServer.
        try:
            length = int(raw_length) if raw_length is not None else 0
        except (TypeError, ValueError):
            self._json(400, {"error": "Invalid Content-Length"})
            return
        if length <= 0:
            self._json(400, {"error": "Body required"})
            return
        if length > 65536:
            self._json(400, {"error": "Body too large (max 64KB)"})
            return

        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"error": "Invalid JSON"})
            return

        if not isinstance(body, dict):
            self._json(400, {"error": "Body must be a JSON object"})
            return

        # These must be STRINGS. {"service": 1} used to reach .strip() and raise, which
        # the single-process server turned into a dropped connection (502 at the edge)
        # instead of the documented 400.
        raw_service = body.get("service")
        raw_event = body.get("event_type")
        if raw_service is not None and not isinstance(raw_service, str):
            self._json(400, {"error": "service must be a string"})
            return
        if raw_event is not None and not isinstance(raw_event, str):
            self._json(400, {"error": "event_type must be a string"})
            return

        service = (raw_service or "").strip()
        event_type = (raw_event or "").strip()

        if not service or not event_type:
            self._json(400, {"error": "service and event_type are required"})
            return

        # Pattern-checked so a producer identity stays a stable key rather than free text.
        if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", service) or \
           not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", event_type):
            self._json(400, {"error": "service/event_type fail pattern check"})
            return

        payload = body.get("payload", {})
        if not isinstance(payload, dict):
            # Was coerced to {"raw": payload}. Coercion hides a caller's bug and produces
            # rows whose shape nothing downstream can rely on. Refuse instead.
            self._json(400, {"error": "payload must be a JSON object"})
            return

        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(
                "INSERT INTO telemetry_events (service, event_type, payload) "
                "VALUES (%s, %s, %s::jsonb) RETURNING id, ts",
                (service, event_type, json.dumps(payload)),
            )
            row = cur.fetchone()
            conn.commit()
            cur.close()
            self._json(201, {"status": "created", "id": row["id"], "ts": row["ts"].isoformat()})
        except Exception:
            req_id = uuid.uuid4().hex[:12]
            logger.error(f"INSERT error req={req_id} service={service}")
            self._json(500, {"error": "Insert failed", "request_id": req_id})
        finally:
            if conn:
                safe_put_conn(conn)

    def _handle_query(self):
        """Execute a named query from the registry and return JSON rows."""
        body, err = self._read_json_body()
        if err:
            return

        # Backwards compat: reject raw SQL with helpful message
        if "sql" in body:
            self._json(400, {
                "error": "Raw SQL is disabled. Use query_name. GET /queries for available queries.",
            })
            return

        query_name = (body.get("query_name") or "").strip()
        if not query_name:
            self._json(400, {"error": "Missing required field: query_name"})
            return

        if query_name not in QUERY_REGISTRY:
            self._json(400, {
                "error": f"Unknown query_name: {query_name}",
                "available": sorted(QUERY_REGISTRY.keys()),
            })
            return

        query_def = QUERY_REGISTRY[query_name]
        raw_params = body.get("params", {})
        if not isinstance(raw_params, dict):
            self._json(400, {"error": "params must be a JSON object"})
            return

        bound, param_err = bind_params(query_def, raw_params)
        if param_err:
            self._json(400, {"error": param_err})
            return

        conn = None
        try:
            conn = get_conn()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(query_def["sql"], bound)
            rows = [serialize_row(r) for r in cur.fetchall()]
            cur.close()
            self._json(200, {"query": query_name, "rows": rows, "count": len(rows)})
        except Exception as exc:
            req_id = uuid.uuid4().hex[:12]
            logger.error(f"QUERY error req={req_id} query={query_name} err={exc}")
            self._json(500, {"error": "Query failed", "request_id": req_id})
        finally:
            if conn:
                safe_put_conn(conn)

    def _handle_sync(self):
        """Run the Paperclip data sync (INSERT from heartbeat_runs + activity_log, prune old)."""
        conn = None
        try:
            conn = get_conn()
            conn.autocommit = True
            cur = conn.cursor()

            # Sync heartbeat_runs -> telemetry_events
            cur.execute("""
                INSERT INTO telemetry_events (ts, service, event_type, payload)
                SELECT hr.created_at, 'paperclip',
                  CASE hr.status
                    WHEN 'completed' THEN 'heartbeat_succeeded'
                    WHEN 'failed' THEN 'heartbeat_failed'
                    WHEN 'timed_out' THEN 'heartbeat_timed_out'
                    ELSE 'heartbeat_' || COALESCE(hr.status, 'unknown')
                  END,
                  jsonb_build_object(
                    'agent_id', hr.agent_id::text,
                    'agent_name', a.name,
                    'run_id', hr.id::text,
                    'status', hr.status,
                    'error', hr.error
                  )
                FROM heartbeat_runs hr LEFT JOIN agents a ON hr.agent_id = a.id
                WHERE hr.created_at > COALESCE(
                  (SELECT MAX(ts) FROM telemetry_events WHERE service = 'paperclip'),
                  '2020-01-01'::timestamptz)
                ORDER BY hr.created_at
            """)
            hb_synced = cur.rowcount

            # Sync activity_log -> telemetry_events
            cur.execute("""
                INSERT INTO telemetry_events (ts, service, event_type, payload)
                SELECT al.created_at, 'paperclip', 'activity_' || al.action,
                  jsonb_build_object(
                    'actor_type', al.actor_type,
                    'entity_type', al.entity_type,
                    'entity_id', al.entity_id,
                    'agent_id', al.agent_id::text
                  )
                FROM activity_log al
                WHERE al.created_at > COALESCE(
                  (SELECT MAX(ts) FROM telemetry_events WHERE service = 'paperclip' AND event_type LIKE 'activity_%'),
                  '2020-01-01'::timestamptz)
                ORDER BY al.created_at
            """)
            act_synced = cur.rowcount

            # Prune old events
            cur.execute("DELETE FROM telemetry_events WHERE ts < NOW() - INTERVAL '90 days'")
            pruned = cur.rowcount

            cur.close()

            self._json(200, {
                "status": "synced",
                "heartbeats_synced": hb_synced,
                "activities_synced": act_synced,
                "pruned": pruned,
            })
        except Exception:
            req_id = uuid.uuid4().hex[:12]
            logger.error(f"SYNC error req={req_id}")
            self._json(500, {"error": "Sync failed", "request_id": req_id})
        finally:
            if conn:
                conn.autocommit = False
                safe_put_conn(conn)

    # ---- Helpers ----

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data, default=str).encode())

    def log_message(self, fmt, *args):
        logger.info(f"{self.command} {self.path} {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    ensure_views()
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    logger.info(f"listening on 0.0.0.0:{PORT}")
    logger.info(
        "routes: POST /telemetry, POST /query, POST /sync, POST /champion, "
        "GET /queries, GET /kpi/{view}, GET /champion/leaderboard"
    )
    server.serve_forever()
