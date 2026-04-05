"""Tests for the weave.yaml config loader."""

from pathlib import Path

import pytest

from weave.cli.config import load_config
from weave.cli.config_schema import CompositionConfig, OutputConfig


def _write_yaml(tmp_path: Path, content: str) -> str:
    """Write a YAML string to a temp file and return its path as a string.

    Args:
        tmp_path: pytest tmp_path fixture directory.
        content: Raw YAML string to write.

    Returns:
        Absolute path to the written file as a string.
    """
    p = tmp_path / "weave.yaml"
    p.write_text(content, encoding="utf-8")
    return str(p)


@pytest.fixture
def valid_yaml(tmp_path: Path) -> Path:
    """Write a minimal valid weave.yaml to tmp_path and return its Path."""
    p = tmp_path / "weave.yaml"
    p.write_text(
        'version: "1"\nskills:\n  - path: .\n    platform: claude_code\n',
        encoding="utf-8",
    )
    return p


def test_load_config_valid_yaml_succeeds(valid_yaml: Path) -> None:
    """load_config() with a fully valid weave.yaml returns a WeaveConfig."""
    cfg = load_config(str(valid_yaml))
    assert cfg.version == "1"
    assert len(cfg.skills) == 1


def test_load_config_applies_composition_defaults(valid_yaml: Path) -> None:
    """load_config() with no composition block uses CompositionConfig defaults."""
    cfg = load_config(str(valid_yaml))
    assert cfg.composition == CompositionConfig()


def test_load_config_applies_output_defaults(valid_yaml: Path) -> None:
    """load_config() with no output block uses OutputConfig defaults."""
    cfg = load_config(str(valid_yaml))
    assert cfg.output == OutputConfig()


def test_load_config_missing_file_raises_file_not_found(tmp_path: Path) -> None:
    """load_config() raises FileNotFoundError for a non-existent path."""
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        load_config(str(tmp_path / "nonexistent.yaml"))


def test_load_config_missing_version_raises_value_error(tmp_path: Path) -> None:
    """load_config() raises ValueError when the version field is absent."""
    path = _write_yaml(
        tmp_path, "skills:\n  - path: .\n    platform: claude_code\n"
    )
    with pytest.raises(ValueError, match="version"):
        load_config(path)


def test_load_config_missing_skills_raises_value_error(tmp_path: Path) -> None:
    """load_config() raises ValueError when the skills key is absent."""
    path = _write_yaml(tmp_path, 'version: "1"\n')
    with pytest.raises(ValueError, match="skills"):
        load_config(path)


def test_load_config_empty_skills_list_raises_value_error(tmp_path: Path) -> None:
    """load_config() raises ValueError when skills is an empty list."""
    path = _write_yaml(tmp_path, 'version: "1"\nskills: []\n')
    with pytest.raises(ValueError, match="skills"):
        load_config(path)


def test_load_config_unknown_platform_raises_value_error(tmp_path: Path) -> None:
    """load_config() raises ValueError for an unrecognised platform string."""
    path = _write_yaml(
        tmp_path,
        'version: "1"\nskills:\n  - path: .\n    platform: vscode\n',
    )
    with pytest.raises(ValueError, match="unsupported platform"):
        load_config(path)


def test_load_config_unknown_strategy_raises_value_error(tmp_path: Path) -> None:
    """load_config() raises ValueError for an unsupported composition strategy."""
    path = _write_yaml(
        tmp_path,
        'version: "1"\nskills:\n  - path: .\n    platform: claude_code\n'
        "composition:\n  strategy: random\n",
    )
    with pytest.raises(ValueError, match="strategy"):
        load_config(path)


def test_load_config_reads_custom_composition_values(tmp_path: Path) -> None:
    """load_config() reads non-default composition values correctly."""
    path = _write_yaml(
        tmp_path,
        'version: "1"\n'
        "skills:\n  - path: .\n    platform: claude_code\n"
        "composition:\n"
        "  strategy: always-merge\n"
        "  confidence_threshold: 0.25\n"
        "  max_active_skills: 3\n",
    )
    cfg = load_config(path)
    assert cfg.composition.strategy == "always-merge"
    assert cfg.composition.confidence_threshold == 0.25
    assert cfg.composition.max_active_skills == 3
