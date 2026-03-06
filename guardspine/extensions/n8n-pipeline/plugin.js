/**
 * n8n Pipeline Manager - OpenClaw Extension
 *
 * Gives AI agents the ability to create, execute, monitor, and modify
 * n8n workflows via the n8n REST API.
 *
 * Architecture: "n8n runs the pipeline. OpenClaw handles the edge cases."
 * This extension is HOW OpenClaw creates and manages those pipelines.
 *
 * Tools exposed:
 *   n8n_list_workflows   (L1) - List all workflows
 *   n8n_get_workflow      (L1) - Get a workflow definition
 *   n8n_create_workflow   (L2) - Create a new workflow
 *   n8n_update_workflow   (L2) - Update an existing workflow
 *   n8n_activate_workflow (L2) - Activate/deactivate a workflow
 *   n8n_execute_workflow  (L2) - Trigger a workflow execution
 *   n8n_get_executions    (L1) - List recent executions
 *   n8n_get_execution     (L1) - Get execution details/results
 */

const https = require("https");
const http = require("http");

module.exports = function register(api) {
  const pluginCfg = api.pluginConfig || {};
  const baseUrl =
    pluginCfg.n8n_base_url ||
    process.env.N8N_BASE_URL ||
    "https://n8n-production-32ffd.up.railway.app";
  const apiKey = pluginCfg.n8n_api_key || process.env.N8N_API_KEY || "";

  if (!apiKey) {
    console.log(
      "[n8n-pipeline] WARNING: No API key configured. Set N8N_API_KEY env var or n8n_api_key in plugin config.",
    );
  }

  // ---------------------------------------------------------------
  // HTTP client for n8n REST API
  // ---------------------------------------------------------------

  function n8nRequest(method, path, body) {
    return new Promise((resolve, reject) => {
      const url = new URL(baseUrl + path);
      const isHttps = url.protocol === "https:";
      const transport = isHttps ? https : http;

      const headers = {
        Accept: "application/json",
        "X-N8N-API-KEY": apiKey,
      };
      if (body) headers["Content-Type"] = "application/json";

      const payload = body ? JSON.stringify(body) : null;

      const req = transport.request(
        url,
        {
          method,
          headers,
          timeout: 30000,
        },
        (res) => {
          let data = "";
          res.on("data", (chunk) => {
            data += chunk;
          });
          res.on("end", () => {
            if (res.statusCode >= 400) {
              let msg = "n8n API error " + res.statusCode;
              try {
                msg += ": " + JSON.parse(data).message;
              } catch (e) {
                msg += ": " + data.substring(0, 200);
              }
              reject(new Error(msg));
              return;
            }
            try {
              resolve(JSON.parse(data));
            } catch (e) {
              resolve({ raw: data });
            }
          });
        },
      );

      req.on("timeout", () => {
        req.destroy();
        reject(new Error("n8n API timeout (30s)"));
      });
      req.on("error", (e) => reject(e));
      if (payload) req.write(payload);
      req.end();
    });
  }

  // ---------------------------------------------------------------
  // TOOL: n8n_list_workflows (L1)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_list_workflows",
      description:
        "List all n8n workflows. Returns id, name, active status, and tags for each workflow.",
      parameters: {
        type: "object",
        properties: {
          active: { type: "boolean", description: "Filter by active status" },
          tags: { type: "string", description: "Filter by tag name" },
          limit: { type: "integer", description: "Max results (default 100)", default: 100 },
        },
      },
      execute: async (params) => {
        try {
          let path = "/api/v1/workflows?limit=" + (params.limit || 100);
          if (params.active !== undefined) path += "&active=" + params.active;
          if (params.tags) path += "&tags=" + encodeURIComponent(params.tags);
          const result = await n8nRequest("GET", path);
          const workflows = (result.data || []).map((w) => ({
            id: w.id,
            name: w.name,
            active: w.active,
            createdAt: w.createdAt,
            updatedAt: w.updatedAt,
            tags: (w.tags || []).map((t) => t.name),
          }));
          return { count: workflows.length, workflows };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_get_workflow (L1)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_get_workflow",
      description:
        "Get the full definition of an n8n workflow by ID. Returns nodes, connections, and settings.",
      parameters: {
        type: "object",
        properties: {
          workflow_id: { type: "string", description: "The workflow ID" },
        },
        required: ["workflow_id"],
      },
      execute: async (params) => {
        try {
          const wf = await n8nRequest("GET", "/api/v1/workflows/" + params.workflow_id);
          return {
            id: wf.id,
            name: wf.name,
            active: wf.active,
            nodes: wf.nodes,
            connections: wf.connections,
            settings: wf.settings,
            tags: (wf.tags || []).map((t) => t.name),
            staticData: wf.staticData,
          };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_create_workflow (L2)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_create_workflow",
      description:
        "Create a new n8n workflow. Provide name, nodes array, and connections object. The workflow is created inactive by default.",
      parameters: {
        type: "object",
        properties: {
          name: { type: "string", description: "Workflow name" },
          nodes: {
            type: "array",
            description:
              "Array of n8n node objects. Each needs: name, type, typeVersion, position [x,y], parameters.",
          },
          connections: {
            type: "object",
            description:
              "Connection map: { 'NodeName': { main: [[{ node: 'TargetName', type: 'main', index: 0 }]] } }",
          },
          settings: {
            type: "object",
            description: "Optional workflow settings (e.g. executionOrder, timezone)",
          },
          tags: {
            type: "array",
            description: "Optional tag names to apply",
            items: { type: "string" },
          },
          activate: {
            type: "boolean",
            description: "Activate immediately after creation (default false)",
            default: false,
          },
        },
        required: ["name", "nodes", "connections"],
      },
      execute: async (params) => {
        try {
          const body = {
            name: params.name,
            nodes: params.nodes,
            connections: params.connections,
            settings: params.settings || { executionOrder: "v1" },
          };

          const wf = await n8nRequest("POST", "/api/v1/workflows", body);

          // Apply tags if provided
          if (params.tags && params.tags.length > 0 && wf.id) {
            try {
              // Tags need to exist first - create or find them
              for (const tagName of params.tags) {
                try {
                  await n8nRequest("POST", "/api/v1/tags", { name: tagName });
                } catch (e) {
                  // Tag may already exist, that's fine
                }
              }
            } catch (e) {
              // Non-fatal
            }
          }

          // Activate if requested
          if (params.activate && wf.id) {
            try {
              await n8nRequest("PATCH", "/api/v1/workflows/" + wf.id, { active: true });
            } catch (e) {
              return {
                id: wf.id,
                name: wf.name,
                created: true,
                activated: false,
                activate_error: e.message,
              };
            }
          }

          return {
            id: wf.id,
            name: wf.name,
            created: true,
            active: params.activate || false,
          };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_update_workflow (L2)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_update_workflow",
      description:
        "Update an existing n8n workflow. Provide the workflow ID and the fields to update (name, nodes, connections, settings).",
      parameters: {
        type: "object",
        properties: {
          workflow_id: { type: "string", description: "The workflow ID to update" },
          name: { type: "string", description: "New workflow name" },
          nodes: { type: "array", description: "Updated nodes array" },
          connections: { type: "object", description: "Updated connections" },
          settings: { type: "object", description: "Updated settings" },
        },
        required: ["workflow_id"],
      },
      execute: async (params) => {
        try {
          const body = {};
          if (params.name) body.name = params.name;
          if (params.nodes) body.nodes = params.nodes;
          if (params.connections) body.connections = params.connections;
          if (params.settings) body.settings = params.settings;

          if (Object.keys(body).length === 0) {
            return {
              error:
                "No fields to update. Provide at least one of: name, nodes, connections, settings.",
            };
          }

          const wf = await n8nRequest("PATCH", "/api/v1/workflows/" + params.workflow_id, body);
          return {
            id: wf.id,
            name: wf.name,
            updated: true,
            active: wf.active,
          };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_activate_workflow (L2)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_activate_workflow",
      description: "Activate or deactivate an n8n workflow.",
      parameters: {
        type: "object",
        properties: {
          workflow_id: { type: "string", description: "The workflow ID" },
          active: { type: "boolean", description: "true to activate, false to deactivate" },
        },
        required: ["workflow_id", "active"],
      },
      execute: async (params) => {
        try {
          const wf = await n8nRequest("PATCH", "/api/v1/workflows/" + params.workflow_id, {
            active: params.active,
          });
          return { id: wf.id, name: wf.name, active: wf.active };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_execute_workflow (L2)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_execute_workflow",
      description:
        "Execute (trigger) an n8n workflow. Optionally pass input data. Returns the execution ID for tracking.",
      parameters: {
        type: "object",
        properties: {
          workflow_id: { type: "string", description: "The workflow ID to execute" },
          data: { type: "object", description: "Input data to pass to the workflow trigger" },
        },
        required: ["workflow_id"],
      },
      execute: async (params) => {
        try {
          const body = {};
          if (params.data) body.data = params.data;

          // n8n v1 API: POST /api/v1/workflows/{id}/run
          // Some versions use /executions with workflowId
          const result = await n8nRequest("POST", "/api/v1/executions", {
            workflowId: params.workflow_id,
            data: params.data || {},
          });

          return {
            execution_id: result.id || result.data?.id,
            status: result.status || "started",
            workflow_id: params.workflow_id,
          };
        } catch (e) {
          // Fallback: try the /run endpoint
          try {
            const result = await n8nRequest(
              "POST",
              "/api/v1/workflows/" + params.workflow_id + "/run",
              {
                data: params.data || {},
              },
            );
            return {
              execution_id: result.id || result.data?.id,
              status: result.status || "started",
              workflow_id: params.workflow_id,
            };
          } catch (e2) {
            return { error: e.message + " (fallback: " + e2.message + ")" };
          }
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_get_executions (L1)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_get_executions",
      description: "List recent workflow executions. Filter by workflow ID, status, or date range.",
      parameters: {
        type: "object",
        properties: {
          workflow_id: { type: "string", description: "Filter by workflow ID" },
          status: {
            type: "string",
            enum: ["success", "error", "waiting", "running"],
            description: "Filter by status",
          },
          limit: { type: "integer", description: "Max results (default 20)", default: 20 },
        },
      },
      execute: async (params) => {
        try {
          let path = "/api/v1/executions?limit=" + (params.limit || 20);
          if (params.workflow_id) path += "&workflowId=" + params.workflow_id;
          if (params.status) path += "&status=" + params.status;

          const result = await n8nRequest("GET", path);
          const executions = (result.data || []).map((ex) => ({
            id: ex.id,
            workflowId: ex.workflowId,
            status: ex.status || (ex.finished ? "success" : "running"),
            startedAt: ex.startedAt,
            stoppedAt: ex.stoppedAt,
            mode: ex.mode,
          }));
          return { count: executions.length, executions };
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // TOOL: n8n_get_execution (L1)
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_get_execution",
      description:
        "Get details of a specific workflow execution by ID. Returns node results, errors, and timing.",
      parameters: {
        type: "object",
        properties: {
          execution_id: { type: "string", description: "The execution ID" },
          include_data: {
            type: "boolean",
            description: "Include full node output data (default false)",
            default: false,
          },
        },
        required: ["execution_id"],
      },
      execute: async (params) => {
        try {
          const ex = await n8nRequest("GET", "/api/v1/executions/" + params.execution_id);

          const result = {
            id: ex.id,
            workflowId: ex.workflowId,
            status: ex.status || (ex.finished ? "success" : "running"),
            startedAt: ex.startedAt,
            stoppedAt: ex.stoppedAt,
            mode: ex.mode,
          };

          // Summarize node results
          if (ex.data && ex.data.resultData && ex.data.resultData.runData) {
            const runData = ex.data.resultData.runData;
            result.nodes = {};
            for (const [nodeName, runs] of Object.entries(runData)) {
              const lastRun = runs[runs.length - 1];
              result.nodes[nodeName] = {
                status: lastRun.error ? "error" : "success",
                items: lastRun.data?.main?.[0]?.length || 0,
                executionTime: lastRun.executionTime,
              };
              if (lastRun.error) {
                result.nodes[nodeName].error = lastRun.error.message || String(lastRun.error);
              }
              if (params.include_data && lastRun.data?.main?.[0]) {
                // Truncate large outputs
                const items = lastRun.data.main[0].map((item) => {
                  const json = item.json || {};
                  const str = JSON.stringify(json);
                  return str.length > 2000 ? JSON.parse(str.substring(0, 2000) + '..."') : json;
                });
                result.nodes[nodeName].data = items;
              }
            }
          }

          // Include error if execution failed
          if (ex.data && ex.data.resultData && ex.data.resultData.error) {
            result.error = ex.data.resultData.error.message || String(ex.data.resultData.error);
          }

          return result;
        } catch (e) {
          return { error: e.message };
        }
      },
    }),
    { priority: 0 },
  );

  // ---------------------------------------------------------------
  // Webhook routes: endpoints that n8n workflows POST to
  // ---------------------------------------------------------------

  function parseJsonBody(req) {
    return new Promise((resolve, reject) => {
      let data = "";
      req.on("data", (chunk) => {
        data += chunk;
      });
      req.on("end", () => {
        try {
          resolve(data ? JSON.parse(data) : {});
        } catch (e) {
          reject(new Error("Invalid JSON body"));
        }
      });
      req.on("error", reject);
    });
  }

  function jsonResponse(res, status, body) {
    res.statusCode = status;
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(body));
  }

  // ---------------------------------------------------------------
  // Webhook handler implementations
  // ---------------------------------------------------------------

  const landingBaseUrl =
    pluginCfg.landing_base_url ||
    process.env.LANDING_BASE_URL ||
    "https://guardspine-landing-production.up.railway.app";
  const landingAdminKey = pluginCfg.landing_admin_key || process.env.LANDING_ADMIN_API_KEY || "";
  const outreachDbPath =
    pluginCfg.outreach_db_path || process.env.OUTREACH_DB_PATH || "/data/outreach.db";

  const fs = require("fs");
  const { execFile } = require("child_process");
  const url = require("url");

  // HTTP GET helper (returns parsed JSON)
  function httpGet(targetUrl, timeoutMs) {
    return new Promise((resolve, reject) => {
      const parsed = new URL(targetUrl);
      const mod = parsed.protocol === "https:" ? https : http;
      const req = mod.get(targetUrl, { timeout: timeoutMs || 10000 }, (res) => {
        let data = "";
        res.on("data", (chunk) => {
          data += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(new Error("Invalid JSON from " + targetUrl));
          }
        });
      });
      req.on("error", reject);
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Timeout: " + targetUrl));
      });
    });
  }

  // SQLite query helper (shells out to sqlite3 CLI)
  function sqliteQuery(dbPath, query) {
    return new Promise((resolve, reject) => {
      if (!fs.existsSync(dbPath)) {
        resolve([]);
        return;
      }
      execFile("sqlite3", ["-json", dbPath, query], { timeout: 10000 }, (err, stdout) => {
        if (err) {
          resolve([]);
          return;
        }
        try {
          resolve(JSON.parse(stdout || "[]"));
        } catch (e) {
          resolve([]);
        }
      });
    });
  }

  function stub(data) {
    return Object.assign({ _stub: true }, data);
  }

  // --- Lead Pipeline handlers ---

  async function checkNewLeads() {
    // Query outreach.db for prospects with signals in last 24h
    const rows = await sqliteQuery(
      outreachDbPath,
      "SELECT name, company, signal_type, lane, message_sent_at " +
        "FROM prospects " +
        "WHERE signal_type IS NOT NULL AND signal_type != 'none' " +
        "AND message_sent_at >= datetime('now', '-24 hours') " +
        "ORDER BY message_sent_at DESC",
    );
    return { new_leads_count: rows.length, new_leads: rows };
  }

  async function checkLandingSignups() {
    if (!landingAdminKey) {
      return stub({
        signup_count: 0,
        signups: [],
        demo_count: 0,
        demos: [],
        error: "No LANDING_ADMIN_API_KEY",
      });
    }
    try {
      const data = await httpGet(
        landingBaseUrl + "/api/admin/signups?key=" + encodeURIComponent(landingAdminKey),
        10000,
      );
      const signups = data.signups || [];
      const demos = data.demoRequests || [];
      // Filter to last 24h
      const cutoff = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
      const recentSignups = signups.filter((s) => s.created_at >= cutoff);
      const recentDemos = demos.filter((d) => d.created_at >= cutoff);
      return {
        signup_count: recentSignups.length,
        signups: recentSignups,
        demo_count: recentDemos.length,
        demos: recentDemos,
        total_signups: signups.length,
        total_demos: demos.length,
      };
    } catch (e) {
      return stub({ signup_count: 0, signups: [], error: e.message });
    }
  }

  async function composeFollowups(body) {
    // For now, return the leads that need follow-up drafts.
    // Real AI drafting would call LiteLLM via the agent -- that's an INT-2 task.
    const leads = body.leads || "[]";
    let parsed = [];
    try {
      parsed = typeof leads === "string" ? JSON.parse(leads) : leads;
    } catch (e) {
      /* skip */
    }
    return stub({ drafted: 0, leads: parsed, note: "AI drafting not yet wired (INT-2)" });
  }

  // --- Pilot Pipeline handlers (still stubbed -- needs GitHub API + codeguard telemetry) ---

  // --- Morning Brief handlers (still stubbed -- needs multi-source aggregation) ---

  const WEBHOOK_HANDLERS = {
    "/webhook/lead-pipeline": {
      check_new_leads: checkNewLeads,
      check_landing_signups: checkLandingSignups,
      compose_followups: composeFollowups,
    },
    "/webhook/pilot-pipeline": {
      check_pilot_repos: () => stub({ issues_count: 0, repos: [] }),
      check_evidence_bundles: () => stub({ bundle_count: 0, evidence_summary: [] }),
      generate_pilot_report: (body) =>
        stub({ report: "stub", repos: body.repos || "[]", bundles: body.bundles || "[]" }),
    },
    "/webhook/morning-brief": {
      gather_data: () => stub({ outreach: {}, github: {}, railway: {}, calendar: {} }),
      format_brief: (body) =>
        stub({
          formatted_brief: "Morning brief stub. Data: " + (body.data || "{}").substring(0, 200),
        }),
      deliver_brief: (body) => stub({ delivered: true, channel: body.channel || "discord" }),
    },
  };

  for (const [routePath, actions] of Object.entries(WEBHOOK_HANDLERS)) {
    api.registerHttpRoute({
      path: routePath,
      auth: "gateway",
      match: "exact",
      handler: async (req, res) => {
        if (req.method !== "POST") {
          jsonResponse(res, 405, { error: "Method not allowed" });
          return true;
        }
        try {
          const body = await parseJsonBody(req);
          const action = body.action;
          if (!action || !actions[action]) {
            jsonResponse(res, 400, {
              error: "Unknown action: " + (action || "(none)"),
              available: Object.keys(actions),
            });
            return true;
          }
          const result = await actions[action](body);
          jsonResponse(res, 200, result);
        } catch (e) {
          jsonResponse(res, 500, { error: e.message });
        }
        return true;
      },
    });
  }

  // ---------------------------------------------------------------
  // Inject context on agent start
  // ---------------------------------------------------------------

  api.on(
    "before_agent_start",
    async () => {
      return {
        prependContext:
          "[N8N] n8n Pipeline Manager active. You can create, list, execute, and monitor n8n workflows. " +
          "Architecture: n8n handles 95% deterministic work, you handle 5% edge cases. " +
          "Use n8n_list_workflows to see existing pipelines. Use n8n_create_workflow to build new ones.",
      };
    },
    { priority: 10 },
  );

  console.log(
    "[n8n-pipeline] Extension loaded. Base URL: " +
      baseUrl +
      " | API key: " +
      (apiKey ? "configured" : "MISSING"),
  );
};
