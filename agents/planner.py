"""PlannerAgent — decomposes tasks into ordered subtasks."""

import re
from typing import Optional

from providers.base import BaseProvider, ProviderResponse


class PlannerAgent:
    """
    Breaks a complex task into clear, ordered subtasks.

    Uses the configured LLM provider to analyze the task and produce
    a structured decomposition plan.
    """

    def __init__(self, provider: BaseProvider, config: Optional[dict] = None):
        self.provider = provider
        self.config = config or {}
        self.max_subtasks = self.config.get("max_subtasks", 8)
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are a planning agent. Break the given task into clear, ordered subtasks. "
            "Return each subtask on a new line, prefixed with its number.",
        )

    async def plan(self, task: str) -> list[str]:
        """Analyze task and return list of subtasks."""
        prompt = (
            f"Task: {task}\n\n"
            f"Break this into at most {self.max_subtasks} concrete, ordered subtasks. "
            "Return ONLY the numbered list, nothing else."
        )

        response: ProviderResponse = await self.provider.complete(
            prompt=prompt, system=self.system_prompt
        )

        subtasks = self._parse_subtasks(response.content)
        return subtasks

    @staticmethod
    def _parse_subtasks(text: str) -> list[str]:
        """Extract numbered subtasks from LLM response."""
        subtasks = []
        for line in text.strip().splitlines():
            line = line.strip()
            # Match: "1. Do thing" or "1) Do thing" or "- Do thing"
            match = re.match(r"^(?:\d+[\.\)]\s*|[-*]\s*)(.+)", line)
            if match:
                subtasks.append(match.group(1).strip())
        return subtasks if subtasks else [text.strip()]

    def mock_plan(self, task: str) -> list[str]:
        """Return realistic mock subtasks for demo mode."""
        return [
            f"Analyze requirements and constraints for: {task}",
            f"Design system architecture and data flow",
            f"Implement core logic and business rules",
            f"Build API endpoints and request handling",
            f"Add input validation and error handling",
            f"Write unit and integration tests",
            f"Document API and usage examples",
        ]
