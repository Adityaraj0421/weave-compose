"""Claude Code adapter: loads skills from SKILL.md files."""

import logging
from pathlib import Path
from typing import Any

import yaml

from weave.core.adapters.base import BaseAdapter
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class ClaudeCodeAdapter(BaseAdapter):
    """Adapter for Claude Code skill files (SKILL.md format).

    Reads any ``.md`` file found recursively under the given directory and
    normalises it into a Skill object. Files follow the SKILL.md convention:
    optional YAML frontmatter delimited by ``---`` markers, followed by a
    markdown body.

    Frontmatter keys used: ``name``, ``description``, ``capabilities``,
    ``version``, ``author``. All keys are optional — the adapter falls back
    gracefully when any are missing.
    """

    def load(self, path: str) -> list[Skill]:
        """Load all Claude Code skills from a directory path.

        Recursively scans for ``*.md`` files and attempts to parse each one.
        Files that are empty, non-UTF-8, or otherwise unparseable are skipped
        with a warning log — they never cause a crash.

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
        for md_path in sorted(resolved.rglob("*.md")):
            skill = self._load_file(md_path)
            if skill is not None:
                skills.append(skill)

        logger.info("Loaded %d skill(s) from %s (platform: claude_code)", len(skills), path)
        return skills

    def detect(self, path: str) -> bool:
        """Return True if the directory contains any ``.md`` files.

        Args:
            path: Absolute or relative path to the directory to inspect.

        Returns:
            True if at least one ``.md`` file exists under path.
        """
        try:
            return next(Path(path).rglob("*.md"), None) is not None
        except OSError:
            return False

    def _parse_frontmatter(self, content: str) -> tuple[dict[str, Any], str]:
        """Split YAML frontmatter from markdown body content.

        Expects the file to start with ``---\\n``. Splits on ``---`` with
        maxsplit=2 to avoid splitting on horizontal rules inside the body.

        Args:
            content: Full raw file content.

        Returns:
            Tuple of (frontmatter_dict, body_str). Returns ({}, content) when
            no frontmatter is found or when YAML parsing fails.
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

        body = parts[2].lstrip("\n")
        return data, body

    def _load_file(self, path: Path) -> Skill | None:
        """Parse a single ``.md`` file and return a Skill, or None on failure.

        Args:
            path: Absolute path to the ``.md`` file to load.

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

        raw_description: str = str(frontmatter.get("description", ""))
        if raw_description:
            trigger_context = raw_description
        else:
            paragraphs = body.strip().split("\n\n")
            fallback = paragraphs[0].strip().lstrip("#").strip() if paragraphs else ""
            trigger_context = fallback

        raw_caps = frontmatter.get("capabilities", [])
        capabilities: list[str] = (
            [str(c) for c in raw_caps if str(c).strip()]
            if isinstance(raw_caps, list) and raw_caps
            else self._extract_capabilities(body)
        )

        metadata: dict[str, Any] = {}
        if "version" in frontmatter:
            metadata["version"] = str(frontmatter["version"])
        if "author" in frontmatter:
            metadata["author"] = str(frontmatter["author"])

        return Skill(
            id=self._generate_id(),
            name=name,
            platform="claude_code",
            source_path=str(path),
            capabilities=capabilities,
            trigger_context=trigger_context,
            raw_content=content,
            embedding=[],
            metadata=metadata,
            loaded_at=self._timestamp(),
        )
