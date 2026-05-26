"""Xiaomi MiMo API provider — primary recommended provider."""

import os
from typing import Optional

import httpx

from .base import BaseProvider, ProviderResponse


class MimoProvider(BaseProvider):
    """
    Xiaomi MiMo API provider.

    MiMo-7B delivers strong reasoning and code generation performance
    at a fraction of the cost of larger models. OpenAI-compatible API
    makes integration seamless.

    Set MIMO_API_KEY environment variable to use.
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", "MIMO_API_KEY"), "")

    async def complete(self, prompt: str, system: Optional[str] = None) -> ProviderResponse:
        """Call MiMo API with the given prompt."""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            data = resp.json()

        choice = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})
        return ProviderResponse(
            content=choice,
            model=self.model,
            tokens_used=usage.get("total_tokens", 0),
            provider_name="mimo",
        )

    async def health_check(self) -> bool:
        if not self.api_key:
            return False
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                return resp.status_code == 200
        except Exception:
            return False
