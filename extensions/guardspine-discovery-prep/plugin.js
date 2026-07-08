/**
 * GuardSpine Discovery Prep Plugin
 *
 * Provides the discovery_prep tool for composing pre-call handoff sheets.
 * Queries outreach.db (SQLite) for prospect data and discovery_tree.json
 * for matching openers, pitch variants, and objection bridges.
 *
 * Also exposes outreach_query for ad-hoc prospect lookups.
 */

const fs = require("fs");
const path = require("path");

// ---------------------------------------------------------------
// PATH RESOLUTION
// ---------------------------------------------------------------

const HOME = process.env.USERPROFILE || process.env.HOME || ".";
const DEFAULT_OUTREACH_DIR = path.join(HOME, ".claude", "outreach");
const DEFAULT_DB_PATH = path.join(DEFAULT_OUTREACH_DIR, "outreach.db");
const DEFAULT_TREE_PATH = path.join(DEFAULT_OUTREACH_DIR, "discovery_tree.json");

function resolveDbPath(config) {
  const p = config && config.outreach_db_path;
  return p && p.length > 0 ? p : DEFAULT_DB_PATH;
}

function resolveTreePath(config) {
  const p = config && config.discovery_tree_path;
  return p && p.length > 0 ? p : DEFAULT_TREE_PATH;
}

// ---------------------------------------------------------------
// SQLITE HELPER (uses better-sqlite3 if available, else spawns)
// ---------------------------------------------------------------

let Database = null;
try {
  Database = require("better-sqlite3");
} catch (_) {
  // Will fall back to python subprocess
}

function queryDb(dbPath, sql, params) {
  if (Database) {
    const db = new Database(dbPath, { readonly: true });
    try {
      const rows = db.prepare(sql).all(...(params || []));
      return rows;
    } finally {
      db.close();
    }
  }

  // Fallback: use python to query sqlite
  const { execSync } = require("child_process");
  const pyCode = [
    "import sqlite3, json, sys",
    "conn = sqlite3.connect(sys.argv[1])",
    "conn.row_factory = sqlite3.Row",
    "cur = conn.cursor()",
    "cur.execute(sys.argv[2], json.loads(sys.argv[3]) if len(sys.argv) > 3 else [])",
    "rows = [dict(r) for r in cur.fetchall()]",
    "print(json.dumps(rows))",
    "conn.close()",
  ].join("\n");
  const tmpFile = path.join(require("os").tmpdir(), "openclaw_query_" + process.pid + ".py");
  fs.writeFileSync(tmpFile, pyCode, "utf-8");
  try {
    const result = execSync(
      `python "${tmpFile}" "${dbPath}" "${sql}" "${JSON.stringify(params || []).replace(/"/g, '\\"')}"`,
      {
        encoding: "utf-8",
        timeout: 10000,
      },
    );
    return JSON.parse(result.trim());
  } finally {
    try {
      fs.unlinkSync(tmpFile);
    } catch (_) {}
  }
}

function queryDbSafe(dbPath, sql, params) {
  try {
    return queryDb(dbPath, sql, params);
  } catch (e) {
    return { error: String(e.message || e) };
  }
}

// ---------------------------------------------------------------
// DISCOVERY TREE LOADER
// ---------------------------------------------------------------

let _cachedTree = null;
let _cachedTreePath = null;

function loadDiscoveryTree(treePath) {
  if (_cachedTree && _cachedTreePath === treePath) return _cachedTree;
  try {
    const raw = fs.readFileSync(treePath, "utf-8");
    _cachedTree = JSON.parse(raw);
    _cachedTreePath = treePath;
    return _cachedTree;
  } catch (e) {
    return null;
  }
}

// ---------------------------------------------------------------
// HANDOFF SHEET BUILDER
// ---------------------------------------------------------------

