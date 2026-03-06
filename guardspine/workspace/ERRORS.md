# ERRORS.md - Known Error Patterns and Fixes

## Format: [SYMPTOM] -> [ROOT CAUSE] -> [FIX]

### OpenClaw

- `EACCES on /data/.openclaw` -> Railway volume mounts as root, container runs as node -> Custom Dockerfile with root entrypoint + chown + su-exec drop
- `--force requires lsof` -> lsof not available on Windows -> Kill node processes manually before gateway restart
- `config validation warns about guardspine keys` -> Cosmetic warning, plugin loads fine -> Ignore
- `INVALID_ARGUMENT (400) Thought signature` -> Ollama models don't support think parameter -> Set reasoning:false for all Ollama models

### GuardSpine

- `Council result signature invalid` -> Using dev fallback key instead of production key -> Set GUARDSPINE_COUNCIL_KEY env var + GUARDSPINE_REQUIRE_COUNCIL_KEY=1
- `Nonce already used (replay attack)` false positive -> Race condition in multi-threaded nonce check -> Added threading.Lock to \_invalidate_nonce

### Railway

- `502 Bad Gateway on healthcheck` -> Container not binding to 0.0.0.0 or wrong PORT -> Verify PORT env var matches listen port, bind to 0.0.0.0
- `railway variables set silently fails` -> MSYS path conversion mangling arguments -> Prefix with MSYS_NO_PATHCONV=1

### Memory MCP

- `ChromaDB 0 collections at chroma_data/` -> Wrong path, actual data at chroma/ -> Use ~/.claude/memory-mcp-data/chroma (not chroma_data)

### Python

- `python3: command not found` (exit 127) -> Windows bash doesn't have python3 -> Always use `python` on Windows
- `dict.get("key", default) returns None` -> Key exists but value IS None -> Use `dict.get("key") or default_value`
- `yaml.safe_load returns None` -> Empty YAML file -> Always use `yaml.safe_load(f) or {}`
