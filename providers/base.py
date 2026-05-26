"""Abstract base class for AI providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ProviderResponse:
    """Standardized response from any provider."""
    content: str
    model: str
    tokens_used: int = 0
    provider_name: str = ""


class BaseProvider(ABC):
    """Abstract base for all AI providers."""

    def __init__(self, config: dict):
        self.config = config
        self.model = config.get("model", "unknown")
        self.base_url = config.get("base_url", "")
        self.max_tokens = config.get("max_tokens", 2048)
        self.temperature = config.get("temperature", 0.7)

    @abstractmethod
    async def complete(self, prompt: str, system: Optional[str] = None) -> ProviderResponse:
        """Send prompt to the LLM and return a response."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the provider is available."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.model}>"
