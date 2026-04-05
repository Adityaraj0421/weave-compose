"""Config loader for weave.yaml project configuration files."""

import logging
from pathlib import Path

import yaml

from weave.cli.config_schema import (
    CompositionConfig,
    OutputConfig,
    SkillEntry,
    WeaveConfig,
)

logger = logging.getLogger(__name__)

SUPPORTED_PLATFORMS: frozenset[str] = frozenset(
    {"claude_code", "cursor", "codex", "windsurf"}
)
SUPPORTED_STRATEGIES: frozenset[str] = frozenset(
    {"dynamic", "manual", "always-merge"}
)


def load_config(path: str) -> WeaveConfig:
    """Read, parse, validate and return a WeaveConfig from a YAML file.

    Reads the file at ``path`` using ``yaml.safe_load()``. Validates that
    required fields are present, skill entries are well-formed, and that
    platform and strategy values are supported.

    Args:
        path: Path to the weave.yaml config file.

    Returns:
        Fully populated WeaveConfig with defaults applied to optional fields.

    Raises:
        FileNotFoundError: If the file at ``path`` does not exist.
        ValueError: If any required field is missing, a skills entry is
            malformed, or a platform/strategy value is unsupported.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {path!r}. "
            "Create a weave.yaml or pass --config <path>."
        )

    with open(config_path, encoding="utf-8") as fh:
        raw: object = yaml.safe_load(fh) or {}

    if not isinstance(raw, dict):
        raise ValueError(
            f"weave.yaml must be a YAML mapping at the top level — "
            f"got {type(raw).__name__!r}"
        )

    data: dict[str, object] = raw

    version = data.get("version")
    if not version or not str(version).strip():
        raise ValueError("weave.yaml: 'version' is required and must not be empty.")

    skills = _parse_skill_entries(data.get("skills"))
    composition = _parse_composition(data.get("composition"))
    output = _parse_output(data.get("output"))

    logger.info(
        "Loaded config from %s: %d skill(s), strategy=%s",
        path,
        len(skills),
        composition.strategy,
    )

    return WeaveConfig(
        version=str(version),
        skills=skills,
        composition=composition,
        output=output,
    )


def _parse_skill_entries(raw_skills: object) -> list[SkillEntry]:
    """Parse and validate the skills list from raw YAML data.

    Args:
        raw_skills: The value of the ``skills`` key from the parsed YAML dict.
            Expected to be a non-empty list of dicts with ``path`` and
            ``platform`` keys.

    Returns:
        List of validated SkillEntry objects.

    Raises:
        ValueError: If ``raw_skills`` is not a list, is empty, or any entry
            is missing required fields or has an unsupported platform value.
    """
    if not isinstance(raw_skills, list) or len(raw_skills) == 0:
        raise ValueError(
            "weave.yaml: 'skills' is required and must be a non-empty list."
        )

    entries: list[SkillEntry] = []
    for i, item in enumerate(raw_skills):
        if not isinstance(item, dict):
            raise ValueError(
                f"weave.yaml: skills[{i}] must be a mapping with 'path' and 'platform'."
            )
        entry_path = item.get("path")
        entry_platform = item.get("platform")

        if not entry_path or not str(entry_path).strip():
            raise ValueError(
                f"weave.yaml: skills[{i}] is missing required field 'path'."
            )
        if not entry_platform or not str(entry_platform).strip():
            raise ValueError(
                f"weave.yaml: skills[{i}] is missing required field 'platform'."
            )
        if entry_platform not in SUPPORTED_PLATFORMS:
            raise ValueError(
                f"weave.yaml: skills[{i}] has unsupported platform {entry_platform!r}. "
                f"Supported: {sorted(SUPPORTED_PLATFORMS)}"
            )
        entries.append(SkillEntry(path=str(entry_path), platform=str(entry_platform)))

    return entries


def _parse_composition(raw: object) -> CompositionConfig:
    """Parse the optional composition block with defaults for missing keys.

    Args:
        raw: The value of the ``composition`` key, or ``None`` if absent.

    Returns:
        CompositionConfig with defaults applied to any missing keys.

    Raises:
        ValueError: If ``strategy`` is present but not in SUPPORTED_STRATEGIES.
    """
    if raw is None:
        return CompositionConfig()

    if not isinstance(raw, dict):
        raise ValueError("weave.yaml: 'composition' must be a mapping.")

    strategy = str(raw.get("strategy", "dynamic"))
    if strategy not in SUPPORTED_STRATEGIES:
        raise ValueError(
            f"weave.yaml: composition.strategy {strategy!r} is not supported. "
            f"Supported: {sorted(SUPPORTED_STRATEGIES)}"
        )

    return CompositionConfig(
        strategy=strategy,
        max_active_skills=int(raw.get("max_active_skills", 2)),
        confidence_threshold=float(raw.get("confidence_threshold", 0.1)),
        model=str(raw.get("model", "all-MiniLM-L6-v2")),
    )


def _parse_output(raw: object) -> OutputConfig:
    """Parse the optional output block with defaults for missing keys.

    Args:
        raw: The value of the ``output`` key, or ``None`` if absent.

    Returns:
        OutputConfig with defaults applied to any missing keys.
    """
    if raw is None:
        return OutputConfig()

    if not isinstance(raw, dict):
        raise ValueError("weave.yaml: 'output' must be a mapping.")

    return OutputConfig(
        verbose=bool(raw.get("verbose", False)),
        explain=bool(raw.get("explain", False)),
    )
