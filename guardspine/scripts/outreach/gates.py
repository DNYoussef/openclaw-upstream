#!/usr/bin/env python3
"""
Pipeline Gates Module
=====================
Explicit synchronization and quality gates for pipeline orchestration.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List

import sys
from pathlib import Path
# Add lib to path for quality_gate imports
_lib_path = Path(__file__).parent / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))

from library.components.utilities.quality_gate import (
    GateConfig,
    GateManager,
    GateResult,
    GateStatus,
    GateType,
    RichMetricResult,
    create_compile_gate,
    create_dependency_gate,
    create_quality_gate,
    create_sync_gate,
)

logger = logging.getLogger(__name__)


async def llm_coherence_metric(agent_analyses: Dict[str, str], skill_client: Any) -> float:
    """
    Calculates a coherence score (0.0-1.0) between multiple agent analyses using an LLM.
    Returns a RichMetricResult which behaves like a float but contains feedback.
    """
    if not agent_analyses:
        return 0.0

    prompt_parts = [
        "You are an expert evaluator of AI agent coherence. Your task is to analyze multiple independent analyses of the same content and determine their semantic coherence.",
        "Assess the semantic similarity, consistency, and identify any direct contradictions or significant divergences in perspective.",
        "Provide a single numerical coherence score between 0.0 (completely incoherent, full of contradictions) and 1.0 (perfectly coherent, highly aligned), along with a brief explanation.",
        "\n--- ANALYSES ---\n",
    ]

    for agent_name, analysis_content in agent_analyses.items():
        prompt_parts.append(f"AGENT: {agent_name}\nANALYSIS:\n{str(analysis_content)[:2000]}\n")

    prompt_parts.append("\n--- END ANALYSES ---\n")
    prompt_parts.append("Respond ONLY with a JSON object containing 'coherence_score' (float) and 'explanation' (string).")

    coherence_prompt = "\n".join(prompt_parts)

    try:
        response_json_str = await skill_client.generate(
            coherence_prompt,
            system="You are a strict JSON-only API that evaluates semantic coherence.",
        )

        response_data = json.loads(response_json_str)
        score = response_data.get("coherence_score")
        explanation = response_data.get("explanation", "No explanation provided.")

        if score is not None and isinstance(score, (int, float)):
            return RichMetricResult(float(score), explanation)

        logger.warning(
            "LLM coherence metric: Could not extract valid coherence_score from response: %s",
            response_json_str,
        )
        return RichMetricResult(0.0, "Failed to extract score.")
    except json.JSONDecodeError as exc:
        logger.error("Error decoding JSON from LLM response in coherence metric: %s", exc)
        return RichMetricResult(0.0, f"JSON Error: {str(exc)}")
    except Exception as exc:
        logger.error("Error calling LLM for coherence metric: %s", exc)
        return RichMetricResult(0.0, f"Error: {str(exc)}")


# ============================================
# CONTENT PIPELINE SPECIFIC GATES
# ============================================

def create_content_pipeline_gates() -> List:
    """Create all gates for the content pipeline. Returns List[QualityGate]."""
    return [
        create_sync_gate(
            "gate_transcription",
            wait_for=[],
        ),
        create_sync_gate(
            "gate_individual_analysis",
            wait_for=[],
        ),
        create_sync_gate(
            "gate_zeitgeist",
            wait_for=["gemini_zeitgeist", "codex_zeitgeist", "claude_zeitgeist"],
        ),
        create_dependency_gate(
            "gate_debate",
            requires=["byzantine_debate"],
        ),
        create_dependency_gate(
            "gate_implications",
            requires=["second_order_implications", "third_order_implications"],
        ),
        create_quality_gate(
            "gate_style",
            metric_fn=None,
            threshold=0.7,
        ),
        create_quality_gate(
            "gate_slop",
            metric_fn=None,
            threshold=0.7,
        ),
        create_quality_gate(
            "gate_image",
            metric_fn=None,
            threshold=0.7,
        ),
        create_compile_gate(
            "gate_publish",
            checks=[],
        ),
    ]


if __name__ == "__main__":
    async def demo():
        manager = GateManager()

        gate = create_sync_gate("test_sync", wait_for=["task1", "task2"])
        manager.register_gate(gate)

        manager.mark_task_complete("task1", {"result": "done"})

        result: GateResult = await manager.check_gate("test_sync")
        print(f"Gate result: {result.status.value} - {result.message}")

        manager.mark_task_complete("task2", {"result": "done"})
        result = await manager.check_gate("test_sync")
        print(f"Gate result: {result.status.value} - {result.message}")

    asyncio.run(demo())
