-- SPOF Hardening: Postgres indexes and retention
-- Generated: 2026-03-31
-- Apply with: psql $DATABASE_URL < postgres-hardening.sql
-- 
-- NOTE: CREATE INDEX CONCURRENTLY cannot run inside a transaction.
-- Indexes are created in a separate transaction first, then deletions + VACUUM
-- run together in a second transaction for consistency.

-- ============================================================
-- PHASE 1: Create indexes (outside transaction, CONCURRENTLY)
-- ============================================================

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telemetry_service_ts
  ON telemetry_events(service, ts DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telemetry_event_type_ts
  ON telemetry_events(event_type, ts DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_telemetry_ts
  ON telemetry_events(ts DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_heartbeat_runs_agent_status
  ON heartbeat_runs(agent_id, status, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_decision_journal_domain_type
  ON decision_journal(domain, decision_type);

-- ============================================================
-- PHASE 2: Retention deletions and VACUUM (in transaction)
-- ============================================================
-- This ensures either all deletions succeed or all roll back (consistency).
-- VACUUM inside transaction minimizes table bloat window.

BEGIN;

-- activity_log: keep 90 days
DELETE FROM activity_log
WHERE timestamp < NOW() - INTERVAL '90 days';

-- heartbeat_runs: keep 90 days
DELETE FROM heartbeat_runs
WHERE created_at < NOW() - INTERVAL '90 days';

-- issue_comments: keep 180 days
DELETE FROM issue_comments
WHERE created_at < NOW() - INTERVAL '180 days';

-- telemetry_events: keep 90 days (already in telemetry-api /sync,
-- but belt-and-suspenders here)
DELETE FROM telemetry_events
WHERE ts < NOW() - INTERVAL '90 days';

-- VACUUM inside transaction to reclaim space immediately
VACUUM ANALYZE activity_log;
VACUUM ANALYZE heartbeat_runs;
VACUUM ANALYZE issue_comments;
VACUUM ANALYZE telemetry_events;

COMMIT;
