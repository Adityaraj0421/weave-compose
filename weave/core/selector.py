"""Skill selector using semantic similarity and activation strategy dispatch."""

import logging

from weave.core.embedder import SentenceTransformerEmbedder, cosine_similarity
from weave.core.registry import SkillRegistry
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class WeaveSelector:
    """Selects skill(s) for a query using semantic similarity or explicit strategy.

    Three activation strategies are supported:

    - ``dynamic`` — embed the query, rank by cosine similarity, return top match(es).
      Use :meth:`select`.
    - ``always-merge`` — return every loaded skill regardless of query relevance.
      Use :meth:`select_all`.
    - ``manual`` — caller specifies skill names explicitly; no scoring applied.
      Use :meth:`select_manual`.
    """

    def __init__(self) -> None:
        """Initialise the selector with a fresh embedder instance."""
        self._embedder = SentenceTransformerEmbedder()

    def select(
        self,
        query: str,
        registry: SkillRegistry,
        top_n: int = 1,
        confidence_threshold: float = 0.1,
        max_active_skills: int = 2,
        explain: bool = False,
    ) -> list[tuple[Skill, float]]:
        """Select the best skill(s) from the registry for the given query.

        Embeds the query, scores every registered skill by cosine similarity,
        and returns the top result(s). If ``top_n`` is 1 and the second-best
        score is within ``confidence_threshold`` of the best, both are returned
        for composition. The result is always capped at ``max_active_skills``.

        Skills with an empty ``embedding`` field are embedded on-the-fly using
        ``embed_skill()``, so the selector works even before a session save.

        Args:
            query: Natural language task description to match against skills.
            registry: The SkillRegistry to search.
            top_n: Minimum number of top skills to return.
            confidence_threshold: Maximum score gap between rank-1 and rank-2
                for both to be returned when top_n is 1.
            max_active_skills: Hard cap on the number of skills returned.
            explain: If True, logs a score table at INFO level for debugging.

        Returns:
            List of (Skill, score) tuples sorted by score descending.
            Empty list if the registry contains no skills.
        """
        skills = registry.get_all()
        if not skills:
            return []

        query_vec = self._embedder.embed(query)

        scored: list[tuple[Skill, float]] = []
        for skill in skills:
            vec = skill.embedding if skill.embedding else self._embedder.embed_skill(skill)
            score = cosine_similarity(query_vec, vec)
            scored.append((skill, score))

        scored.sort(key=lambda t: t[1], reverse=True)

        if explain:
            logger.info("WeaveSelector scores for query: %r", query)
            for skill, score in scored:
                logger.info("  %.4f  %s (%s)", score, skill.name, skill.platform)

        result = scored[:top_n]
        if top_n == 1 and len(scored) >= 2:
            gap = scored[0][1] - scored[1][1]
            if gap < confidence_threshold:
                result = scored[:2]

        return result[:max_active_skills]

    def select_all(
        self,
        registry: SkillRegistry,
        max_active_skills: int = 2,
    ) -> list[tuple[Skill, float]]:
        """Return all skills in the registry, each with a score of 1.0.

        Implements the ``always-merge`` activation strategy: every loaded skill
        is returned regardless of query relevance, capped at ``max_active_skills``.
        Results are returned in registration order (stable and deterministic).

        Args:
            registry: The SkillRegistry to pull all skills from.
            max_active_skills: Hard cap on the number of skills returned.

        Returns:
            List of (Skill, 1.0) tuples. Empty list if the registry is empty.
        """
        skills = registry.get_all()
        logger.info("select_all: returning %d skill(s)", min(len(skills), max_active_skills))
        return [(skill, 1.0) for skill in skills][:max_active_skills]

    def select_manual(
        self,
        names: list[str],
        registry: SkillRegistry,
    ) -> list[tuple[Skill, float]]:
        """Return skills matching the given names, each with a score of 1.0.

        Implements the ``manual`` activation strategy: the caller specifies
        exactly which skills to activate by name. Matching is case-sensitive.
        Skills not found in the registry are logged at WARNING level and skipped.

        Args:
            names: List of skill name strings to look up in the registry.
            registry: The SkillRegistry to search.

        Returns:
            List of (Skill, 1.0) tuples in the order of names that matched.
            Empty list if no names matched any registered skill.
        """
        name_map: dict[str, Skill] = {skill.name: skill for skill in registry.get_all()}
        results: list[tuple[Skill, float]] = []
        for name in names:
            if name in name_map:
                results.append((name_map[name], 1.0))
            else:
                logger.warning(
                    "select_manual: skill %r not found in registry — skipping", name
                )
        return results
