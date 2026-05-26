"""MiMo Multi-Agent — CLI entry point."""

import argparse
import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.text import Text
from rich.table import Table

from orchestrator import Orchestrator, OrchestratorResult

console = Console()

BANNER = r"""
[bold cyan]╔══════════════════════════════════════════╗
║   🤖 MiMo Multi-Agent Framework  v1.0   ║
║   Powered by Xiaomi MiMo                 ║
╚══════════════════════════════════════════╝[/bold cyan]
"""


def print_banner():
    console.print(BANNER)


def print_plan(subtasks: list[str]):
    table = Table(title="📋 Execution Plan", show_lines=True, border_style="cyan")
    table.add_column("#", style="bold", width=3)
    table.add_column("Subtask", style="white")
    for i, st in enumerate(subtasks, 1):
        table.add_row(str(i), st)
    console.print(table)
    console.print()


def print_result(result: OrchestratorResult):
    console.print(Rule("[bold green]Results[/bold green]"))

    for i, (subtask, output, (approved, feedback)) in enumerate(
        zip(result.subtasks, result.outputs, result.reviews), 1
    ):
        status = "[bold green]✅ APPROVED[/bold green]" if approved else "[bold red]❌ REVISE[/bold red]"
        panel_title = f"Step {i}: {subtask[:60]}{'...' if len(subtask) > 60 else ''}  {status}"
        console.print(Panel(Markdown(output), title=panel_title, border_style="green" if approved else "red"))
        if feedback:
            console.print(f"  [dim]Feedback: {feedback}[/dim]")
        console.print()

    # Summary
    total = len(result.subtasks)
    approved_count = sum(1 for a, _ in result.reviews if a)
    status_style = "bold green" if result.success else "bold yellow"
    summary = f"Tasks: {total} | Approved: {approved_count}/{total} | Status: {'✅ ALL PASSED' if result.success else '⚠️  SOME NEED REVISION'}"
    console.print(Panel(Text(summary, style=status_style), border_style="cyan"))


async def run_live(task: str, demo: bool):
    """Run orchestration with live spinners."""
    config_path = "config.yaml"
    try:
        orch = Orchestrator(config_path)
    except FileNotFoundError:
        console.print("[yellow]config.yaml not found, using defaults[/yellow]")
        config_path = None

    if demo:
        console.print("[dim]Running in demo mode (mock outputs, no API key needed)[/dim]\n")
        with Live(Spinner("dots", text=" Planning task..."), console=console, refresh_per_second=10):
            import time
            time.sleep(1)
        if config_path:
            orch = Orchestrator(config_path)
            result = orch.run_mock(task)
        else:
            from agents.planner import PlannerAgent
            from agents.executor import ExecutorAgent
            from agents.reviewer import ReviewerAgent
            from providers.mimo_provider import MimoProvider

            planner = PlannerAgent(MimoProvider({"model": "MiMo-7B"}))
            executor = ExecutorAgent(MimoProvider({"model": "MiMo-7B"}))
            reviewer = ReviewerAgent(MimoProvider({"model": "MiMo-7B"}))

            result = OrchestratorResult(task=task)
            result.subtasks = planner.mock_plan(task)
            for i, st in enumerate(result.subtasks):
                out = executor.mock_execute(st, i)
                app, fb = reviewer.mock_review(st, out)
                result.outputs.append(out)
                result.reviews.append((app, fb))
            result.success = all(a for a, _ in result.reviews)

        print_plan(result.subtasks)
        print_result(result)
    else:
        with Live(Spinner("dots", text=" Running multi-agent pipeline via MiMo..."), console=console, refresh_per_second=10):
            result = await orch.run(task)
        print_plan(result.subtasks)
        print_result(result)


def main():
    parser = argparse.ArgumentParser(
        description="MiMo Multi-Agent Framework — multi-agent AI orchestration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python main.py --demo\n"
               '  python main.py "Build a chat server"\n'
               "  python main.py --demo --task 'Design a recommendation engine'\n",
    )
    parser.add_argument("task", nargs="?", default=None, help="Task to execute")
    parser.add_argument("--demo", action="store_true", help="Run with mock outputs (no API key needed)")
    parser.add_argument("--task", dest="task_flag", default=None, help="Task (alternative to positional)")

    args = parser.parse_args()
    task = args.task or args.task_flag

    if not task:
        task = "Build a REST API with authentication, rate limiting, and comprehensive test coverage"

    print_banner()

    if not args.demo:
        console.print("[yellow]Tip: Use --demo for mock mode (no API key needed)[/yellow]\n")

    asyncio.run(run_live(task, demo=args.demo))


if __name__ == "__main__":
    main()
