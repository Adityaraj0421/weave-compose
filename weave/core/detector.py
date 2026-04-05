"""Platform auto-detector for the Weave composition engine."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def detect_platform(path: str) -> str:
    """Auto-detect platform from directory contents.

    Checks the directory at path against known file and directory patterns for
    each supported platform. Returns the first match in priority order:
    claude_code → cursor → codex → windsurf → unknown.

    Never raises — non-existent or non-directory paths return ``"unknown"``.

    Args:
        path: Absolute or relative path to the directory to inspect.

    Returns:
        Platform string: one of ``"claude_code"``, ``"cursor"``, ``"codex"``,
        ``"windsurf"``, or ``"unknown"`` if no pattern matched or the path
        does not exist or is not a directory.
    """
    dir_path = Path(path)

    if not dir_path.exists() or not dir_path.is_dir():
        logger.debug(
            "detect_platform: path %r does not exist or is not a directory — returning unknown",
            path,
        )
        return "unknown"

    # claude_code: SKILL.md at root, or a skills/ subdirectory containing .md files
    has_skill_md = (dir_path / "SKILL.md").exists()
    skills_dir = dir_path / "skills"
    has_skills_dir = skills_dir.is_dir() and any(skills_dir.glob("*.md"))
    if has_skill_md or has_skills_dir:
        logger.info("detect_platform: detected %r for path %r", "claude_code", path)
        return "claude_code"

    # cursor: .cursorrules file, or .cursor/rules/ subdirectory
    has_cursorrules = (dir_path / ".cursorrules").exists()
    has_cursor_rules_dir = (dir_path / ".cursor" / "rules").is_dir()
    if has_cursorrules or has_cursor_rules_dir:
        logger.info("detect_platform: detected %r for path %r", "cursor", path)
        return "cursor"

    # codex: .codex/ subdirectory, or AGENTS.md at root
    has_codex_dir = (dir_path / ".codex").is_dir()
    has_agents_md = (dir_path / "AGENTS.md").exists()
    if has_codex_dir or has_agents_md:
        logger.info("detect_platform: detected %r for path %r", "codex", path)
        return "codex"

    # windsurf: .windsurfrules file at root
    if (dir_path / ".windsurfrules").exists():
        logger.info("detect_platform: detected %r for path %r", "windsurf", path)
        return "windsurf"

    logger.debug("detect_platform: no platform detected for path %r — returning unknown", path)
    return "unknown"
