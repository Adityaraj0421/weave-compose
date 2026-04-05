"""Codex adapter: loads skills from AGENTS.md and .codex/*.md files."""

import logging
from pathlib import Path
from typing import Any

import yaml

from weave.core.adapters.base import BaseAdapter
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class CodexAdapter(BaseAdapter):
    """Adapter for Codex skill files (AGENTS.md and .codex/*.md format).

    Reads two sources from the given directory:

    - ``AGENTS.md`` at the directory root (standard single-agent file).
    - ``*.md`` files under ``.codex/`` (multi-agent directory format).

    Both are normalised into Skill objects with ``platform="codex"``.
    Files that are empty, non-UTF-8, or otherwise unparseable are skipped
    with a warning — they never cause a crash.
    """

    def load(self, path: str) -> list[Skill]:
        """Load all Codex skills from a directory path.

        Checks for ``AGENTS.md`` at root first, then scans ``.codex/*.md``.
        Results are returned in that order.

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

        agents_md = resolved / "AGENTS.md"
        if agents_md.is_file():
            skill = self._load_md_file(agents_md)
            if skill is not None:
                skills.append(skill)

        codex_dir = resolved / ".codex"
        if codex_dir.is_dir():
            for md_path in sorted(codex_dir.glob("*.md")):
                skill = self._load_md_file(md_path)
                if skill is not None:
                    skills.append(skill)

        logger.info("Loaded %d skill(s) from %s (platform: codex)", len(skills), path)
        return skills

    def detect(self, path: str) -> bool:
        """Return True if the directory contains AGENTS.md or .codex/*.md files.

        Args:
            path: Absolute or relative path to the directory to inspect.

        Returns:
            True if at least one supported Codex file exists under path.
        """
        try:
            p = Path(path)
            has_agents_md = (p / "AGENTS.md").is_file()
            codex_dir = p / ".codex"
            has_codex_dir = codex_dir.is_dir() and next(codex_dir.glob("*.md"), None) is not None
            return has_agents_md or has_codex_dir
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

    def _extract_heading_name(self, content: str) -> str:
        """Return the text of the first '# ' heading, or empty string if none.

        Args:
            content: Raw markdown content to search.

        Returns:
            Heading text without the leading ``# ``, or ``""`` if not found.
        """
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return ""

    def _load_md_file(self, path: Path) -> Skill | None:
        """Parse a single markdown file and return a Skill, or None on failure.

        Name resolved in priority order: frontmatter["name"] → first # heading
        → file stem. trigger_context: frontmatter["description"] → first
        non-heading, non-empty paragraph of body.

        Args:
            path: Absolute path to the ``.md`` file.

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

        name: str = (
            str(frontmatter.get("name", ""))
            or self._extract_heading_name(content)
            or path.stem
        )

        description: str = str(frontmatter.get("description", ""))
        if description:
            trigger_context = description
        else:
            paragraphs = body.strip().split("\n\n")
            trigger_context = next(
                (p.strip() for p in paragraphs if p.strip() and not p.strip().startswith("#")),
                paragraphs[0].strip() if paragraphs else "",
            )

        raw_caps = frontmatter.get("capabilities", [])
        capabilities: list[str] = (
            [str(c) for c in raw_caps if str(c).strip()]
            if isinstance(raw_caps, list) and raw_caps
            else self._extract_capabilities(body or content)
        )

        metadata: dict[str, Any] = {}
        if "version" in frontmatter:
            metadata["version"] = str(frontmatter["version"])
        if "author" in frontmatter:
            metadata["author"] = str(frontmatter["author"])

        return Skill(
            id=self._generate_id(),
            name=name,
            platform="codex",
            source_path=str(path),
            capabilities=capabilities,
            trigger_context=trigger_context,
            raw_content=content,
            embedding=[],
            metadata=metadata,
            loaded_at=self._timestamp(),
        )
