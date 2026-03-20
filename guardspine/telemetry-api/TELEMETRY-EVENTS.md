# Telemetry Event Catalog

POST http://telemetry-api.railway.internal:8090/telemetry
Content-Type: application/json

All events follow: { "service": "...", "event_type": "...", "payload": {...} }

## Outreach events (service: "outreach")

| event_type        | When                             | payload fields                                                                 |
| ----------------- | -------------------------------- | ------------------------------------------------------------------------------ |
| outreach_draft    | CMO posts draft as issue comment | prospect_name, company, pain_bucket, channel, word_count, slop_pass, swap_pass |
| outreach_sent     | David manually sends message     | prospect_name, company, channel, issue_id                                      |
| outreach_response | Prospect replies                 | prospect_name, company, sentiment (positive/neutral/negative), qualified       |
| outreach_negative | Negative/spam response           | prospect_name, company, reason                                                 |
| outreach_override | David rejects/edits CMO draft    | issue_id, reason, original_pain_bucket                                         |

## Content events (service: "content")

| event_type         | When                         | payload fields                                      |
| ------------------ | ---------------------------- | --------------------------------------------------- |
| content_draft      | Content Director posts draft | content_type, account, topic, word_count, slop_pass |
| content_published  | David publishes to LinkedIn  | content_type, account, post_url                     |
| content_rejected   | David rejects draft          | issue_id, reason                                    |
| content_engagement | Engagement data collected    | post_url, impressions, comments, likes, shares      |

## Automation events (service: "paperclip" or "openclaw")

Auto-synced from Paperclip heartbeat_runs and activity_log tables.

| event_type          | When                      | payload fields                         |
| ------------------- | ------------------------- | -------------------------------------- |
| heartbeat_succeeded | Agent heartbeat completes | agent_id, agent_name, duration_ms      |
| heartbeat_failed    | Agent heartbeat fails     | agent_id, agent_name, error, exit_code |
| heartbeat_timed_out | Agent heartbeat times out | agent_id, agent_name                   |
| activity\_\*        | Any Paperclip activity    | actor_type, entity_type, details       |

## Governance events (service: "guardspine")

| event_type       | When                             | payload fields                                                                            |
| ---------------- | -------------------------------- | ----------------------------------------------------------------------------------------- |
| council_decision | GuardSpine council votes         | decision (approve/block/conditions), risk_tier, agreement_score, duration_ms, models_used |
| policy_violation | Agent violates governance policy | tool_name, risk_tier, violation_type, agent                                               |

## Funnel events (service: "funnel")

| event_type         | When                             | payload fields                       |
| ------------------ | -------------------------------- | ------------------------------------ |
| funnel_impression  | LinkedIn post published          | post_url, account, content_type      |
| funnel_engagement  | Comment/lead magnet request      | post_url, user_name, engagement_type |
| funnel_opt_in      | Email captured                   | source, email_hash (never raw email) |
| funnel_activation  | Lead magnet consumed (>30s view) | lead_magnet_id, source               |
| funnel_advancement | CTA clicked (cal.com booking)    | source, cta_type                     |
| funnel_conversion  | Meeting booked / deal created    | source, deal_value                   |
| funnel_referral    | Customer/partner shares          | referrer, channel                    |

## Infrastructure events (service: "soak-monitor" or "infrastructure")

| event_type      | When              | payload fields                       |
| --------------- | ----------------- | ------------------------------------ |
| health_check    | Soak-monitor runs | checked, healthy, unhealthy, details |
| service_crash   | Service crashes   | service_name, error                  |
| service_restart | Service restarts  | service_name, reason                 |
