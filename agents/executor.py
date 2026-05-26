"""ExecutorAgent — executes individual subtasks via LLM."""

from typing import Optional

from providers.base import BaseProvider, ProviderResponse


class ExecutorAgent:
    """
    Executes a single subtask by prompting the LLM.

    Takes a subtask description and returns the LLM's output.
    Can be chained across multiple subtasks sequentially.
    """

    def __init__(self, provider: BaseProvider, config: Optional[dict] = None):
        self.provider = provider
        self.config = config or {}
        self.system_prompt = self.config.get(
            "system_prompt",
            "You are an execution agent. Complete the given subtask thoroughly. "
            "Return clean, well-structured output.",
        )

    async def execute(self, subtask: str, context: str = "") -> str:
        """Execute a subtask and return the result."""
        prompt = subtask
        if context:
            prompt = f"Context from previous steps:\n{context}\n\nSubtask: {subtask}"

        response: ProviderResponse = await self.provider.complete(
            prompt=prompt, system=self.system_prompt
        )
        return response.content

    def mock_execute(self, subtask: str, index: int = 0) -> str:
        """Return realistic mock output for demo mode."""
        mock_outputs = [
            "**Requirements Analysis Complete**\n"
            "- Functional: REST API with CRUD operations, JWT auth, rate limiting\n"
            "- Non-functional: <100ms p99 latency, 99.9% uptime, horizontal scaling\n"
            "- Tech stack: Python/FastAPI, PostgreSQL, Redis cache layer",

            "**Architecture Design**\n"
            "```\nClient → Nginx → FastAPI → Service Layer → PostgreSQL\n                          ↓\n                      Redis Cache\n```\n"
            "- Hexagonal architecture with clean separation of concerns\n"
            "- Event-driven async processing for non-blocking I/O",

            "**Core Implementation**\n"
            "```python\nclass UserService:\n    def __init__(self, repo: UserRepository, cache: CacheService):\n        self.repo = repo\n        self.cache = cache\n\n    async def get_user(self, user_id: str) -> User:\n        cached = await self.cache.get(f\"user:{user_id}\")\n        if cached:\n            return User.parse_raw(cached)\n        user = await self.repo.find_by_id(user_id)\n        await self.cache.set(f\"user:{user_id}\", user.json(), ttl=300)\n        return user\n```",

            "**API Endpoints Built**\n"
            "| Method | Path | Description |\n|--------|------|-------------|\n"
            "| POST | /auth/register | Create account |\n"
            "| POST | /auth/login | Get JWT token |\n"
            "| GET | /users/{id} | Fetch user profile |\n"
            "| PUT | /users/{id} | Update profile |\n"
            "| DELETE | /users/{id} | Soft-delete account |",

            "**Validation & Error Handling**\n"
            "- Pydantic models enforce request schema validation\n"
            "- Custom exception handlers return structured JSON errors\n"
            "- Rate limiter: 100 req/min per API key, 10 req/min for auth endpoints\n"
            "- All errors logged with correlation IDs for tracing",

            "**Tests Written**\n"
            "- 24 unit tests covering service layer (all passing)\n"
            "- 12 integration tests with test database fixtures\n"
            "- Load test: 500 concurrent users, p95=87ms, p99=142ms\n"
            "- Coverage: 94% lines, 89% branches",

            "**Documentation Complete**\n"
            "- OpenAPI spec auto-generated from FastAPI decorators\n"
            "- README with setup instructions, env vars, deployment guide\n"
            "- Example curl commands for all endpoints\n"
            "- Architecture decision records (ADRs) for key design choices",
        ]
        return mock_outputs[index % len(mock_outputs)]
