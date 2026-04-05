"""Multi-skill context composer for the Weave composition engine."""

import logging

from weave.core.embedder import cosine_similarity
from weave.core.schema import Skill

logger = logging.getLogger(__name__)

SKILL_SEPARATOR: str = "\n\n---\n\n"

# Keyword pairs whose presence in opposing skills signals a contradiction.
# Each tuple is (positive_term, negative_term).
_OPPOSING_PAIRS: list[tuple[str, str]] = [
    ("always", "never"),
    ("use", "avoid"),
    ("enable", "disable"),
    ("add", "remove"),
    ("require", "forbid"),
    ("must", "must not"),
]


class WeaveComposer:
    """Merges selected skills into a single context string for injection.

    Takes the output of WeaveSelector (a list of (Skill, score) tuples) and
    produces one merged string. Two strategies are provided:

    - ``compose()`` — full raw_content merge, suitable for most contexts.
    - ``compose_minimal()`` — trigger_context + capabilities only, for tight
      token budgets.

    Both strategies sort skills by score descending (highest confidence first)
    and deduplicate lines across skill blocks to avoid repetition.

    Conflict detection runs automatically inside ``compose()``. When two skills
    are found to both target the same domain (embedding similarity ≥ threshold)
    AND contain opposing keyword pairs in their content, a WARNING is logged and
    the higher-score skill's content is preferred by virtue of appearing first.
    """

    CONFLICT_SIMILARITY_THRESHOLD: float = 0.9

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

        conflicts = self.detect_conflicts(sorted_skills)
        for skill_a, skill_b in conflicts:
            logger.warning(
                "Conflict detected between %r and %r — preferring %r (higher score)",
                skill_a.name,
                skill_b.name,
                skill_a.name,
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

    def detect_conflicts(
        self, skills: list[tuple[Skill, float]]
    ) -> list[tuple[Skill, Skill]]:
        """Identify conflicting skill pairs in a list of (Skill, score) tuples.

        A conflict is declared when BOTH conditions hold for a pair (A, B):

        1. **Embedding similarity ≥ CONFLICT_SIMILARITY_THRESHOLD** — the two
           skills target the same task domain. Requires both skills to have
           non-empty embeddings; pairs where either embedding is empty are
           silently skipped (no false positives).
        2. **Opposing keywords** — their ``raw_content`` fields contain at least
           one pair from ``_OPPOSING_PAIRS`` in opposing positions.

        The input list is assumed to be sorted by score descending (as produced
        by ``compose()``). Returned pairs preserve that order: the
        higher-score skill is always the first element of the tuple.

        Args:
            skills: List of (Skill, score) tuples, highest score first.

        Returns:
            List of (Skill, Skill) conflict pairs. Empty list if no conflicts
            are found or if fewer than two skills are provided.
        """
        conflicts: list[tuple[Skill, Skill]] = []
        n = len(skills)
        for i in range(n):
            for j in range(i + 1, n):
                skill_a, _ = skills[i]
                skill_b, _ = skills[j]
                if not skill_a.embedding or not skill_b.embedding:
                    continue
                sim = cosine_similarity(skill_a.embedding, skill_b.embedding)
                if sim >= self.CONFLICT_SIMILARITY_THRESHOLD and self._opposing_keywords(
                    skill_a.raw_content, skill_b.raw_content
                ):
                    conflicts.append((skill_a, skill_b))
        return conflicts

    def _opposing_keywords(self, a: str, b: str) -> bool:
        """Return True if a and b contain opposing keyword pairs from _OPPOSING_PAIRS."""
        a_lower = a.lower()
        b_lower = b.lower()
        for pos, neg in _OPPOSING_PAIRS:
            if (pos in a_lower and neg in b_lower) or (neg in a_lower and pos in b_lower):
                return True
        return False

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
