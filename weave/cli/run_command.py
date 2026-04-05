"""Interactive query loop command for the Weave composition engine."""

import logging
import readline  # noqa: F401 — imported for side-effect: enables line editing in input()

import typer

from weave.cli.config import load_config
from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.composer import WeaveComposer
from weave.core.registry import SkillRegistry
from weave.core.selector import WeaveSelector

logger = logging.getLogger(__name__)


def _resolve_adapter(platform: str) -> BaseAdapter:
    """Return the adapter instance for the given platform identifier.

    Kept local to avoid a circular import between run_command and main.

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


def run(
    config: str = typer.Option(
        "weave.yaml",
        "--config",
        "-c",
        help="Path to weave.yaml config file (default: ./weave.yaml)",
    ),
) -> None:
    """Load skills from weave.yaml and start an interactive query loop.

    Reads the config file, loads all skill directories listed under
    ``skills:``, registers them in the session registry, then enters a
    readline-powered input loop. Each line entered is treated as a
    natural-language query; the best matching skill(s) and their composed
    context are printed. Press Ctrl+C or Ctrl+D to exit.

    Args:
        config: Path to the weave.yaml config file.
    """
    try:
        cfg = load_config(config)
    except FileNotFoundError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    except ValueError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    registry = SkillRegistry()
    total_loaded = 0

    for entry in cfg.skills:
        adapter = _resolve_adapter(entry.platform)
        try:
            skills = adapter.load(entry.path)
        except FileNotFoundError as exc:
            typer.echo(f"Warning: skipping {entry.path!r} — {exc}", err=True)
            continue
        for skill in skills:
            registry.register(skill)
        total_loaded += len(skills)

    if registry.count() == 0:
        typer.echo(
            "Error: no skills loaded. Check the paths in your weave.yaml.", err=True
        )
        raise typer.Exit(code=1)

    typer.echo(
        f"Loaded {total_loaded} skill(s) from {len(cfg.skills)} source(s). Ready."
    )
    typer.echo("Type a query to find the best skill. Ctrl+C or Ctrl+D to exit.\n")

    selector = WeaveSelector()
    composer = WeaveComposer()

    while True:
        try:
            line = input("weave> ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if not line:
            continue

        results = selector.select(
            line,
            registry,
            top_n=1,
            confidence_threshold=cfg.composition.confidence_threshold,
            max_active_skills=cfg.composition.max_active_skills,
            explain=cfg.output.explain,
        )

        if not results:
            typer.echo("No matching skills found.")
            continue

        for i, (skill, score) in enumerate(results, start=1):
            typer.echo(f"\n[{i}] {skill.name} ({skill.platform}) — score: {score:.4f}")
            typer.echo(f"    {skill.trigger_context}")

        composed = composer.compose(results)
        typer.echo("\n── Composed context ──")
        typer.echo(composed)
        typer.echo("──────────────────────")

    typer.echo("\nExiting weave run.")
