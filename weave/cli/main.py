"""Typer CLI entry point for the Weave composition engine."""

import json
import logging
from pathlib import Path

import typer

from weave.cli.query_command import query as _query_command
from weave.cli.run_command import run as _run_command
from weave.cli.serve_command import serve as _serve_command
from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.detector import detect_platform
from weave.core.persistent_registry import PersistentRegistry
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
    persist: bool = typer.Option(
        False,
        "--persist",
        help="Persist skills to ChromaDB (requires: pip install weave-compose[persist])",
    ),
) -> None:
    """Load skills from a directory and save the session for later queries."""
    adapter = _get_adapter(platform)

    try:
        skills = adapter.load(path)
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    registry: SkillRegistry = PersistentRegistry() if persist else SkillRegistry()
    for skill in skills:
        registry.register(skill)

    dep_count = sum(len(registry.resolve_dependencies(s)) for s in skills)

    registry.save_session(SESSION_FILE)

    typer.echo(f"Loaded {len(skills)} skill(s) from {path} (platform: {platform})")
    if dep_count > 0:
        typer.echo(f"  Resolved {dep_count} dependency link(s)")
    typer.echo(f"Session saved to {SESSION_FILE}")
    if persist:
        typer.echo("Skills persisted to ChromaDB at ./chroma")

    if verbose:
        for skill in skills:
            typer.echo(f"  {skill.name} ({len(skill.capabilities)} capabilities)")


@app.command(name="list")
def list_skills(
    platform: str | None = typer.Option(
        None,
        "--platform",
        "-p",
        help="Filter by platform: claude_code, cursor, codex, windsurf",
    ),
) -> None:
    """List all skills loaded in the current session."""
    registry = SkillRegistry()
    registry.load_session(SESSION_FILE)

    skills = (
        registry.get_by_platform(platform) if platform is not None else registry.get_all()
    )

    if not skills:
        suffix = f" for platform {platform!r}" if platform else ""
        typer.echo(f"No skills loaded{suffix}. Run `weave load <path>` first.")
        return

    for skill in skills:
        caps = ", ".join(skill.capabilities[:3])
        if len(skill.capabilities) > 3:
            caps += "..."
        typer.echo(f"  {skill.name:<30} {skill.platform:<15} [{caps}]")

    typer.echo(f"\nTotal: {len(skills)} skill(s)")


@app.command()
def status() -> None:
    """Show registry status: skill count, platform breakdown, and session info."""
    registry = SkillRegistry()
    registry.load_session(SESSION_FILE)

    total = registry.count()
    typer.echo(f"Skills loaded:   {total}")

    if total > 0:
        platforms: dict[str, int] = {}
        for skill in registry.get_all():
            platforms[skill.platform] = platforms.get(skill.platform, 0) + 1
        for plat, count in sorted(platforms.items()):
            typer.echo(f"  {plat}: {count}")

    typer.echo("Embedding model: all-MiniLM-L6-v2")

    session_path = Path(SESSION_FILE)
    if session_path.exists():
        try:
            with open(session_path, encoding="utf-8") as fh:
                data: dict[str, object] = json.load(fh)
            saved_at = str(data.get("saved_at", "unknown"))
        except (json.JSONDecodeError, KeyError):
            saved_at = "unknown"
        typer.echo(f"Session file:    {SESSION_FILE}")
        typer.echo(f"Last saved:      {saved_at}")
    else:
        typer.echo("Session file:    not found")


@app.command()
def clear(
    persist: bool = typer.Option(
        False,
        "--persist",
        help="Also clear the ChromaDB collection",
    ),
) -> None:
    """Clear all loaded skills and delete the session file."""
    typer.confirm("Clear all loaded skills?", abort=True)
    registry: SkillRegistry = PersistentRegistry() if persist else SkillRegistry()
    registry.clear()
    Path(SESSION_FILE).unlink(missing_ok=True)
    typer.echo("Registry cleared.")


@app.command()
def detect(
    path: str = typer.Argument(..., help="Path to directory to auto-detect platform for"),
) -> None:
    """Detect the platform of a skill directory from its file structure.

    Inspects the directory at path and prints the detected platform name,
    or an informational message if no platform could be identified.

    Args:
        path: Absolute or relative path to the directory to inspect.
    """
    platform = detect_platform(path)
    if platform == "unknown":
        typer.echo("Unknown platform — could not detect from directory contents")
    else:
        typer.echo(f"Detected platform: {platform}")


app.command(name="query")(_query_command)
app.command(name="run")(_run_command)
app.command(name="serve")(_serve_command)
