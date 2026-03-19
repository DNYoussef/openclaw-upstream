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
    "https://n8n-production-7528.up.railway.app";
  const apiKey = pluginCfg.n8n_api_key || process.env.N8N_API_KEY || "";

  if (!apiKey) {
    console.log(
      "[n8n-pipeline] WARNING: No API key configured. Set N8N_API_KEY env var or n8n_api_key in plugin config.",
    );
  }

  // BUG N3: Configurable response size limit (default 100KB)
  const maxResponseBytes =
    Number(pluginCfg.max_response_bytes) || Number(process.env.N8N_MAX_RESPONSE_BYTES) || 102400;

  // BUG N5: Workflow name-to-ID cache with TTL
  let workflowNameCache = null;
  let workflowCacheExpiry = 0;
  const WORKFLOW_CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes

  // ---------------------------------------------------------------
  // HTTP client for n8n REST API
  // ---------------------------------------------------------------

  // BUG N4: Status codes that should NOT be retried (client errors)
  const NON_RETRYABLE_STATUS = new Set([400, 401, 403, 404, 405, 409, 422]);

  function n8nRequestOnce(method, path, body) {
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
              // BUG N4: Attach status code and Retry-After header to error
              const err = new Error(msg);
              err.statusCode = res.statusCode;
              err.retryAfter = res.headers["retry-after"]
                ? Number(res.headers["retry-after"])
                : null;
              reject(err);
              return;
            }
            // BUG N3: Truncate oversized responses before JSON.parse
            let truncated = false;
            if (data.length > maxResponseBytes) {
              // Find the last complete JSON object/array boundary before the limit
              let cutoff = maxResponseBytes;
              const slice = data.substring(0, cutoff);
              // Walk backward to find last '}' or ']' that could close a JSON structure
              for (let i = slice.length - 1; i >= 0; i--) {
                if (slice[i] === "}" || slice[i] === "]") {
                  cutoff = i + 1;
                  break;
                }
              }
              data = data.substring(0, cutoff);
              truncated = true;
            }
            try {
              const parsed = JSON.parse(data);
              if (truncated) {
                parsed._truncated = "response exceeded " + maxResponseBytes + " byte limit";
              }
              resolve(parsed);
            } catch (e) {
              if (truncated) {
                resolve({
                  raw: data,
                  _truncated:
                    "response exceeded " + maxResponseBytes + " byte limit (parse failed)",
                });
              } else {
                resolve({ raw: data });
              }
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

  // BUG N4: Retry wrapper - only retries on server/timeout/rate-limit errors
  async function n8nRequest(method, path, body) {
    const MAX_RETRIES = 3;
    const BASE_DELAY_MS = 1000;
    let lastErr = null;

    for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
      try {
        return await n8nRequestOnce(method, path, body);
      } catch (e) {
        lastErr = e;
        const status = e.statusCode;

        // Fail immediately on client errors - retrying won't help
        if (status && NON_RETRYABLE_STATUS.has(status)) {
          throw e;
        }

        // No more retries left
        if (attempt >= MAX_RETRIES) {
          throw e;
        }

        // Calculate delay: respect Retry-After on 429, else exponential backoff
        let delayMs;
        if (status === 429 && e.retryAfter && e.retryAfter > 0) {
          delayMs = e.retryAfter * 1000;
        } else {
          delayMs = BASE_DELAY_MS * Math.pow(2, attempt); // 1s, 2s, 4s
        }

        console.log(
          "[n8n-pipeline] " +
            method +
            " " +
            path +
            " failed (status=" +
            (status || "network") +
            "), retry " +
            (attempt + 1) +
            "/" +
            MAX_RETRIES +
            " in " +
            delayMs +
            "ms",
        );

        await new Promise((r) => setTimeout(r, delayMs));
      }
    }
    throw lastErr;
  }

  // ---------------------------------------------------------------
  // BUG N5: Workflow name-to-ID resolution
  // ---------------------------------------------------------------

  async function refreshWorkflowCache() {
    try {
      const result = await n8nRequest("GET", "/api/v1/workflows?limit=250");
      const map = {};
      for (const wf of result.data || []) {
        map[wf.name] = wf.id;
      }
      workflowNameCache = map;
      workflowCacheExpiry = Date.now() + WORKFLOW_CACHE_TTL_MS;
      return map;
    } catch (e) {
      console.error("[n8n-pipeline] Failed to refresh workflow cache: " + e.message);
      return workflowNameCache || {};
    }
  }

  async function resolveWorkflowId(nameOrId) {
    if (!nameOrId) {
      throw new Error("workflow_id is required");
    }
    // If it looks like a pure numeric or n8n-style alphanumeric ID, try it directly
    // but also check cache in case it's actually a name
    const looksLikeId = /^[a-zA-Z0-9_-]+$/.test(nameOrId) && nameOrId.length <= 30;

    // Refresh cache if expired or missing
    if (!workflowNameCache || Date.now() > workflowCacheExpiry) {
      await refreshWorkflowCache();
    }

    // Check by name first (exact match)
    if (workflowNameCache && workflowNameCache[nameOrId]) {
      return workflowNameCache[nameOrId];
    }

    // If it looks like an ID, return as-is
    if (looksLikeId) {
      return nameOrId;
    }

    // Force-refresh cache once in case workflow was just created
    if (Date.now() <= workflowCacheExpiry) {
      // Cache is fresh but name not found, try raw
      return nameOrId;
    }
    await refreshWorkflowCache();
    if (workflowNameCache && workflowNameCache[nameOrId]) {
      return workflowNameCache[nameOrId];
    }

    throw new Error(
      "Workflow not found: '" +
        nameOrId +
        "'. Not a known workflow name and does not look like a valid ID. " +
        "Available workflows: " +
        Object.keys(workflowNameCache || {}).join(", "),
    );
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
          workflow_id: { type: "string", description: "The workflow ID or name" },
        },
        required: ["workflow_id"],
      },
      execute: async (params) => {
        try {
          const resolvedId = await resolveWorkflowId(params.workflow_id);
          const wf = await n8nRequest("GET", "/api/v1/workflows/" + resolvedId);
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
          workflow_id: { type: "string", description: "The workflow ID or name to update" },
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

          const resolvedId = await resolveWorkflowId(params.workflow_id);
          const wf = await n8nRequest("PATCH", "/api/v1/workflows/" + resolvedId, body);
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
          workflow_id: { type: "string", description: "The workflow ID or name" },
          active: { type: "boolean", description: "true to activate, false to deactivate" },
        },
        required: ["workflow_id", "active"],
      },
      execute: async (params) => {
        try {
          const resolvedId = await resolveWorkflowId(params.workflow_id);
          const wf = await n8nRequest("PATCH", "/api/v1/workflows/" + resolvedId, {
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
          workflow_id: { type: "string", description: "The workflow ID or name to execute" },
          data: { type: "object", description: "Input data to pass to the workflow trigger" },
        },
        required: ["workflow_id"],
      },
      execute: async (params) => {
        try {
          const body = {};
          if (params.data) body.data = params.data;

          const resolvedId = await resolveWorkflowId(params.workflow_id);

          // n8n v1 API: POST /api/v1/workflows/{id}/run
          // Some versions use /executions with workflowId
          const result = await n8nRequest("POST", "/api/v1/executions", {
            workflowId: resolvedId,
            data: params.data || {},
          });

          return {
            execution_id: result.id || result.data?.id,
            status: result.status || "started",
            workflow_id: resolvedId,
          };
        } catch (e) {
          // Fallback: try the /run endpoint
          try {
            const fallbackId = await resolveWorkflowId(params.workflow_id);
            const result = await n8nRequest("POST", "/api/v1/workflows/" + fallbackId + "/run", {
              data: params.data || {},
            });
            return {
              execution_id: result.id || result.data?.id,
              status: result.status || "started",
              workflow_id: fallbackId,
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
          workflow_id: { type: "string", description: "Filter by workflow ID or name" },
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
          if (params.workflow_id) {
            const resolvedId = await resolveWorkflowId(params.workflow_id);
            path += "&workflowId=" + resolvedId;
          }
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
                // BUG N3: Safely truncate large outputs without crashing
                const items = lastRun.data.main[0].map((item) => {
                  const json = item.json || {};
                  const str = JSON.stringify(json);
                  if (str.length > 2000) {
                    // Find last complete JSON boundary before the 2000-char limit
                    let cutoff = 2000;
                    for (let i = cutoff - 1; i >= 0; i--) {
                      if (str[i] === "}" || str[i] === "]" || str[i] === "," || str[i] === '"') {
                        cutoff = i + 1;
                        break;
                      }
                    }
                    return {
                      _truncated: true,
                      _original_bytes: str.length,
                      preview: str.substring(0, cutoff),
                    };
                  }
                  return json;
                });
                result.nodes[nodeName].data = items;
              }
            }
          }

          // Include error if execution failed
          if (ex.data && ex.data.resultData && ex.data.resultData.error) {
            result.error = ex.data.resultData.error.message || String(ex.data.resultData.error);
          }

          // BUG N3: Final safety check - ensure serialized result is under limit
          const serialized = JSON.stringify(result);
          if (serialized.length > maxResponseBytes) {
            // Strip node data to fit, keep metadata
            if (result.nodes) {
              for (const nodeName of Object.keys(result.nodes)) {
                delete result.nodes[nodeName].data;
              }
            }
            result._truncated =
              "Full result exceeded " + maxResponseBytes + " byte limit; node data stripped";
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
  // TOOL: n8n_request_approval (L3) - Escalate to n8n approval workflow
  // ---------------------------------------------------------------

  api.registerTool(
    () => ({
      name: "n8n_request_approval",
      description:
        "Request human approval via an n8n governance workflow. Creates an execution of the " +
        "governance-approval-flow workflow, passing the action description, risk tier, requester " +
        "info, and evidence hash. Returns the execution ID for tracking. Use this for L3-L4 " +
        "escalations (outreach emails, dangerous operations, etc.).",
      parameters: {
        type: "object",
        properties: {
          action_type: {
            type: "string",
            description:
              "Type of action needing approval (e.g. 'outreach_email', 'deploy', 'config_change')",
          },
          action_description: {
            type: "string",
            description: "Human-readable description of what needs approval",
          },
          risk_tier: {
            type: "string",
            enum: ["L3", "L4"],
            description: "GuardSpine risk tier (L3 = council review, L4 = human approval required)",
          },
          requester: {
            type: "string",
            description: "Who is requesting this action (agent name or human)",
          },
          evidence_hash: {
            type: "string",
            description: "SHA-256 hash of the action evidence for tamper-proof tracking",
          },
          context: {
            type: "object",
            description: "Additional context (prospect_id, recipient, subject, etc.)",
          },
          workflow_name: {
            type: "string",
            description: "n8n workflow name to trigger (default: 'governance-approval-flow')",
            default: "governance-approval-flow",
          },
        },
        required: ["action_type", "action_description", "risk_tier", "requester"],
      },
      execute: async (params) => {
        const workflowName = params.workflow_name || "governance-approval-flow";
        const approvalData = {
          action_type: params.action_type,
          action_description: params.action_description,
          risk_tier: params.risk_tier,
          requester: params.requester,
          evidence_hash: params.evidence_hash || "none",
          context: params.context || {},
          requested_at: new Date().toISOString(),
        };

        try {
          const resolvedId = await resolveWorkflowId(workflowName);

          // Try the executions endpoint first
          let result;
          try {
            result = await n8nRequest("POST", "/api/v1/executions", {
              workflowId: resolvedId,
              data: approvalData,
            });
          } catch (e1) {
            // Fallback to /run endpoint
            try {
              result = await n8nRequest("POST", "/api/v1/workflows/" + resolvedId + "/run", {
                data: approvalData,
              });
            } catch (e2) {
              // n8n unreachable -- log and return degraded result
              console.error(
                "[n8n-pipeline] n8n_request_approval: both endpoints failed. " +
                  "Primary: " +
                  e1.message +
                  " | Fallback: " +
                  e2.message,
              );
              return {
                status: "degraded",
                approval_requested: false,
                reason: "n8n unreachable: " + e1.message,
                action_type: params.action_type,
                risk_tier: params.risk_tier,
                evidence_hash: params.evidence_hash || "none",
                fallback: "Action logged locally. Manual approval required.",
              };
            }
          }

          return {
            status: "pending",
            approval_requested: true,
            execution_id: result.id || (result.data && result.data.id),
            workflow_id: resolvedId,
            workflow_name: workflowName,
            action_type: params.action_type,
            risk_tier: params.risk_tier,
            evidence_hash: params.evidence_hash || "none",
          };
        } catch (e) {
          // Workflow not found or other resolution error
          console.error("[n8n-pipeline] n8n_request_approval error: " + e.message);
          return {
            status: "degraded",
            approval_requested: false,
            reason: e.message,
            action_type: params.action_type,
            risk_tier: params.risk_tier,
            evidence_hash: params.evidence_hash || "none",
            fallback:
              "Workflow '" + workflowName + "' not found. Create it in n8n or approve manually.",
          };
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
      const MAX_BODY = 1_000_000; // 1MB
      req.on("data", (chunk) => {
        data += chunk;
        if (data.length > MAX_BODY) {
          req.destroy();
          reject(new Error("Request body too large (>" + MAX_BODY + " bytes)"));
        }
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
    pluginCfg.outreach_db_path || process.env.OUTREACH_DB_PATH || "/app/.openclaw/data/outreach.db";

  const fs = require("fs");
  const path = require("path");
  const { execFile, execFileSync } = require("child_process");
  const url = require("url");

  // HTTP GET helper (returns parsed JSON)
  function httpGet(targetUrl, timeoutMs, extraHeaders) {
    return new Promise((resolve, reject) => {
      const parsed = new URL(targetUrl);
      const mod = parsed.protocol === "https:" ? https : http;
      const options = { timeout: timeoutMs || 10000, headers: extraHeaders || {} };
      const req = mod.get(targetUrl, options, (res) => {
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

  // Ensure outreach DB exists with correct schema.
  // Data lives on Railway volume (or local disk), never in git or Docker image.
  // Schema lives in guardspine/data/migration.sql (code, not data).
  function ensureDb(dbPath) {
    if (fs.existsSync(dbPath)) return;
    const dir = path.dirname(dbPath);
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
    // Find migration.sql relative to this plugin
    const migrationPaths = [
      path.join(__dirname, "..", "..", "data", "migration.sql"),
      path.join(__dirname, "..", "data", "migration.sql"),
      "/app/.openclaw/data/migration.sql",
    ];
    let migrationSql = null;
    for (const p of migrationPaths) {
      if (fs.existsSync(p)) {
        migrationSql = fs.readFileSync(p, "utf8");
        break;
      }
    }
    if (!migrationSql) {
      console.error("[n8n-pipeline] No migration.sql found. DB will not be created.");
      return;
    }
    try {
      execFileSync("sqlite3", [dbPath], { input: migrationSql, timeout: 10000 });
      console.log("[n8n-pipeline] Created outreach DB from migration.sql at " + dbPath);
    } catch (e) {
      console.error("[n8n-pipeline] Failed to create DB:", e.message);
    }
  }

  ensureDb(outreachDbPath);

  // SQLite query helper (shells out to sqlite3 CLI)
  // Returns rows array on success, or {error, rows: []} on failure.
  function sqliteQuery(dbPath, query) {
    return new Promise((resolve, reject) => {
      if (!fs.existsSync(dbPath)) {
        console.error("[n8n-pipeline] DB not found: " + dbPath);
        resolve({ error: "DB not found: " + dbPath, rows: [] });
        return;
      }
      execFile("sqlite3", ["-json", dbPath, query], { timeout: 10000 }, (err, stdout, stderr) => {
        if (err) {
          console.error("[n8n-pipeline] sqlite3 error:", err.message, stderr || "");
          resolve({ error: err.message, rows: [] });
          return;
        }
        try {
          resolve(JSON.parse(stdout || "[]"));
        } catch (e) {
          console.error("[n8n-pipeline] sqlite3 JSON parse error:", e.message);
          resolve({ error: e.message, rows: [] });
        }
      });
    });
  }

  // Extract rows from sqliteQuery result (handles both old array and new {error, rows} format)
  function dbRows(result) {
    if (Array.isArray(result)) return result;
    if (result && result.error) return result.rows || [];
    return [];
  }

  function stub(data) {
    return Object.assign({ _stub: true }, data);
  }

  // --- Outreach Pipeline handlers (P1) ---

  async function checkResponseSignals() {
    const rows = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT id, name, company, signal_type, lane, investor_tier, message_sent_at, signal_notes " +
          "FROM prospects " +
          "WHERE signal_type IN ('green','yellow') " +
          "ORDER BY message_sent_at DESC",
      ),
    );
    const green = rows.filter((r) => r.signal_type === "green");
    const yellow = rows.filter((r) => r.signal_type === "yellow");
    return {
      green_count: green.length,
      yellow_count: yellow.length,
      green_signals: green,
      yellow_signals: yellow,
    };
  }

  async function checkLandingSignups() {
    if (!landingAdminKey) {
      return {
        signup_count: 0,
        signups: [],
        demo_count: 0,
        demos: [],
        error: "No LANDING_ADMIN_API_KEY",
      };
    }
    try {
      const data = await httpGet(landingBaseUrl + "/api/admin/signups", 10000, {
        Authorization: "Bearer " + landingAdminKey,
      });
      const signups = data.signups || [];
      const demos = data.demoRequests || [];
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
      return { signup_count: 0, signups: [], demo_count: 0, demos: [], error: e.message };
    }
  }

  async function checkFollowupsDue() {
    const rows = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT id, name, company, lane, investor_tier, message_sent_at, channel " +
          "FROM prospects " +
          "WHERE message_sent_at IS NOT NULL " +
          "AND (signal_type IS NULL OR signal_type = 'none') " +
          "AND message_sent_at <= datetime('now', '-7 days') " +
          "ORDER BY message_sent_at ASC " +
          "LIMIT 20",
      ),
    );
    return { followups_due_count: rows.length, followups_due: rows };
  }

  // HTTP POST helper (returns parsed JSON)
  function httpPost(targetUrl, payload, timeoutMs) {
    return new Promise((resolve, reject) => {
      const parsed = new URL(targetUrl);
      const mod = parsed.protocol === "https:" ? https : http;
      const data = JSON.stringify(payload);
      const opts = {
        method: "POST",
        hostname: parsed.hostname,
        port: parsed.port,
        path: parsed.pathname + parsed.search,
        timeout: timeoutMs || 15000,
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(data),
        },
      };
      const req = mod.request(opts, (res) => {
        let body = "";
        res.on("data", (chunk) => {
          body += chunk;
        });
        res.on("end", () => {
          try {
            resolve(JSON.parse(body));
          } catch (e) {
            resolve({ raw: body, statusCode: res.statusCode });
          }
        });
      });
      req.on("error", reject);
      req.on("timeout", () => {
        req.destroy();
        reject(new Error("Timeout: " + targetUrl));
      });
      req.write(data);
      req.end();
    });
  }

  async function draftFollowups(body) {
    const prospects = body.prospects || "[]";
    let parsed = [];
    try {
      parsed = typeof prospects === "string" ? JSON.parse(prospects) : prospects;
    } catch (e) {
      /* skip */
    }

    const litellmUrl = process.env.LITELLM_URL || "http://litellm.railway.internal:4000";
    const drafted = [];
    let errors = 0;

    for (const prospect of parsed) {
      // Skip prospects with no signal or already followed up twice
      if (prospect.signal_type === "none" || !prospect.signal_type) continue;
      if ((prospect.followup_count || 0) >= 2) continue;

      const prompt =
        "Draft a 2-sentence follow-up for " +
        (prospect.name || "this person") +
        " at " +
        (prospect.company || "their company") +
        ". Their pain bucket is " +
        (prospect.pain_bucket || "unknown") +
        ". Previous message was about " +
        (prospect.hook_angle || "code governance") +
        ". Keep it under 50 words. No slop words.";

      try {
        const result = await httpPost(
          litellmUrl + "/v1/chat/completions",
          {
            model: "gemini-2.0-flash",
            messages: [
              {
                role: "system",
                content: "You draft brief, direct follow-up messages for B2B outreach. No fluff.",
              },
              { role: "user", content: prompt },
            ],
            max_tokens: 120,
            temperature: 0.7,
          },
          15000,
        );

        const message =
          result.choices && result.choices[0] && result.choices[0].message
            ? result.choices[0].message.content
            : null;

        drafted.push({
          prospect_id: prospect.id,
          name: prospect.name,
          company: prospect.company,
          draft: message || "(LLM returned empty response)",
        });
      } catch (e) {
        errors++;
        drafted.push({
          prospect_id: prospect.id,
          name: prospect.name,
          company: prospect.company,
          draft: null,
          error: "LLM call failed: " + e.message,
        });
      }
    }

    return { drafted: drafted.filter((d) => d.draft && !d.error).length, errors, drafts: drafted };
  }

  async function sendAlert(body) {
    const signals = body.signals || "{}";
    let parsed = {};
    try {
      parsed = typeof signals === "string" ? JSON.parse(signals) : signals;
    } catch (e) {
      /* skip */
    }

    const slackWebhookUrl = process.env.SLACK_WEBHOOK_URL;
    const telemetryUrl =
      process.env.TELEMETRY_URL || "http://telemetry-api.railway.internal:8090/telemetry";

    // Build a readable summary from the signals
    const items = Array.isArray(parsed)
      ? parsed
      : parsed.green_signals || parsed.yellow_signals || [parsed];
    const summary =
      items
        .filter((s) => s && s.name)
        .map(
          (s) =>
            "- " +
            s.name +
            " (" +
            (s.company || "?") +
            "): " +
            (s.signal_type || "signal") +
            " -- action needed",
        )
        .join("\n") || "Alert triggered (no structured signal data)";

    if (slackWebhookUrl) {
      try {
        await httpPost(
          slackWebhookUrl,
          {
            text: "*Outreach Alert*\n" + summary,
          },
          10000,
        );
        console.log("[outreach-alert] Sent to Slack");
        return { alerted: true, channel: "slack", data: parsed };
      } catch (e) {
        console.error(
          "[outreach-alert] Slack delivery failed: " + e.message + ". Falling back to telemetry.",
        );
        // Fall through to telemetry
      }
    }

    // No Slack or Slack failed: record in telemetry
    try {
      await httpPost(
        telemetryUrl,
        {
          event_type: "alert",
          source: "outreach-pipeline",
          data: parsed,
          summary: summary,
          timestamp: new Date().toISOString(),
        },
        10000,
      );
      console.log("[outreach-alert] Recorded in telemetry");
      return { alerted: true, channel: "telemetry", data: parsed };
    } catch (e) {
      console.error("[outreach-alert] Telemetry delivery failed: " + e.message);
      // Last resort: at least log it
      console.log("[outreach-alert]", JSON.stringify(parsed));
      return {
        alerted: true,
        channel: "log",
        data: parsed,
        warning: "Both Slack and telemetry failed",
      };
    }
  }

  async function getPipelineStatus() {
    const totals = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT COUNT(*) as total, " +
          "SUM(CASE WHEN message_sent_at IS NOT NULL THEN 1 ELSE 0 END) as sent, " +
          "SUM(CASE WHEN signal_type='green' THEN 1 ELSE 0 END) as green, " +
          "SUM(CASE WHEN signal_type='yellow' THEN 1 ELSE 0 END) as yellow, " +
          "SUM(CASE WHEN signal_type='red' THEN 1 ELSE 0 END) as red " +
          "FROM prospects",
      ),
    );
    const byLane = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT lane, COUNT(*) as total, " +
          "SUM(CASE WHEN message_sent_at IS NOT NULL THEN 1 ELSE 0 END) as sent, " +
          "SUM(CASE WHEN signal_type='green' THEN 1 ELSE 0 END) as green " +
          "FROM prospects GROUP BY lane",
      ),
    );
    return {
      totals: totals[0] || {},
      by_lane: byLane,
      response_rate: totals[0]
        ? (((totals[0].green || 0) / Math.max(totals[0].sent || 1, 1)) * 100).toFixed(1) + "%"
        : "0%",
    };
  }

  // --- Narrowcast Pipeline handlers (P3) ---

  async function scanCommunities() {
    // Query existing narrowcast_scans and threads from last 24h
    const recentScans = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT * FROM narrowcast_scans ORDER BY scan_date DESC LIMIT 5",
      ),
    );
    const recentThreads = dbRows(
      await sqliteQuery(
        outreachDbPath,
        "SELECT * FROM narrowcast_threads WHERE engaged_at IS NULL ORDER BY discovered_at DESC LIMIT 10",
      ),
    );
    return {
      threads_found: recentThreads.length,
      threads: recentThreads,
      recent_scans: recentScans,
    };
  }

  // Relevance keywords for thread scoring (no LLM needed)
  const RELEVANCE_KEYWORDS = [
    { pattern: /code\s*review/i, weight: 15 },
    { pattern: /governance/i, weight: 15 },
    { pattern: /audit/i, weight: 12 },
    { pattern: /compliance/i, weight: 12 },
    { pattern: /ai\s*code/i, weight: 10 },
    { pattern: /pr\s*review/i, weight: 10 },
    { pattern: /evidence/i, weight: 8 },
    { pattern: /dora\b/i, weight: 10 },
    { pattern: /soc\s*2/i, weight: 12 },
    { pattern: /security\s*review/i, weight: 8 },
    { pattern: /code\s*quality/i, weight: 6 },
    { pattern: /pull\s*request/i, weight: 5 },
  ];

  function scoreThreadRelevance(thread) {
    const text = [
      thread.title || "",
      thread.body || "",
      thread.content || "",
      thread.url || "",
    ].join(" ");
    let score = 0;
    for (const kw of RELEVANCE_KEYWORDS) {
      if (kw.pattern.test(text)) score += kw.weight;
    }
    return Math.min(score, 100);
  }

  async function evaluateAndSource(body) {
    const threads = body.threads || "[]";
    let parsed = [];
    try {
      parsed = typeof threads === "string" ? JSON.parse(threads) : threads;
    } catch (e) {
      /* skip */
    }

    const telemetryUrl =
      process.env.TELEMETRY_URL || "http://telemetry-api.railway.internal:8090/telemetry";
    const evaluated = [];
    let prospectsAdded = 0;

    for (const thread of parsed) {
      const score = scoreThreadRelevance(thread);
      const entry = {
        url: thread.url || null,
        title: thread.title || null,
        score: score,
        qualified: score >= 60,
      };

      if (score >= 60) {
        try {
          await httpPost(
            telemetryUrl,
            {
              event_type: "prospect_sourced",
              source: "narrowcast",
              data: {
                url: thread.url,
                title: thread.title,
                author: thread.author || null,
                platform: thread.platform || null,
                relevance_score: score,
              },
              timestamp: new Date().toISOString(),
            },
            10000,
          );
          prospectsAdded++;
          entry.added = true;
        } catch (e) {
          entry.added = false;
          entry.error = e.message;
        }
      }

      evaluated.push(entry);
    }

    return {
      threads_evaluated: parsed.length,
      prospects_added: prospectsAdded,
      evaluated: evaluated,
    };
  }

  // --- Pilot Pipeline handlers (still stubbed -- needs GitHub API + codeguard telemetry) ---

  // --- Morning Brief handlers (still stubbed -- needs multi-source aggregation) ---

  const WEBHOOK_HANDLERS = {
    "/webhook/outreach-pipeline": {
      check_response_signals: checkResponseSignals,
      check_landing_signups: checkLandingSignups,
      check_followups_due: checkFollowupsDue,
      draft_followups: draftFollowups,
      send_alert: sendAlert,
      pipeline_status: getPipelineStatus,
    },
    "/webhook/narrowcast-pipeline": {
      scan_communities: scanCommunities,
      evaluate_and_source: evaluateAndSource,
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
        const t0 = Date.now();
        if (req.method !== "POST") {
          jsonResponse(res, 405, { error: "Method not allowed" });
          console.log(
            "[webhook] " + routePath + " 405 method=" + req.method + " " + (Date.now() - t0) + "ms",
          );
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
            console.log(
              "[webhook] " +
                routePath +
                " 400 action=" +
                (action || "none") +
                " " +
                (Date.now() - t0) +
                "ms",
            );
            return true;
          }
          const result = await actions[action](body);
          jsonResponse(res, 200, result);
          console.log(
            "[webhook] " + routePath + " 200 action=" + action + " " + (Date.now() - t0) + "ms",
          );
        } catch (e) {
          jsonResponse(res, 500, { error: e.message });
          console.error(
            "[webhook] " + routePath + " 500 error=" + e.message + " " + (Date.now() - t0) + "ms",
          );
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
      // BUG N5: Dynamically fetch workflow list instead of hardcoded IDs
      let workflowList = "";
      try {
        const cache = await refreshWorkflowCache();
        const entries = Object.entries(cache);
        if (entries.length > 0) {
          workflowList = entries
            .map(([name, id]) => "  - " + name + " (ID: " + id + ")")
            .join("\n");
        } else {
          workflowList = "  (no workflows found - use n8n_create_workflow to create one)";
        }
      } catch (e) {
        workflowList = "  (could not fetch workflows: " + e.message + ")";
      }

      return {
        prependContext:
          "[N8N] n8n Pipeline Manager active. Architecture: n8n handles 95% deterministic work, you handle 5% edge cases.\n" +
          "\n" +
          "DEPLOYED WORKFLOWS (live from n8n, use name or ID with any tool):\n" +
          workflowList +
          "\n" +
          "\n" +
          "WEBHOOK ENDPOINTS (all POST, auth=gateway token):\n" +
          "\n" +
          "/webhook/outreach-pipeline\n" +
          "  Actions: check_response_signals, check_landing_signups, check_followups_due, draft_followups, send_alert, pipeline_status\n" +
          "  CRM DB: /app/.openclaw/data/outreach.db (4 lanes: builder/buyer/connector/investor)\n" +
          "\n" +
          "/webhook/narrowcast-pipeline\n" +
          "  Actions: scan_communities, evaluate_and_source\n" +
          "  Data: narrowcast_scans + narrowcast_threads tables in outreach.db\n" +
          "\n" +
          "/webhook/pilot-pipeline\n" +
          "  Actions: check_pilot_repos, check_evidence_bundles, generate_pilot_report\n" +
          "\n" +
          "/webhook/morning-brief\n" +
          "  Actions: gather_data, format_brief, deliver_brief\n" +
          "\n" +
          "STUBS REMAINING (INT-2): draft_followups (AI drafting), evaluate_and_source (AI eval), send_alert (Slack/Discord delivery).\n" +
          "Tools accept workflow name OR ID. Names are resolved dynamically (cache TTL: 5min).",
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
