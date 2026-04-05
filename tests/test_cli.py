"""Tests for the Weave CLI commands."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from weave.cli.main import app

CLAUDE_FIXTURES = Path(__file__).parent / "fixtures" / "claude_code"

runner = CliRunner()


def test_load_succeeds_and_creates_session_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave load with a valid path exits 0 and writes .weave_session.json."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["load", str(CLAUDE_FIXTURES)])
    assert result.exit_code == 0
    assert (tmp_path / ".weave_session.json").exists()


def test_load_with_invalid_path_prints_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave load with a non-existent path exits non-zero and prints an error."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["load", "/nonexistent/skills/directory"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_query_with_no_session_file_prints_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave query with no session file exits non-zero with a helpful message."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["query", "design a component"])
    assert result.exit_code != 0
    assert "No skills loaded" in result.output


def test_query_returns_result_after_loading(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave query returns a skill result after weave load has been run.

    NOTE: triggers sentence-transformers model loading on first run (~60s).
    Model is cached after the first invocation.
    """
    monkeypatch.chdir(tmp_path)
    load_result = runner.invoke(app, ["load", str(CLAUDE_FIXTURES)])
    assert load_result.exit_code == 0

    result = runner.invoke(app, ["query", "design a UI component with Tailwind"])
    assert result.exit_code == 0
    assert "Naksha" in result.output


def test_query_with_output_composed_prints_composed_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave query --output composed prints merged composed context after loading."""
    monkeypatch.chdir(tmp_path)
    load_result = runner.invoke(app, ["load", str(CLAUDE_FIXTURES)])
    assert load_result.exit_code == 0

    result = runner.invoke(
        app, ["query", "design a UI component with Tailwind", "--output", "composed"]
    )
    assert result.exit_code == 0
    assert "Composed context" in result.output


def test_clear_deletes_session_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave clear removes .weave_session.json after user confirms."""
    monkeypatch.chdir(tmp_path)
    session = tmp_path / ".weave_session.json"
    session.write_text('{"version":"1","saved_at":"","skills":[]}')

    result = runner.invoke(app, ["clear"], input="y\n")
    assert result.exit_code == 0
    assert not session.exists()


def test_detect_prints_platform_for_claude_code_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """weave detect prints 'Detected platform: claude_code' for a dir with SKILL.md."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / "SKILL.md").touch()
    result = runner.invoke(app, ["detect", str(tmp_path)])
    assert result.exit_code == 0
    assert "Detected platform: claude_code" in result.output


def test_detect_prints_unknown_for_empty_dir(tmp_path: Path) -> None:
    """weave detect prints 'Unknown platform' for an empty directory."""
    result = runner.invoke(app, ["detect", str(tmp_path)])
    assert result.exit_code == 0
    assert "Unknown platform" in result.output
