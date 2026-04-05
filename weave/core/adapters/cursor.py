"""Cursor adapter: loads skills from .cursorrules and .mdc files."""

import logging
from pathlib import Path
from typing import Any

import yaml

from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.manifest import apply_manifest
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class CursorAdapter(BaseAdapter):
    """Adapter for Cursor skill files (.cursorrules and .mdc format).

    Reads ``*.cursorrules`` files (plain text, legacy format) and ``*.mdc``
    files under ``.cursor/rules/`` (YAML frontmatter, current format).
    Both are normalised into Skill objects with ``platform="cursor"``.
    """

    def load(self, path: str) -> list[Skill]:
        """Load all Cursor skills from a directory path.

        Args:
            path: Absolute or relative path to the directory to scan.

        Returns:
            List of normalised Skill objects. Empty list if no skills found.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        resolved = Path(path).resolve()
        if not resolved.exists():
            raise FileNotFoundError(f"Path does not exist: {path!r}")

        skills: list[Skill] = []

        for cursorrules_path in sorted(resolved.rglob("*.cursorrules")):
            skill = self._load_cursorrules_file(cursorrules_path)
            if skill is not None:
                skills.append(skill)

        mdc_dir = resolved / ".cursor" / "rules"
        if mdc_dir.is_dir():
            for mdc_path in sorted(mdc_dir.glob("*.mdc")):
                skill = self._load_mdc_file(mdc_path)
                if skill is not None:
                    skills.append(skill)

        logger.info("Loaded %d skill(s) from %s (platform: cursor)", len(skills), path)
        return skills

    def detect(self, path: str) -> bool:
        """Return True if the directory contains .cursorrules or .mdc files.

        Args:
            path: Absolute or relative path to the directory to inspect.

        Returns:
            True if at least one supported Cursor file exists under path.
        """
        try:
            p = Path(path)
            has_cursorrules = next(p.rglob("*.cursorrules"), None) is not None
            mdc_dir = p / ".cursor" / "rules"
            has_mdc = mdc_dir.is_dir() and next(mdc_dir.glob("*.mdc"), None) is not None
            return has_cursorrules or has_mdc
        except OSError:
            return False

    def _parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """Split YAML frontmatter from body. Returns ({}, content) on failure.

        Args:
            content: Full raw file content.

        Returns:
            Tuple of (frontmatter_dict, body_str).
        """
        if not content.startswith("---\n"):
            return {}, content
        parts = content.split("---", maxsplit=2)
        if len(parts) < 3:
            return {}, content
        try:
            data = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError as exc:
            logger.warning("YAML parse error in frontmatter — skipping: %s", exc)
            return {}, content
        if not isinstance(data, dict):
            return {}, content
        return data, parts[2].lstrip("\n")

    def _load_cursorrules_file(self, path: Path) -> Skill | None:
        """Parse a single ``*.cursorrules`` file and return a Skill, or None.

        Args:
            path: Absolute path to the ``*.cursorrules`` file.

        Returns:
            A Skill object if the file is valid, None if it should be skipped.
        """
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("Could not read %s — skipping: %s", path, exc)
            return None

        if not content.strip():
            logger.warning("Empty file, skipping: %s", path)
            return None

        # Path(".cursorrules").stem == ".cursorrules" — strip leading dot
        name = path.stem.lstrip(".") or "cursor-rules"
        paragraphs = content.strip().split("\n\n")
        trigger_context = paragraphs[0].strip() if paragraphs else ""

        skill = Skill(
            id=self._generate_id(),
            name=name,
            platform="cursor",
            source_path=str(path),
            capabilities=self._extract_capabilities(content),
            trigger_context=trigger_context,
            raw_content=content,
            embedding=[],
            metadata={"format": "cursorrules"},
            loaded_at=self._timestamp(),
        )
        return apply_manifest(skill, path)

    def _load_mdc_file(self, path: Path) -> Skill | None:
        """Parse a single ``*.mdc`` file and return a Skill, or None on failure.

        Args:
            path: Absolute path to the ``*.mdc`` file.

        Returns:
            A Skill object if the file is valid, None if it should be skipped.
        """
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError as exc:
            logger.warning("Could not read %s — skipping: %s", path, exc)
            return None

        if not content.strip():
            logger.warning("Empty file, skipping: %s", path)
            return None

        frontmatter, body = self._parse_frontmatter(content)
        name: str = str(frontmatter.get("name", "")) or path.stem

        description: str = str(frontmatter.get("description", ""))
        if description:
            trigger_context = description
        else:
            paragraphs = body.strip().split("\n\n")
            trigger_context = paragraphs[0].strip() if paragraphs else ""

        raw_globs = frontmatter.get("globs", [])
        globs: list[str] = (
            [str(g) for g in raw_globs if str(g).strip()]
            if isinstance(raw_globs, list)
            else []
        )
        capabilities = globs if globs else self._extract_capabilities(body or content)

        metadata: dict[str, Any] = {"format": "mdc"}
        if globs:
            metadata["globs"] = globs

        skill = Skill(
            id=self._generate_id(),
            name=name,
            platform="cursor",
            source_path=str(path),
            capabilities=capabilities,
            trigger_context=trigger_context,
            raw_content=content,
            embedding=[],
            metadata=metadata,
            loaded_at=self._timestamp(),
        )
        return apply_manifest(skill, path)
