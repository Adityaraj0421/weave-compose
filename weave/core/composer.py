"""Multi-skill context composer for the Weave composition engine."""

import logging

from weave.core.schema import Skill

logger = logging.getLogger(__name__)

SKILL_SEPARATOR: str = "\n\n---\n\n"


class WeaveComposer:
    """Merges selected skills into a single context string for injection.

    Takes the output of WeaveSelector (a list of (Skill, score) tuples) and
    produces one merged string. Two strategies are provided:

    - ``compose()`` — full raw_content merge, suitable for most contexts.
    - ``compose_minimal()`` — trigger_context + capabilities only, for tight
      token budgets.

    Both strategies sort skills by score descending (highest confidence first)
    and deduplicate lines across skill blocks to avoid repetition.
    """

    def compose(self, skills: list[tuple[Skill, float]]) -> str:
        """Merge full raw_content from selected skills into one context string.

        Sorts by score descending so the highest-confidence skill's content
        appears first. Splits each skill's ``raw_content`` into lines, tracks
        seen lines across all blocks, and drops duplicate lines from later
        blocks. Skill blocks are joined with ``SKILL_SEPARATOR``.

        Args:
            skills: List of (Skill, score) tuples from WeaveSelector.select().
                Empty list returns an empty string.

        Returns:
            Single merged string with duplicate lines removed across skills.
            Empty string if ``skills`` is empty. Single skill's raw_content
            (stripped) if only one skill is provided.
        """
        if not skills:
            return ""

        sorted_skills = sorted(skills, key=lambda t: t[1], reverse=True)

        for skill, score in sorted_skills:
            logger.info(
                "Composing skill: %s (%s) — score: %.4f",
                skill.name,
                skill.platform,
                score,
            )

        blocks = [skill.raw_content.strip() for skill, _ in sorted_skills]
        deduped = self._deduplicate(blocks)
        return SKILL_SEPARATOR.join(block for block in deduped if block)

    def compose_minimal(self, skills: list[tuple[Skill, float]]) -> str:
        """Merge only trigger_context and capabilities from selected skills.

        Produces a compact context for tight token budgets. Each skill
        contributes one block: its ``trigger_context`` followed by a
        bullet-list of its ``capabilities``. Blocks are joined with
        ``SKILL_SEPARATOR``. Deduplication is applied at the line level
        across all blocks.

        Args:
            skills: List of (Skill, score) tuples from WeaveSelector.select().
                Empty list returns an empty string.

        Returns:
            Minimal merged string, shorter than ``compose()`` for the same
            input. Empty string if ``skills`` is empty.
        """
        if not skills:
            return ""

        sorted_skills = sorted(skills, key=lambda t: t[1], reverse=True)

        blocks: list[str] = []
        for skill, _ in sorted_skills:
            cap_lines = "\n".join(f"- {cap}" for cap in skill.capabilities)
            block = f"{skill.trigger_context.strip()}\n{cap_lines}".strip()
            blocks.append(block)

        deduped = self._deduplicate(blocks)
        return SKILL_SEPARATOR.join(block for block in deduped if block)

    def _deduplicate(self, blocks: list[str]) -> list[str]:
        """Return blocks with duplicate lines removed across all blocks.

        Lines in earlier blocks are kept verbatim. Lines in later blocks
        are dropped if the same line appeared in any earlier block. Blank
        lines are always preserved and never treated as duplicates.

        Args:
            blocks: Ordered list of text blocks (highest-score first).

        Returns:
            New list of blocks with cross-block duplicate lines removed.
            Block count and order are preserved; some blocks may be shorter
            if their lines duplicated earlier content.
        """
        seen: set[str] = set()
        result: list[str] = []

        for block in blocks:
            lines = block.split("\n")
            kept: list[str] = []
            for line in lines:
                if not line.strip():
                    kept.append(line)
                elif line not in seen:
                    seen.add(line)
                    kept.append(line)
            result.append("\n".join(kept))

        return result
