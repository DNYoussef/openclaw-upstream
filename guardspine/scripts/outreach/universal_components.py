"""Universal component wiring for content-pipeline."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from library.components.cognitive_architecture.integration.telemetry_bridge import TelemetryBridge
from library.components.memory.memory_mcp_client import create_memory_mcp_client
from library.components.observability.tagging_protocol import TaggingProtocol, create_simple_tagger
from library.components.utilities.quality_gate import GateManager


def init_tagger() -> TaggingProtocol:
    return create_simple_tagger(agent_id="content-pipeline", project_id="content-pipeline")


def init_memory_client():
    endpoint = os.getenv("MEMORY_MCP_URL", "http://localhost:3000")
    return create_memory_mcp_client(
        project_id="content-pipeline",
        project_name="content-pipeline",
        agent_id="content-pipeline",
        agent_category="orchestration",
        capabilities=["content-pipeline", "analysis"],
        mcp_endpoint=endpoint,
    )


def init_telemetry_bridge(loop_dir: Optional[str] = None) -> TelemetryBridge:
    resolved = Path(loop_dir) if loop_dir else Path(".loop")
    return TelemetryBridge(loop_dir=resolved)


def init_gate_manager() -> GateManager:
    return GateManager()

