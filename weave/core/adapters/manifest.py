"""Manifest loader: reads weave.skill.json sidecars and applies them to Skills."""

import dataclasses
import json
import logging
from pathlib import Path
from typing import Any

from weave.core.schema import Skill

logger = logging.getLogger(__name__)

MANIFEST_FILENAME: str = "weave.skill.json"


def load_manifest(skill_file: Path) -> dict[str, Any] | None:
    """Load a manifest sidecar from the same directory as skill_file.

    Checks for a skill-specific manifest named ``<stem>.skill.json`` first
    (e.g. ``naksha_design.skill.json`` for ``naksha_design.md``), then falls
    back to the directory-level ``weave.skill.json``. The skill-specific name
    takes precedence so that multiple skill files in the same directory can each
    have their own manifest without conflicts.

    Returns ``None`` silently if neither file exists or if parsing fails —
    manifests are always optional and must never prevent a skill from loading.

    Args:
        skill_file: Absolute path to the skill file whose directory is searched.

    Returns:
        Parsed manifest dict if a sidecar exists and is valid JSON, else None.
    """
    # Prefer <stem>.skill.json (skill-specific) over weave.skill.json (directory-level)
    stem_manifest = skill_file.parent / f"{skill_file.stem}.skill.json"
    manifest_path = stem_manifest if stem_manifest.exists() else skill_file.parent / MANIFEST_FILENAME
    try:
        content = manifest_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError as exc:
        logger.debug("Could not read manifest at %s: %s", manifest_path, exc)
        return None

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        logger.warning("Invalid JSON in manifest %s — ignoring: %s", manifest_path, exc)
        return None

    if not isinstance(data, dict):
        logger.warning("Manifest %s must be a JSON object — ignoring", manifest_path)
        return None

    logger.debug("Manifest found: %s", manifest_path)
    return data


def apply_manifest(skill: Skill, skill_file: Path) -> Skill:
    """Apply weave.skill.json sidecar fields to a Skill, returning a new Skill.

    Loads the manifest from the same directory as ``skill_file``. If no manifest
    exists or loading fails, the original skill is returned unchanged. When a
    manifest is present, its fields take precedence over adapter-inferred values
    for ``name``, ``capabilities``, ``trigger_context``, and ``metadata``.

    The returned Skill is a new frozen instance — the original is never mutated.

    Manifest field mapping:
        ``name``             → ``skill.name`` (if non-empty)
        ``capabilities``     → ``skill.capabilities`` (if present)
        ``trigger_patterns`` → ``skill.trigger_context`` (first entry, if non-empty)
        ``version``          → ``skill.metadata["version"]``
        ``author``           → ``skill.metadata["author"]``
        ``dependencies``     → ``skill.metadata["dependencies"]``

    Args:
        skill: The Skill object produced by the adapter's file parser.
        skill_file: Absolute path to the skill file (used to locate the sidecar).

    Returns:
        A new Skill with manifest fields applied, or the original skill unchanged
        if no manifest was found.
    """
    manifest = load_manifest(skill_file)
    if manifest is None:
        return skill

    # name — prefer manifest if non-empty
    raw_name = str(manifest.get("name", "")).strip()
    name = raw_name if raw_name else skill.name

    # capabilities — prefer manifest list if present
    raw_caps = manifest.get("capabilities")
    capabilities: list[str] = (
        [str(c) for c in raw_caps if str(c).strip()]
        if isinstance(raw_caps, list)
        else skill.capabilities
    )

    # trigger_context — first trigger_pattern if list is non-empty
    raw_patterns = manifest.get("trigger_patterns")
    if isinstance(raw_patterns, list) and raw_patterns:
        trigger_context = str(raw_patterns[0]).strip() or skill.trigger_context
    else:
        trigger_context = skill.trigger_context

    # metadata — copy existing, overlay manifest extras
    metadata: dict[str, Any] = dict(skill.metadata)
    version = str(manifest.get("version", "")).strip()
    author = str(manifest.get("author", "")).strip()
    raw_deps = manifest.get("dependencies", [])
    dependencies: list[str] = (
        [str(d) for d in raw_deps if str(d).strip()]
        if isinstance(raw_deps, list)
        else []
    )
    if version:
        metadata["version"] = version
    if author:
        metadata["author"] = author
    if dependencies:
        metadata["dependencies"] = dependencies

    return dataclasses.replace(
        skill,
        name=name,
        capabilities=capabilities,
        trigger_context=trigger_context,
        metadata=metadata,
    )
