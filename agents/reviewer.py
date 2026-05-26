"""ReviewerAgent — reviews executor outputs for quality."""

from typing import Optional

from providers.base import BaseProvider, ProviderResponse


class ReviewerAgent:
    """
    Reviews subtask outputs for correctness, completeness, and quality.

    Returns either APPROVED or REVISE with specific feedback.
    """

    def __init__(self, provider: BaseProvider, config: Optional[dict] = None):
        self.provider = provider
        self.config = config or {}
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are a review agent. Evaluate the output for correctness, completeness, "
            "and quality. Return APPROVED if the output meets standards, or REVISE with "
            "specific feedback.",
        )

    async def review(self, subtask: str, output: str) -> tuple[bool, str]:
        """
        Review an executor's output.

        Returns:
            (approved: bool, feedback: str)
        """
        prompt = (
            f"Subtask: {subtask}\n\n"
            f"Output to review:\n{output}\n\n"
            "Respond with APPROVED or REVISE: <feedback>"
        )

        response: ProviderResponse = await self.provider.complete(
            prompt=prompt, system=self.system_prompt
        )

        text = response.content.strip()
        approved = text.upper().startswith("APPROVED")
        feedback = text if not approved else ""
        return approved, feedback

    def mock_review(self, subtask: str, output: str) -> tuple[bool, str]:
        """Return mock review result for demo mode — always approves."""
        return True, "Output meets quality standards. Well-structured and complete."
