from dataclasses import dataclass
from typing import Callable, Any, Dict, Optional, Union
import asyncio
import logging

logger = logging.getLogger(__name__)

@dataclass
class AuditResult:
    success: bool
    iterations: int
    output: Any
    message: str = ""
    score: float = 0.0
    # PIP-002: Add feedback field for style audit compatibility
    feedback: str = ""

async def ralph_wiggum_loop(
    generate_fn: Callable[..., Any],
    audit_fn: Callable[..., Any],
    max_iterations: int = 3,
    pass_threshold: float = 0.7,
    feedback_key: str = "feedback",
    loop_name: str = "ralph_wiggum_loop"
) -> AuditResult:
    """
    Implements the "Ralph Wiggum" iterative refinement loop.
    
    "I'm learning!" - Ralph Wiggum
    
    Cycle:
    1. Generate (Attempt 1)
    2. Audit (Quality Gate)
    3. If Pass -> Return
    4. If Fail -> Generate(feedback) -> Goto 2
    
    Args:
        generate_fn: Async function that produces content. Must accept a keyword argument 
                     matching `feedback_key` (e.g., feedback="...") for refinement.
        audit_fn: Async function that evaluates content. Returns float or object with 
                  .score (float) and optional .feedback (str).
        max_iterations: Maximum number of refinement attempts.
        pass_threshold: Score required to pass.
        feedback_key: The keyword argument name to pass feedback to generate_fn.
        loop_name: Identifier for logging.
    """
    logger.info(f"[{loop_name}] Starting Ralph Wiggum loop (Threshold: {pass_threshold})")
    
    current_output = None
    current_feedback = None
    
    for i in range(max_iterations):
        iteration_label = f"Iteration {i+1}/{max_iterations}"
        logger.info(f"[{loop_name}] {iteration_label} - Generating...")
        
        try:
            # Generate (pass feedback if not first iteration)
            if current_feedback and i > 0:
                kwargs = {feedback_key: current_feedback}
                current_output = await generate_fn(**kwargs)
            else:
                current_output = await generate_fn()
            
            # Audit
            audit_result = await audit_fn(current_output)
            
            # Handle different audit result types
            score = 0.0
            feedback_from_audit = ""
            
            if hasattr(audit_result, "score"):
                score = float(audit_result.score)
                feedback_from_audit = getattr(audit_result, "feedback", "")
            elif isinstance(audit_result, (int, float)):
                score = float(audit_result)
            else:
                logger.warning(f"[{loop_name}] Audit returned unknown type: {type(audit_result)}. Assuming 0.0.")
                score = 0.0

            logger.info(f"[{loop_name}] {iteration_label} - Score: {score:.2f} (Feedback: {feedback_from_audit[:50]}...)")
            
            # Check success
            if score >= pass_threshold:
                logger.info(f"[{loop_name}] SUCCESS at {iteration_label}")
                return AuditResult(
                    success=True,
                    iterations=i + 1,
                    output=current_output,
                    message=f"Passed at iteration {i+1} with score {score:.2f}",
                    score=score
                )
            
            # Prepare for next iteration
            if i < max_iterations - 1:
                logger.info(f"[{loop_name}] Failed. Preparing refinement...")
                if feedback_from_audit:
                    current_feedback = f"Previous attempt scored {score:.2f}. Feedback: {feedback_from_audit}"
                else:
                    current_feedback = f"Previous attempt scored {score:.2f}. Please improve quality and coherence."
            
        except Exception as e:
            logger.error(f"[{loop_name}] Error at {iteration_label}: {e}")
            # If generation fails, we might want to retry or abort. 
            # For now, we continue to next iteration if possible, or return failure if critical.
            current_feedback = f"Previous attempt failed with error: {str(e)}. Please try again."

    logger.warning(f"[{loop_name}] FAILED after {max_iterations} iterations. Returning best attempt.")
    
    return AuditResult(
        success=False,
        iterations=max_iterations,
        output=current_output,
        message=f"Failed to reach threshold {pass_threshold} after {max_iterations} iterations.",
        score=score if 'score' in locals() else 0.0
    )