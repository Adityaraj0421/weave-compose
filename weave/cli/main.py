"""Typer CLI entry point for the Weave composition engine."""

import logging

import typer

from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.registry import SkillRegistry
from weave.core.selector import WeaveSelector

logger = logging.getLogger(__name__)

app = typer.Typer(
    name="weave",
    help="Platform-aware skill composition layer for AI coding tools.",
    add_completion=False,
)

SESSION_FILE: str = ".weave_session.json"


def _get_adapter(platform: str) -> BaseAdapter:
    """Return the adapter instance for the given platform identifier.

    Args:
        platform: Platform string, e.g. ``"claude_code"``.

    Returns:
        A concrete BaseAdapter subclass for the requested platform.

    Raises:
        typer.Exit: With exit code 1 if the platform is not supported.
    """
    if platform == "claude_code":
        return ClaudeCodeAdapter()
    typer.echo(
        f"Error: unsupported platform {platform!r}. Supported: claude_code",
        err=True,
    )
    raise typer.Exit(code=1)


@app.command()
def load(
    path: str = typer.Argument(..., help="Path to directory containing skill files"),
    platform: str = typer.Option(
        "claude_code",
        "--platform",
        "-p",
        help="Platform adapter to use: claude_code (default)",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Print each loaded skill name and capability count",
    ),
) -> None:
    """Load skills from a directory and save the session for later queries."""
    adapter = _get_adapter(platform)

    try:
        skills = adapter.load(path)
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    registry = SkillRegistry()
    for skill in skills:
        registry.register(skill)

    registry.save_session(SESSION_FILE)

    typer.echo(f"Loaded {len(skills)} skill(s) from {path} (platform: {platform})")
    typer.echo(f"Session saved to {SESSION_FILE}")

    if verbose:
        for skill in skills:
            typer.echo(f"  {skill.name} ({len(skill.capabilities)} capabilities)")


@app.command()
def query(
    text: str = typer.Argument(..., help="Natural language query to match skills"),
    explain: bool = typer.Option(
        False,
        "--explain",
        help="Print similarity scores for all loaded skills",
    ),
    top: int = typer.Option(
        1,
        "--top",
        "-n",
        help="Minimum number of top skills to return",
    ),
) -> None:
    """Query loaded skills and return the best match(es) for the given text."""
    if explain:
        logging.basicConfig(level=logging.INFO)

    registry = SkillRegistry()
    registry.load_session(SESSION_FILE)

    if registry.count() == 0:
        typer.echo(
            "No skills loaded. Run `weave load <path>` first.", err=True
        )
        raise typer.Exit(code=1)

    selector = WeaveSelector()
    results = selector.select(text, registry, top_n=top, explain=explain)

    if not results:
        typer.echo("No matching skills found.")
        return

    for i, (skill, score) in enumerate(results, start=1):
        typer.echo(f"\n[{i}] {skill.name} ({skill.platform}) — score: {score:.4f}")
        typer.echo(f"    {skill.trigger_context}")
