"""Telemetry event collector. Accepts POST /telemetry, inserts into Postgres."""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

import psycopg2
from psycopg2.extras import RealDictCursor

DB_URL = os.environ["DATABASE_URL"]
PORT = int(os.environ.get("PORT", "8090"))


def get_conn():
    return psycopg2.connect(DB_URL)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/telemetry":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        if length == 0 or length > 65536:
            self._error(400, "Body required (max 64KB)")
            return

        try:
            body = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._error(400, "Invalid JSON")
            return

        service = body.get("service", "").strip()
        event_type = body.get("event_type", "").strip()
        if not service or not event_type:
            self._error(400, "Missing required fields: service, event_type")
            return

        payload = body.get("payload", {})
        if not isinstance(payload, dict):
            self._error(400, "payload must be a JSON object")
            return

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
            conn.close()

            self.send_response(201)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "created",
                "id": row["id"],
                "ts": row["ts"].isoformat(),
            }).encode())

        except Exception as e:
            self._error(500, str(e))

    def _error(self, code, msg):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "error", "message": msg}).encode())

    def log_message(self, fmt, *args):
        # Structured one-liner instead of default Apache format
        print(f"[telemetry] {self.command} {self.path} {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[telemetry] listening on 0.0.0.0:{PORT}")
    server.serve_forever()
