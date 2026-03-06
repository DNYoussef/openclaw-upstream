
import asyncio
import logging
from typing import Dict, Any
from gates import llm_coherence_metric

# Mock SkillHookClient
class MockSkillHookClient:
    async def generate(self, prompt: str, system: str = "") -> str:
        # Simple heuristic mock: 
        # If the prompt contains "INCOHERENT", return a low score.
        # Otherwise return a high score.
        print(f"\n[MockClient] Received prompt length: {len(prompt)}")
        
        if "INCOHERENT" in prompt:
            return '{"coherence_score": 0.2, "explanation": "Analyses are contradictory."}'
        else:
            return '{"coherence_score": 0.9, "explanation": "Analyses are highly aligned."}'

async def main():
    logging.basicConfig(level=logging.INFO)
    client = MockSkillHookClient()

    print("--- Test 1: Coherent Analyses ---")
    coherent_analyses = {
        "Agent A": "AI is advancing rapidly. Transformers are key.",
        "Agent B": "The pace of AI progress is fast, largely due to transformer architecture."
    }
    score1 = await llm_coherence_metric(coherent_analyses, client)
    print(f"Score 1: {score1}")

    print("\n--- Test 2: Incoherent Analyses ---")
    # We inject the trigger word "INCOHERENT" into the content for the mock to pick up
    incoherent_analyses = {
        "Agent A": "AI is advancing rapidly. INCOHERENT data.",
        "Agent B": "AI stagnation is evident. Nothing is happening."
    }
    score2 = await llm_coherence_metric(incoherent_analyses, client)
    print(f"Score 2: {score2}")

if __name__ == "__main__":
    asyncio.run(main())
