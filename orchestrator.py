"""Orchestrator — chains Planner → Executor → Reviewer agents."""

from dataclasses import dataclass, field

import yaml

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.reviewer import ReviewerAgent
from providers.base import BaseProvider
from providers.mimo_provider import MimoProvider
from providers.openai_provider import OpenAIProvider

PROVIDER_REGISTRY = {
    "mimo": MimoProvider,
    "openai": OpenAIProvider,
    "deepseek": OpenAIProvider,
    "claude": OpenAIProvider,
}


@dataclass
class OrchestratorResult:
    """Result of a full orchestration run."""
    task: str
    subtasks: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    reviews: list[tuple[bool, str]] = field(default_factory=list)
    success: bool = False


class Orchestrator:
    """
    Multi-agent orchestrator.

    Flow: Task → Planner → [Executor → Reviewer]×N → Result
    """

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.orchestrator_cfg = self.config.get("orchestrator", {})
        self.provider = self._build_provider()
        self.max_retries = self.orchestrator_cfg.get("max_retries", 2)

        agent_cfg = self.config.get("agents", {})
        self.planner = PlannerAgent(self.provider, agent_cfg.get("planner", {}))
        self.executor = ExecutorAgent(self.provider, agent_cfg.get("executor", {}))
        self.reviewer = ReviewerAgent(self.provider, agent_cfg.get("reviewer", {}))

    def _build_provider(self) -> BaseProvider:
        """Instantiate the primary provider from config."""
        primary = self.config.get("providers", {}).get("primary", "mimo")
        configs = self.config.get("providers", {}).get("configs", {})
        provider_cfg = configs.get(primary, {})
        provider_cls = PROVIDER_REGISTRY.get(primary, MimoProvider)
        return provider_cls(provider_cfg)

    async def run(self, task: str) -> OrchestratorResult:
        """Execute full orchestration pipeline."""
        result = OrchestratorResult(task=task)

        # Plan
        result.subtasks = await self.planner.plan(task)

        # Execute + Review each subtask
        context_parts = []
        for i, subtask in enumerate(result.subtasks):
            context = "\n---\n".join(context_parts[-3:])  # last 3 as context
            output = await self.executor.execute(subtask, context)
            approved, feedback = await self.reviewer.review(subtask, output)

            # Retry if not approved
            retries = 0
            while not approved and retries < self.max_retries:
                retries += 1
                output = await self.executor.execute(
                    f"{subtask}\n\nPrevious attempt feedback: {feedback}", context
                )
                approved, feedback = await self.reviewer.review(subtask, output)

            result.outputs.append(output)
            result.reviews.append((approved, feedback))
            context_parts.append(output)

        result.success = all(approved for approved, _ in result.reviews)
        return result

    def run_mock(self, task: str) -> OrchestratorResult:
        """Run full pipeline with mock outputs for demo mode."""
        result = OrchestratorResult(task=task)
        result.subtasks = self.planner.mock_plan(task)

        context_parts = []
        for i, subtask in enumerate(result.subtasks):
            output = self.executor.mock_execute(subtask, i)
            approved, feedback = self.reviewer.mock_review(subtask, output)
            result.outputs.append(output)
            result.reviews.append((approved, feedback))
            context_parts.append(output)

        result.success = all(approved for approved, _ in result.reviews)
        return result
