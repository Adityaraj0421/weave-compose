"""Tests for the platform auto-detector."""

from pathlib import Path

from weave.core.detector import detect_platform

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_detect_platform_returns_claude_code_for_skill_md(tmp_path: Path) -> None:
    """SKILL.md at root triggers claude_code detection."""
    (tmp_path / "SKILL.md").touch()
    assert detect_platform(str(tmp_path)) == "claude_code"


def test_detect_platform_returns_claude_code_for_skills_subdir(tmp_path: Path) -> None:
    """skills/ subdirectory containing a .md file triggers claude_code detection."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (skills_dir / "my_skill.md").touch()
    assert detect_platform(str(tmp_path)) == "claude_code"


def test_detect_platform_returns_cursor_for_cursorrules(tmp_path: Path) -> None:
    """.cursorrules file at root triggers cursor detection."""
    (tmp_path / ".cursorrules").touch()
    assert detect_platform(str(tmp_path)) == "cursor"


def test_detect_platform_returns_codex_for_agents_md(tmp_path: Path) -> None:
    """AGENTS.md at root triggers codex detection."""
    (tmp_path / "AGENTS.md").touch()
    assert detect_platform(str(tmp_path)) == "codex"


def test_detect_platform_returns_codex_for_codex_dir(tmp_path: Path) -> None:
    """.codex/ subdirectory triggers codex detection."""
    (tmp_path / ".codex").mkdir()
    assert detect_platform(str(tmp_path)) == "codex"


def test_detect_platform_returns_windsurf(tmp_path: Path) -> None:
    """.windsurfrules file at root triggers windsurf detection."""
    (tmp_path / ".windsurfrules").touch()
    assert detect_platform(str(tmp_path)) == "windsurf"


def test_detect_platform_returns_unknown_for_empty_dir(tmp_path: Path) -> None:
    """Empty directory returns unknown."""
    assert detect_platform(str(tmp_path)) == "unknown"


def test_detect_platform_returns_unknown_for_nonexistent_path() -> None:
    """Non-existent path returns unknown without raising."""
    assert detect_platform("/nonexistent/path/that/cannot/exist") == "unknown"


def test_detect_platform_returns_unknown_for_file_path(tmp_path: Path) -> None:
    """Passing a file path (not a directory) returns unknown."""
    file_path = tmp_path / "somefile.txt"
    file_path.touch()
    assert detect_platform(str(file_path)) == "unknown"
