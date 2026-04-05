"""Typer CLI entry point for the Weave composition engine."""

import logging

import typer

from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.registry import SkillRegistry

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