function buildHandoffSheet(prospect, tree, personaCard, objectionCards) {
  const sections = [];

  // Header
  sections.push("# Pre-Call Discovery Handoff Sheet");
  sections.push("");
  sections.push("## Prospect");
  sections.push("- Name: " + (prospect.name || "Unknown"));
  sections.push("- Title: " + (prospect.title || "N/A"));
  sections.push("- Company: " + (prospect.company || "N/A"));
  sections.push("- Industry: " + (prospect.industry || "N/A"));
  sections.push("- Lane: " + (prospect.lane || "buyer"));
  sections.push("- Funnel Stage: " + (prospect.funnel_stage || "research"));
  sections.push("- Channel: " + (prospect.channel || "N/A"));
  if (prospect.email) sections.push("- Email: " + prospect.email);
  if (prospect.linkedin_url) sections.push("- LinkedIn: " + prospect.linkedin_url);

  // Signal data
  sections.push("");
  sections.push("## Signals");
  sections.push("- Signal Type: " + (prospect.signal_type || "none"));
  if (prospect.signal_notes) sections.push("- Signal Notes: " + prospect.signal_notes);
  if (prospect.ai_adoption_signal)
    sections.push("- AI Adoption Signal: " + prospect.ai_adoption_signal);
  if (prospect.governance_signal)
    sections.push("- Governance Signal: " + prospect.governance_signal);
  if (prospect.research_confidence)
    sections.push("- Research Confidence: " + prospect.research_confidence);

  // Pain data
  sections.push("");
  sections.push("## Pain Analysis");
  sections.push("- Pain Bucket: " + (prospect.pain_bucket || "not identified"));
  if (prospect.pain_bucket_confirmed)
    sections.push("- Pain Confirmed: " + prospect.pain_bucket_confirmed);
  if (prospect.struggling_moment_hypothesis)
    sections.push("- Struggling Moment Hypothesis: " + prospect.struggling_moment_hypothesis);
  if (prospect.struggling_moment_actual)
    sections.push("- Struggling Moment Actual: " + prospect.struggling_moment_actual);
  if (prospect.hook_angle) sections.push("- Hook Angle: " + prospect.hook_angle);

  // Objection intelligence
  if (prospect.objection_primary || prospect.objection_force) {
    sections.push("");
    sections.push("## Objection Intelligence");
    if (prospect.objection_primary)
      sections.push("- Primary Objection: " + prospect.objection_primary);
    if (prospect.objection_force) sections.push("- Objection Force: " + prospect.objection_force);
  }

  // Partnership / pilot state
  if (prospect.partnership_scope || prospect.pilot_scope) {
    sections.push("");
    sections.push("## Partnership / Pilot");
    if (prospect.partnership_scope)
      sections.push("- Partnership Scope: " + prospect.partnership_scope);
    if (prospect.pilot_scope) sections.push("- Pilot Scope: " + prospect.pilot_scope);
    if (prospect.pilot_repo) sections.push("- Pilot Repo: " + prospect.pilot_repo);
    if (prospect.sean_ellis_score)
      sections.push("- Sean Ellis Score: " + prospect.sean_ellis_score);
    if (prospect.champion_strength)
      sections.push("- Champion Strength: " + prospect.champion_strength);
  }

  // Discovery tree guidance
  if (tree) {
    sections.push("");
    sections.push("## Discovery Playbook");

    // Step 1: Opening questions
    if (tree.step_1_open && tree.step_1_open.questions) {
      sections.push("");
      sections.push("### Opening Questions");
      tree.step_1_open.questions.forEach(function (q) {
        sections.push("- " + q);
      });
    }

    // Match pain bucket to discovery tree patterns
    const painBucket = prospect.pain_bucket || "";
    if (tree.step_3_identify_dominant_pain && tree.step_3_identify_dominant_pain.patterns) {
      const matchedPattern = tree.step_3_identify_dominant_pain.patterns.find(function (p) {
        return (
          painBucket.toLowerCase().includes(p.pattern.replace(/_/g, " ")) ||
          p.pattern.includes(painBucket.replace(/ /g, "_").toLowerCase())
        );
      });
      if (matchedPattern) {
        sections.push("");
        sections.push("### Matched Pain Pattern: " + matchedPattern.pattern);
        sections.push("- Recap Line: " + matchedPattern.recap);
        sections.push("- Listen for: " + matchedPattern.they_say.join(" | "));
      }
    }

    // Quantification questions matched to pain bucket
    if (tree.step_4_quantify_cost && tree.step_4_quantify_cost.branches) {
      // Map pain buckets to branch keys
      const branchMap = {
        review_velocity_gap: "review_overload",
        review_overload: "review_overload",
        evidence_chain_gap: "evidence_scramble",
        evidence_scramble: "evidence_scramble",
        weak_approval_trail: "weak_approval_trail",
        authorization_provenance_gap: "weak_approval_trail",
        semantic_governance_gap: "weak_approval_trail",
        regulatory_readiness_gap: "regulatory_pressure",
        regulatory_pressure: "regulatory_pressure",
      };
      const branchKey = branchMap[painBucket] || branchMap[painBucket.replace(/ /g, "_")];
      const questions = branchKey && tree.step_4_quantify_cost.branches[branchKey];
      if (questions) {
        sections.push("");
        sections.push("### Cost Quantification Questions");
        questions.forEach(function (q) {
          sections.push("- " + q);
        });
      }
    }

    // Pitch variant selection
    if (tree.pitch_variants) {
      const persona = (prospect.persona || prospect.archetype || "").toLowerCase();
      const lane = (prospect.lane || "buyer").toLowerCase();
      // Try persona-specific pitch, then lane-mapped, then core
      const variantKey = persona || (lane === "investor" ? "startup_ceo" : "core");
      const pitch = tree.pitch_variants[variantKey] || tree.pitch_variants.core;
      sections.push("");
      sections.push("### Recommended Pitch Variant (" + variantKey + ")");
      sections.push(pitch);
    }

    // Transition line
    if (tree.step_5_transition_to_pitch) {
      sections.push("");
      sections.push("### Transition Line");
      sections.push(tree.step_5_transition_to_pitch.standard);
    }

    // Relevant one-liners
    if (tree.one_liner_arsenal) {
      sections.push("");
      sections.push("### One-Liner Arsenal (select relevant)");
      Object.entries(tree.one_liner_arsenal).forEach(function (entry) {
        sections.push('- "' + entry[0] + '" -> ' + entry[1]);
      });
    }
  }

  // Persona card from DB
  if (personaCard) {
    sections.push("");
    sections.push("## Persona Card: " + (personaCard.persona || ""));
    sections.push("- Functional Job: " + (personaCard.functional_job || ""));
    sections.push("- Social Job: " + (personaCard.social_job || ""));
    sections.push("- Emotional Job: " + (personaCard.emotional_job || ""));
    sections.push("- Push: " + (personaCard.push || ""));
    sections.push("- Pull: " + (personaCard.pull || ""));
    sections.push("- Anxieties: " + (personaCard.anxieties || ""));
    sections.push("- Discovery Opener: " + (personaCard.discovery_opener || ""));
    sections.push("- Pitch Variant: " + (personaCard.pitch_variant || ""));
    sections.push("- Urgency Lever: " + (personaCard.urgency_lever || ""));
    sections.push("- Best Next Step: " + (personaCard.best_next_step || ""));
  }

  // Objection cards from DB
  if (objectionCards && objectionCards.length > 0) {
    sections.push("");
    sections.push("## Objection Bridges");
    objectionCards.forEach(function (card) {
      sections.push("");
      sections.push('### "' + card.trigger_phrase + '" (' + card.force_type + ")");
      sections.push("- Response: " + card.verbal_response);
      sections.push("- Story: " + card.story);
      sections.push("- Bridge: " + card.bridge_line);
      if (card.counter_question) sections.push("- Counter Question: " + card.counter_question);
    });
  }

  // Research notes
  if (prospect.research_notes || prospect.company_context) {
    sections.push("");
    sections.push("## Research Notes");
    if (prospect.company_context) sections.push(prospect.company_context);
    if (prospect.research_notes) sections.push(prospect.research_notes);
  }

  // Response history
  if (prospect.response_snippet || prospect.last_response_at) {
    sections.push("");
    sections.push("## Response History");
    if (prospect.last_response_at) sections.push("- Last Response: " + prospect.last_response_at);
    if (prospect.response_snippet) sections.push("- Snippet: " + prospect.response_snippet);
    sections.push("- Follow-up Count: " + (prospect.follow_up_count || 0));
  }

  return sections.join("\n");
}

