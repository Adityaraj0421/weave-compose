"""Skill selector using sentence-transformers embeddings and cosine similarity."""

import logging
from typing import Any, ClassVar, cast

from sentence_transformers import SentenceTransformer

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
