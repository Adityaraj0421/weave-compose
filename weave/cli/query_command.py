"""Query command for the Weave CLI — skill selection with optional composed output."""

import logging

import typer

from weave.core.composer import WeaveComposer
from weave.core.registry import SkillRegistry
from weave.core.selector import WeaveSelector

logger = logging.getLogger(__name__)

# Local constant — avoids circular import with main.py
SESSION_FILE: str = ".weave_session.json"


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
    output: str = typer.Option(
        "skill",
        "--output",
        "-o",
        help="Output format: skill (default) or composed",
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

    if output == "composed":
        composed = WeaveComposer().compose(results)
        typer.echo("\n── Composed context ──")
        typer.echo(composed)
        typer.echo("──────────────────────")