// ---------------------------------------------------------------
// PLUGIN ENTRY POINT
// ---------------------------------------------------------------

function register(api) {
  const config = api.pluginConfig || {};
  const dbPath = resolveDbPath(config);
  const treePath = resolveTreePath(config);

  // =============================================
  // TOOL: discovery_prep
  // =============================================
  api.registerTool(
    function () {
      return {
        name: "discovery_prep",
        description:
          "Compose a pre-call discovery handoff sheet for a prospect. " +
          "Accepts prospect_id or email. Queries outreach.db for prospect data " +
          "(lane, pain_bucket, funnel_stage, signals) and discovery_tree.json " +
          "for matching openers, pitch variants, and objection bridges. " +
          "Returns a formatted markdown handoff sheet ready for a sales call.",
        parameters: {
          type: "object",
          properties: {
            prospect_id: {
              type: "string",
              description: "Prospect ID from outreach.db",
            },
            email: {
              type: "string",
              description: "Prospect email address (used if prospect_id not provided)",
            },
          },
        },
        execute: function (params) {
          if (!fs.existsSync(dbPath)) {
            return { error: "outreach.db not found at: " + dbPath };
          }

          // Build query
          var sql, sqlParams;
          if (params.prospect_id) {
            sql = "SELECT * FROM prospects WHERE id = ? LIMIT 1";
            sqlParams = [params.prospect_id];
          } else if (params.email) {
            sql = "SELECT * FROM prospects WHERE email = ? LIMIT 1";
            sqlParams = [params.email];
          } else {
            return { error: "Provide prospect_id or email" };
          }

          var rows = queryDbSafe(dbPath, sql, sqlParams);
          if (rows.error) return { error: rows.error };
          if (!rows || rows.length === 0) return { error: "Prospect not found" };

          var prospect = rows[0];

          // Load discovery tree
          var tree = loadDiscoveryTree(treePath);

          // Load persona card if persona/archetype matches
          var personaCard = null;
          var persona = prospect.persona || prospect.archetype || "";
          if (persona) {
            var personaRows = queryDbSafe(
              dbPath,
              "SELECT * FROM persona_cards WHERE LOWER(persona) = ? LIMIT 1",
              [persona.toLowerCase()],
            );
            if (personaRows && !personaRows.error && personaRows.length > 0) {
              personaCard = personaRows[0];
            }
          }

          // Load matching objection cards
          var objectionCards = [];
          if (prospect.objection_primary) {
            var objRows = queryDbSafe(
              dbPath,
              "SELECT * FROM objection_cards WHERE LOWER(trigger_phrase) LIKE ? LIMIT 5",
              ["%" + prospect.objection_primary.toLowerCase().substring(0, 50) + "%"],
            );
            if (objRows && !objRows.error) objectionCards = objRows;
          }
          // Also load by force type if we have objection_force
          if (prospect.objection_force && objectionCards.length === 0) {
            var forceRows = queryDbSafe(
              dbPath,
              "SELECT * FROM objection_cards WHERE LOWER(force_type) = ? LIMIT 5",
              [prospect.objection_force.toLowerCase()],
            );
            if (forceRows && !forceRows.error) objectionCards = forceRows;
          }

          var sheet = buildHandoffSheet(prospect, tree, personaCard, objectionCards);
          return { handoff_sheet: sheet, prospect_id: prospect.id, prospect_name: prospect.name };
        },
      };
    },
    { priority: 0 },
  );

  // =============================================
  // TOOL: outreach_query
  // =============================================
  api.registerTool(
    function () {
      return {
        name: "outreach_query",
        description:
          "Query the outreach pipeline database. Returns prospect records " +
          "matching filters. Use for ad-hoc lookups before composing outreach.",
        parameters: {
          type: "object",
          properties: {
            filter: {
              type: "string",
              description:
                "SQL WHERE clause fragment (e.g. \"lane = 'buyer' AND funnel_stage = 'discovery'\")",
            },
            columns: {
              type: "string",
              description:
                "Comma-separated column names to return. Default: id,name,company,lane,funnel_stage,pain_bucket,signal_type",
            },
            limit: {
              type: "integer",
              description: "Max rows to return. Default: 20",
            },
          },
        },
        execute: function (params) {
          if (!fs.existsSync(dbPath)) {
            return { error: "outreach.db not found at: " + dbPath };
          }
          var ALLOWED_COLUMNS = [
            "id",
            "name",
            "company",
            "lane",
            "funnel_stage",
            "pain_bucket",
            "signal_type",
          ];
          var cols = params.columns || ALLOWED_COLUMNS.join(",");
          // Columns are identifiers (cannot be parameterized). Whitelist against
          // the known prospect columns: charset-checking alone would still let a
          // caller read arbitrary/unintended fields. Reject anything off the list.
          var colList = cols.split(",").map(function (c) {
            return c.trim();
          });
          if (
            !colList.length ||
            !colList.every(function (c) {
              return ALLOWED_COLUMNS.indexOf(c) !== -1;
            })
          ) {
            return {
              error: "columns must be a comma-separated subset of: " + ALLOWED_COLUMNS.join(","),
            };
          }
          cols = colList.join(",");
          var lim = Math.max(1, Math.min(100, parseInt(params.limit, 10) || 20));

          var sql = "SELECT " + cols + " FROM prospects";
          var listParams = [];
          if (params.filter) {
            // Free-form SQL is unsafe. Accept only "column OP value"; the column is
            // a validated identifier and the value is bound as a parameter.
            var m = String(params.filter).match(
              /^\s*([A-Za-z0-9_]+)\s*(=|!=|LIKE)\s*'?([^';]*)'?\s*$/i,
            );
            if (!m) {
              return {
                error: "filter must be 'column = value', 'column != value', or 'column LIKE value'",
              };
            }
            if (ALLOWED_COLUMNS.indexOf(m[1]) === -1) {
              return { error: "filter column must be one of: " + ALLOWED_COLUMNS.join(",") };
            }
            sql += " WHERE " + m[1] + " " + m[2].toUpperCase() + " ?";
            listParams.push(m[3]);
          }
          sql += " LIMIT " + lim;

          var rows = queryDbSafe(dbPath, sql, listParams);
          if (rows.error) return { error: rows.error };
          return { count: rows.length, prospects: rows };
        },
      };
    },
    { priority: 0 },
  );
}

module.exports = {
  register,
};
