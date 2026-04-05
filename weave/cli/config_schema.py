"""Typed dataclasses for the weave.yaml configuration schema."""

from dataclasses import dataclass, field


@dataclass
class SkillEntry:
    """One entry from the skills list in weave.yaml.

    Attributes:
        path: Relative or absolute path to the skill directory.
        platform: Platform identifier for the adapter to use.
    """

    path: str
    platform: str


@dataclass
class CompositionConfig:
    """Typed representation of the composition: block in weave.yaml.

    All fields have defaults matching the documented schema so the block
    is entirely optional in the config file.

    Attributes:
        strategy: Composition strategy. One of: dynamic, manual, always-merge.
        max_active_skills: Hard cap on skills returned by the selector.
        confidence_threshold: Max score gap for dual-skill selection.
        model: Sentence-transformers model name for embedding.
    """

    strategy: str = "dynamic"
    max_active_skills: int = 2
    confidence_threshold: float = 0.1
    model: str = "all-MiniLM-L6-v2"


@dataclass
class OutputConfig:
    """Typed representation of the output: block in weave.yaml.

    All fields have defaults so the block is entirely optional.

    Attributes:
        verbose: If True, print each loaded skill name and capability count.
        explain: If True, print similarity scores for all loaded skills.
    """

    verbose: bool = False
    explain: bool = False


@dataclass
class WeaveConfig:
    """Fully validated, typed representation of a weave.yaml file.

    Attributes:
        version: Config schema version string. Currently ``"1"``.
        skills: Non-empty list of skill directory entries to load.
        composition: Composition settings with defaults applied.
        output: Output verbosity settings with defaults applied.
    """

    version: str
    skills: list[SkillEntry]
    composition: CompositionConfig = field(default_factory=CompositionConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
