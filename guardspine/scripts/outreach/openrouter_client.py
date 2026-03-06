"""
OpenRouter API Client for Content Pipeline

Provides a unified interface for LLM calls via OpenRouter API.
Used by weekly_zeitgeist_analysis.py and dashboard pipelines.

Environment Variables:
    OPENROUTER_API_KEY: Your OpenRouter API key
    OPENROUTER_MODEL: Default model (default: anthropic/claude-3.5-sonnet)

Usage:
    from openrouter_client import get_client
    client = get_client()
    response = await client.generate("prompt", "system", max_tokens=2000)
"""

import os
import asyncio
import aiohttp
import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"  # Cost-effective default


class OpenRouterClient:
    """
    Async client for OpenRouter API.

    Supports all OpenRouter models with unified interface.
    Falls back to local CLI if API key not configured.
    """

    # Retry configuration (PIP-008)
    MAX_RETRIES = 3
    RETRY_STATUS_CODES = {429, 500, 502, 503, 504}  # Rate limit and server errors
    BASE_RETRY_DELAY = 1.0  # seconds

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        site_url: str = "https://github.com/DNYoussef/context-cascade",
        site_name: str = "Life OS Content Pipeline"
    ):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model = model or os.getenv("OPENROUTER_MODEL", DEFAULT_MODEL)
        self.site_url = site_url
        self.site_name = site_name

        if not self.api_key:
            logger.warning(
                "OPENROUTER_API_KEY not set. "
                "Will fall back to local CLI execution."
            )

    async def generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        model: Optional[str] = None
    ) -> str:
        """
        Generate completion via OpenRouter API.

        Args:
            prompt: User prompt
            system: System message (optional)
            max_tokens: Max tokens to generate
            temperature: Sampling temperature
            model: Override default model

        Returns:
            Generated text response
        """
        if not self.api_key:
            return await self._fallback_generate(prompt, system, max_tokens)

        use_model = model or self.model

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": use_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.site_name
        }

        # PIP-008: Retry with exponential backoff for transient errors
        last_error = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        OPENROUTER_API_URL,
                        json=payload,
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=180)
                    ) as response:
                        if response.status == 200:
                            data = await response.json()
                            return data["choices"][0]["message"]["content"]

                        # Check if error is retryable
                        if response.status in self.RETRY_STATUS_CODES and attempt < self.MAX_RETRIES:
                            error_text = await response.text()
                            delay = self.BASE_RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                            logger.warning(
                                f"OpenRouter API {response.status} (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), "
                                f"retrying in {delay}s: {error_text[:100]}"
                            )
                            await asyncio.sleep(delay)
                            continue

                        # Non-retryable error or max retries exceeded
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error {response.status}: {error_text}")
                        return await self._fallback_generate(prompt, system, max_tokens)

            except asyncio.TimeoutError:
                last_error = "timeout"
                if attempt < self.MAX_RETRIES:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"OpenRouter API timeout (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {delay}s")
                    await asyncio.sleep(delay)
                    continue
                logger.error("OpenRouter API timeout after all retries")
                return await self._fallback_generate(prompt, system, max_tokens)

            except Exception as e:
                last_error = str(e)
                if attempt < self.MAX_RETRIES:
                    delay = self.BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"OpenRouter API error (attempt {attempt + 1}/{self.MAX_RETRIES + 1}), retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"OpenRouter API error after all retries: {e}")
                return await self._fallback_generate(prompt, system, max_tokens)

        # Shouldn't reach here, but fallback just in case
        logger.error(f"OpenRouter API failed after {self.MAX_RETRIES + 1} attempts: {last_error}")
        return await self._fallback_generate(prompt, system, max_tokens)

    async def _fallback_generate(
        self,
        prompt: str,
        system: str = "",
        max_tokens: int = 2000
    ) -> str:
        """
        Fallback to local CLI execution when API unavailable.
        Uses Claude Code CLI or returns structured placeholder.
        """
        import subprocess

        logger.info("Using local CLI fallback for generation")

        combined_prompt = prompt
        if system:
            combined_prompt = f"[System: {system}]\n\n{prompt}"

        try:
            # Try Claude Code CLI
            result = subprocess.run(
                ["claude", "-p", combined_prompt[:15000]],
                capture_output=True,
                text=True,
                timeout=180,
                encoding='utf-8',
                errors='replace'
            )

            if result.returncode == 0 and result.stdout.strip():
                return result.stdout

        except FileNotFoundError:
            pass
        except subprocess.TimeoutExpired:
            logger.warning("Claude CLI timeout")
        except Exception as e:
            logger.warning(f"Claude CLI error: {e}")

        # Return structured placeholder indicating fallback mode
        return json.dumps({
            "status": "fallback_mode",
            "message": "OpenRouter API not configured and local CLI unavailable",
            "prompt_length": len(prompt),
            "timestamp": datetime.now().isoformat(),
            "suggestion": "Set OPENROUTER_API_KEY environment variable"
        })


# Singleton instance
_client: Optional[OpenRouterClient] = None


def get_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> OpenRouterClient:
    """
    Get OpenRouter client instance (singleton).

    Args:
        api_key: Override API key (optional)
        model: Override default model (optional)

    Returns:
        OpenRouterClient instance
    """
    global _client

    if _client is None or api_key or model:
        _client = OpenRouterClient(api_key=api_key, model=model)

    return _client


# Convenience function for quick calls
async def generate(
    prompt: str,
    system: str = "",
    max_tokens: int = 2000,
    model: Optional[str] = None
) -> str:
    """
    Quick generation without explicit client creation.

    Args:
        prompt: User prompt
        system: System message
        max_tokens: Max tokens
        model: Model override

    Returns:
        Generated text
    """
    client = get_client()
    return await client.generate(prompt, system, max_tokens, model=model)
