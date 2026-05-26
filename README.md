# 🤖 MiMo Multi-Agent

A multi-agent orchestration framework supporting multiple AI providers, powered by **Xiaomi MiMo** as the primary recommended model.

## Overview

MiMo Multi-Agent chains specialized AI agents — **Planner**, **Executor**, **Reviewer** — through a configurable orchestrator. Each agent can use different providers: MiMo, OpenAI, Claude, DeepSeek, or any OpenAI-compatible API.

## Architecture

```
Task → [Planner Agent] → subtasks → [Executor Agent] → outputs → [Reviewer Agent] → final result
         ↓ provider                    ↓ provider                    ↓ provider
        MiMo API                      MiMo API                      MiMo API
```

## Agents

- **PlannerAgent** — Decomposes complex tasks into ordered subtasks
- **ExecutorAgent** — Executes each subtask against the configured LLM provider
- **ReviewerAgent** — Reviews executor output for quality, correctness, completeness

## Providers

| Provider | Class | Best For |
|----------|-------|----------|
| **MiMo** (recommended) | `MimoProvider` | Fast reasoning, code generation |
| OpenAI | `OpenAIProvider` | GPT-4o, general tasks |
| DeepSeek | `OpenAIProvider` | Deep reasoning (OpenAI-compatible) |
| Claude | `OpenAIProvider` | Long context, analysis |

## Quick Start

```bash
pip install -r requirements.txt

# Run demo (no API key needed)
python main.py --demo

# Run with MiMo API
export MIMO_API_KEY="your-key"
python main.py "Build a REST API with authentication"
```

## Configuration

Edit `config.yaml` to set providers, models, and agent parameters. MiMo is the default primary provider.

## Demo Mode

`--demo` runs the full multi-agent pipeline with mock outputs — no API keys required. Great for understanding the architecture.

## Why MiMo?

Xiaomi's MiMo-7B model punches above its weight class in reasoning and coding benchmarks. Its OpenAI-compatible API makes integration trivial. Fast inference + strong reasoning = ideal for multi-agent loops.

## License

MIT
