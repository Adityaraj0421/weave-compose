"""Skill selector using sentence-transformers embeddings and cosine similarity."""

import logging
from typing import Any, ClassVar, cast

import numpy as np

from sentence_transformers import SentenceTransformer

from weave.core.registry import SkillRegistry
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder:
    """Embeds text and Skill objects using a local sentence-transformers model.

    The model (``all-MiniLM-L6-v2``) is loaded lazily on the first call to
    ``embed()`` and cached as a class attribute, so subsequent calls within
    the same process reuse the loaded model without reloading weights.

    Attributes:
        _model: Class-level cache for the loaded SentenceTransformer instance.
            None until the first embed call. Typed as Any because
            sentence_transformers has no mypy stubs.
    """

    _model: ClassVar[Any] = None

    @classmethod
    def _get_model(cls) -> Any:
        """Return the cached model, loading it on first call.

        # NOTE: requires internet on first run, cached after
        (~/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2)

        Returns:
            The loaded SentenceTransformer model instance.
        """
        if cls._model is None:
            logger.info("Loading sentence-transformers model all-MiniLM-L6-v2")
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._model

    def embed(self, text: str) -> list[float]:
        """Embed a text string into a float vector.

        Calls ``model.encode()`` which returns a ``numpy.ndarray``. The
        ``.tolist()`` call converts it to a plain Python ``list[float]``
        safe for JSON serialisation and Skill storage.

        Args:
            text: The text string to embed.

        Returns:
            Float vector as a plain Python list. Length is 384 for
            ``all-MiniLM-L6-v2``.
        """
        raw = self._get_model().encode(text).tolist()
        return cast(list[float], raw)

    def embed_skill(self, skill: Skill) -> list[float]:
        """Embed a Skill by combining its trigger_context and capabilities.

        Concatenates ``trigger_context`` (highest signal field) followed by
        the space-joined ``capabilities`` list into a single string, then
        delegates to ``embed()``.

        Args:
            skill: The Skill object to embed.

        Returns:
            Float vector representing the skill's semantic content.
        """
        combined = f"{skill.trigger_context} {' '.join(skill.capabilities)}"
        return self.embed(combined)


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two float vectors.

    Uses numpy for the dot product and norm calculations. Returns 0.0 when
    either input is a zero vector to avoid division by zero.

    Args:
        a: First float vector.
        b: Second float vector. Must be the same length as ``a``.

    Returns:
        Similarity score in the range [-1, 1]. Returns 0.0 if either
        vector is a zero vector.
    """
    arr_a = np.array(a)
    arr_b = np.array(b)
    norm_a = float(np.linalg.norm(arr_a))
    norm_b = float(np.linalg.norm(arr_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(arr_a, arr_b) / (norm_a * norm_b))


class WeaveSelector:
    """Selects the best skill(s) for a query using semantic similarity.

    Embeds the query text and each skill's context, computes cosine similarity,
    and returns the top match(es). When the top two scores are within
    ``confidence_threshold`` of each other, both are returned for composition.
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
