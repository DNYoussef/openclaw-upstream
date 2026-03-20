-- Outreach CRM schema
-- Data lives in Railway volume, not in git or Docker image.
-- This file is CODE (schema definition). Data is populated at runtime.

CREATE TABLE IF NOT EXISTS prospects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    title TEXT,
    company TEXT,
    industry TEXT,
    persona TEXT,
    linkedin_url TEXT,
    email TEXT,
    notes TEXT,
    source TEXT,
    created_at TEXT,
    artifact_sent TEXT,
    message_sent_at TEXT,
    response_received INTEGER DEFAULT 0,
    signal_type TEXT DEFAULT 'none',
    signal_notes TEXT,
    lane TEXT DEFAULT 'buyer',
    archetype TEXT,
    investor_score INTEGER,
    investor_tier TEXT,
    capacity_band TEXT,
    intro_paths TEXT,
    next_action TEXT,
    campaign TEXT,
    target_segment TEXT,
    landing_url TEXT,
    hook_text TEXT,
    company_context TEXT,
    message_draft TEXT,
    batch_number INTEGER,
    channel TEXT,
    utm_content TEXT,
    page_visited_at TEXT,
    signup_completed INTEGER DEFAULT 0,
    research_notes TEXT,
    consent_basis TEXT DEFAULT 'legitimate_interest',
    consent_recorded_at TEXT,
    suppressed INTEGER DEFAULT 0,
    suppression_reason TEXT,
    do_not_contact INTEGER DEFAULT 0,
    followup_count INTEGER DEFAULT 0,
    last_followup_at TEXT
);

-- Suppression list: prospects who opted out or said no
CREATE TABLE IF NOT EXISTS suppression_list (
    email TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    added_at TEXT DEFAULT (datetime('now')),
    source TEXT
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    action TEXT,
    prospect_id TEXT,
    details TEXT
);

CREATE TABLE IF NOT EXISTS narrowcast_scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    scan_date TEXT NOT NULL,
    tier TEXT NOT NULL,
    platform TEXT NOT NULL,
    channel_name TEXT,
    query TEXT,
    threads_found INTEGER DEFAULT 0,
    threads_relevant INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS narrowcast_threads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    pain_signal TEXT,
    profiles_json TEXT,
    discovered_at TEXT,
    engaged_at TEXT,
    comment_text TEXT,
    outcome TEXT,
    prospects_sourced INTEGER DEFAULT 0,
    notes TEXT
);

CREATE TABLE IF NOT EXISTS weekly_metrics (
    week_start TEXT PRIMARY KEY,
    messages_sent INTEGER DEFAULT 0,
    companies_json TEXT,
    artifacts_json TEXT,
    responses_received INTEGER DEFAULT 0,
    green_signals INTEGER DEFAULT 0,
    yellow_signals INTEGER DEFAULT 0,
    red_signals INTEGER DEFAULT 0
);

-- Indexes for pipeline query performance
CREATE INDEX IF NOT EXISTS idx_prospects_signal_type ON prospects(signal_type);
CREATE INDEX IF NOT EXISTS idx_prospects_message_sent_at ON prospects(message_sent_at);
CREATE INDEX IF NOT EXISTS idx_prospects_lane ON prospects(lane);
CREATE INDEX IF NOT EXISTS idx_prospects_company ON prospects(company);
CREATE INDEX IF NOT EXISTS idx_prospects_persona ON prospects(persona);
CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_narrowcast_scans_date ON narrowcast_scans(scan_date);
CREATE INDEX IF NOT EXISTS idx_narrowcast_platform ON narrowcast_threads(platform);
