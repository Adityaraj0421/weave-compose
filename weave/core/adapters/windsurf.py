"""Windsurf adapter: loads skills from .windsurfrules files."""

import logging
from pathlib import Path
from typing import Any

from weave.core.adapters.base import BaseAdapter
from weave.core.adapters.manifest import apply_manifest
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class WindsurfAdapter(BaseAdapter):
    """Adapter for Windsurf skill files (.windsurfrules format).

    Reads ``*.windsurfrules`` files found anywhere under the given directory.
    Windsurf uses a single plain-text rules file at the project root — no
    frontmatter, no MDC equivalent. All files are normalised into Skill
    objects with ``platform="windsurf"``.
    """

    def load(self, path: str) -> list[Skill]:
        """Load all Windsurf skills from a directory path.

        Recursively scans for ``*.windsurfrules`` files. Files that are
        empty, non-UTF-8, or otherwise unreadable are skipped with a warning.

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

        for ws_path in sorted(resolved.rglob("*.windsurfrules")):
            skill = self._load_windsurfrules_file(ws_path)
            if skill is not None:
                skills.append(skill)

        logger.info("Loaded %d skill(s) from %s (platform: windsurf)", len(skills), path)
        return skills

    def detect(self, path: str) -> bool:
        """Return True if the directory contains any .windsurfrules files.

        Args:
            path: Absolute or relative path to the directory to inspect.

        Returns:
            True if at least one ``.windsurfrules`` file exists under path.
        """
        try:
            return next(Path(path).rglob("*.windsurfrules"), None) is not None
        except OSError:
            return False

    def _load_windsurfrules_file(self, path: Path) -> Skill | None:
        """Parse a single ``*.windsurfrules`` file and return a Skill, or None.

        Name is resolved via ``path.stem.lstrip(".") or "windsurf-rules"``
        to handle the standard hidden filename ``.windsurfrules`` whose stem
        would otherwise be ``.windsurfrules`` (with leading dot).
        trigger_context is the first non-empty paragraph of content.

        Args:
            path: Absolute path to the ``*.windsurfrules`` file.

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

        # Path(".windsurfrules").stem == ".windsurfrules" — strip leading dot
        name = path.stem.lstrip(".") or "windsurf-rules"

        paragraphs = content.strip().split("\n\n")
        trigger_context = paragraphs[0].strip() if paragraphs else ""

        metadata: dict[str, Any] = {"format": "windsurfrules"}

        skill = Skill(
            id=self._generate_id(),
            name=name,
            platform="windsurf",
            source_path=str(path),
            capabilities=self._extract_capabilities(content),
            trigger_context=trigger_context,
            raw_content=content,
            embedding=[],
            metadata=metadata,
            loaded_at=self._timestamp(),
        )
        return apply_manifest(skill, path)
