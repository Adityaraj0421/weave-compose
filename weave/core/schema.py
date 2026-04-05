"""Universal Skill schema for the Weave composition engine."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, repr=False)
class Skill:
    """Universal skill schema normalizing skills from all supported platforms.

    All platform-specific skill files (SKILL.md, .cursorrules, AGENTS.md,
    .windsurfrules) are normalized into this single dataclass. Downstream
    layers (registry, selector, composer) work exclusively with Skill objects.

    Instances are immutable after creation (frozen=True). Do not attempt to
    mutate fields — create a new Skill instead.

    Attributes:
        id: UUID4 string generated at load time. Unique per skill instance.
        name: Human-readable skill name, from frontmatter or filename fallback.
        platform: Source platform identifier. One of: "claude_code", "cursor",
            "codex", "windsurf".
        source_path: Absolute path to the original skill file on disk.
        capabilities: Extracted capability tags e.g. ["design", "components"].
            Used alongside trigger_context for embedding.
        trigger_context: Natural language description of what tasks this skill
            handles. The most important field — quality of selection depends
            on quality of this field.
        raw_content: Full original file content, completely unmodified.
        embedding: Float vector computed by sentence-transformers at load time.
            Empty list until the selector embeds the skill.
        metadata: Platform-specific extras such as version, author, tags.
            Must be typed as dict[str, Any] for mypy --strict compliance.
        loaded_at: ISO 8601 timestamp of when the skill was loaded into the
            registry.
    """

    id: str
    name: str
    platform: str
    source_path: str
    capabilities: list[str]
    trigger_context: str
    raw_content: str
    embedding: list[float]
    metadata: dict[str, Any]
    loaded_at: str

    def __repr__(self) -> str:
        """Return a concise representation showing name, platform, and capability count.

        Returns:
            String in the form: Skill(name='...', platform='...', capabilities=N)
        """
        return (
            f"Skill(name={self.name!r}, platform={self.platform!r}, "
            f"capabilities={len(self.capabilities)})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize the Skill to a plain dictionary safe for json.dumps().

        All field values are JSON-serializable primitives or collections.
        The embedding field (list[float]) and metadata field (dict[str, Any])
        serialize correctly via json.dumps without additional conversion.

        Used by SkillRegistry.save_session() to persist the registry to
        .weave_session.json between CLI invocations.

        Returns:
            Dictionary with all 10 Skill fields, keys matching field names.
        """
        return {
            "id": self.id,
            "name": self.name,
            "platform": self.platform,
            "source_path": self.source_path,
            "capabilities": self.capabilities,
            "trigger_context": self.trigger_context,
            "raw_content": self.raw_content,
            "embedding": self.embedding,
            "metadata": self.metadata,
            "loaded_at": self.loaded_at,
        }
