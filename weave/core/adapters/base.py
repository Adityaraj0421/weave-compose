"""Abstract base adapter for all platform-specific skill loaders."""

import logging
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from weave.core.schema import Skill

logger = logging.getLogger(__name__)

# Common English words that are not meaningful capability keywords.
# Used by _extract_capabilities to filter noise from raw skill text.
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "the",
        "and",
        "for",
        "are",
        "not",
        "you",
        "all",
        "can",
        "use",
        "this",
        "that",
        "with",
        "have",
        "from",
        "they",
        "will",
        "been",
        "has",
        "its",
        "your",
        "our",
        "any",
        "each",
        "must",
        "only",
        "also",
        "into",
        "when",
        "than",
        "then",
        "these",
        "their",
        "there",
        "where",
        "which",
        "every",
        "never",
        "always",
        "should",
        "would",
        "could",
        "using",
        "make",
        "more",
        "such",
        "very",
        "over",
        "well",
        "both",
        "need",
        "keep",
        "set",
        "per",
        "add",
        "get",
        "put",
        "run",
        "one",
        "two",
        "new",
        "via",
        "non",
    }
)


class BaseAdapter(ABC):
    """Abstract base class for all platform-specific skill loaders.

    Every supported platform (Claude Code, Cursor, Codex, Windsurf) has a
    concrete subclass that reads its native skill file format and normalises
    the result into a list of Skill objects.

    Subclasses must implement ``load()``. The ``detect()`` method has a safe
    default (returns False) and should be overridden to signal platform match.

    Helper methods ``_generate_id``, ``_timestamp``, and
    ``_extract_capabilities`` are available to all subclasses and handle the
    mechanical parts of Skill construction so adapters stay focused on parsing.
    """

    @abstractmethod
    def load(self, path: str) -> list[Skill]:
        """Load all skills from a directory or file path.

        Args:
            path: Absolute or relative path to the directory or file to load.

        Returns:
            List of normalised Skill objects. Empty list if no skills found.
            Never returns None.

        Raises:
            FileNotFoundError: If the path does not exist.
        """

    def detect(self, path: str) -> bool:
        """Return True if this adapter can handle files at the given path.

        Subclasses override this to inspect the directory structure and signal
        whether their platform's files are present. The default returns False.

        Args:
            path: Absolute or relative path to the directory to inspect.

        Returns:
            True if this adapter should handle the path, False otherwise.
        """
        return False

    def _generate_id(self) -> str:
        """Return a new unique UUID4 string for use as a Skill id.

        Returns:
            A UUID4 string in the standard hyphenated format.
        """
        return str(uuid.uuid4())

    def _timestamp(self) -> str:
        """Return the current UTC time as an ISO 8601 string.

        Returns:
            ISO 8601 timestamp string, e.g. ``"2026-04-05T10:00:00+00:00"``.
        """
        return datetime.now(tz=timezone.utc).isoformat()

    def _extract_capabilities(self, text: str) -> list[str]:
        """Extract capability keywords from the first 500 characters of text.

        Uses simple regex tokenisation — no ML. Tokens shorter than 3
        characters and common English stop words are filtered out. Results
        are deduplicated while preserving order and capped at 10 items.

        Args:
            text: Raw skill text to extract capabilities from.

        Returns:
            List of up to 10 lowercase capability keyword strings. May be
            empty if no meaningful tokens are found.
        """
        sample = text[:500]
        tokens = re.findall(r"[a-z][a-z0-9_-]*", sample.lower())
        seen: list[str] = []
        for token in tokens:
            if len(token) >= 3 and token not in _STOP_WORDS and token not in seen:
                seen.append(token)
            if len(seen) >= 10:
                break
        return seen
