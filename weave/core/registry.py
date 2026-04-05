"""In-memory skill registry for the Weave composition engine."""

import json
import logging
from datetime import datetime, timezone
from typing import Any

from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """In-memory store for the current Weave session's loaded skills.

    Skills are keyed internally by their ``id`` field. Registering a skill
    with a duplicate id overwrites the existing entry (last-write-wins).

    This class is the single source of truth for session state. All other
    modules are stateless — they receive inputs and return outputs.

    ``save_session`` and ``load_session`` are CLI-layer helpers for persisting
    state between separate process invocations. They are not called internally.
    """

    def __init__(self) -> None:
        """Initialise an empty registry."""
        self._store: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """Add or overwrite a skill in the registry.

        Args:
            skill: The Skill object to register. Keyed by ``skill.id``.
        """
        self._store[skill.id] = skill
        logger.info("Registered skill %r (platform: %s)", skill.name, skill.platform)

    def get_all(self) -> list[Skill]:
        """Return all registered skills in insertion order.

        Returns:
            List of all Skill objects.
        """
        return list(self._store.values())

    def get_by_platform(self, platform: str) -> list[Skill]:
        """Return all skills matching the given platform identifier.

        Args:
            platform: Platform string to filter on, e.g. ``"claude_code"``.

        Returns:
            List of matching Skill objects. Empty list if none found.
        """
        return [s for s in self._store.values() if s.platform == platform]

    def get_by_id(self, id: str) -> Skill | None:
        """Return the skill with the given id, or None if not found.

        Args:
            id: UUID4 string matching the target skill's ``id`` field.

        Returns:
            The matching Skill, or None.
        """
        return self._store.get(id)

    def clear(self) -> None:
        """Remove all skills from the registry."""
        self._store.clear()
        logger.info("Registry cleared")

    def count(self) -> int:
        """Return the number of skills currently in the registry."""
        return len(self._store)

    def save_session(self, path: str) -> None:
        """Serialise the registry to a JSON session file.

        Writes all registered skills using ``Skill.to_dict()`` into a file
        at ``path``. The session file is read back by ``load_session`` in a
        later process invocation.

        Args:
            path: File path to write the session JSON to.
        """
        payload: dict[str, Any] = {
            "version": "1",
            "saved_at": datetime.now(tz=timezone.utc).isoformat(),
            "skills": [skill.to_dict() for skill in self._store.values()],
        }
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        logger.info("Session saved to %s (%d skills)", path, len(self._store))

    def load_session(self, path: str) -> None:
        """Restore skills from a previously saved JSON session file.

        On success, all skills in the file are registered into the current
        registry. On any failure (missing file, malformed JSON, missing keys),
        logs a warning and leaves the registry in its current state — never
        raises to the caller.

        Args:
            path: File path of the session JSON to read.
        """
        try:
            with open(path, encoding="utf-8") as fh:
                data: dict[str, Any] = json.load(fh)
            raw_skills: list[Any] = data["skills"]
            for raw in raw_skills:
                skill = self._skill_from_dict(raw)
                self.register(skill)
            logger.info(
                "Session restored from %s (%d skills)", path, len(raw_skills)
            )
        except FileNotFoundError:
            logger.warning("No session file found at %s — starting fresh", path)
        except (json.JSONDecodeError, KeyError) as exc:
            logger.warning(
                "Malformed session file at %s — starting fresh: %s", path, exc
            )

    def get_by_name(self, name: str) -> Skill | None:
        """Return the first skill whose name matches exactly, or None.

        Linear scan; first match returned when names are not unique.

        Args:
            name: Exact skill name string to search for.

        Returns:
            The first matching Skill, or None if no skill has that name.
        """
        for skill in self._store.values():
            if skill.name == name:
                return skill
        return None

    def resolve_dependencies(self, skill: Skill) -> list[Skill]:
        """Resolve the dependency skills declared in a skill's manifest.

        Reads ``skill.metadata.get("dependencies", [])`` for skill names and
        looks each up via ``get_by_name()``. Found deps are returned; missing
        ones log a WARNING directing the user to load them first. Read-only —
        does not modify the registry or the skill.

        Args:
            skill: The Skill whose declared dependencies should be resolved.

        Returns:
            List of resolved Skill objects. Empty list if the skill declares
            no dependencies or none of the declared names are in the registry.
        """
        raw_deps = skill.metadata.get("dependencies", [])
        if not isinstance(raw_deps, list):
            return []

        resolved: list[Skill] = []
        for dep_name in raw_deps:
            name_str = str(dep_name)
            dep_skill = self.get_by_name(name_str)
            if dep_skill is not None:
                resolved.append(dep_skill)
            else:
                logger.warning(
                    "Dependency %r declared by %r not found in registry"
                    " — load it with `weave load` first",
                    name_str,
                    skill.name,
                )
        return resolved

    def _skill_from_dict(self, raw: dict[str, Any]) -> Skill:
        """Reconstruct a Skill from a plain dictionary (e.g. loaded from JSON).

        Applies explicit type casts required by mypy --strict: embedding values
        are cast to float, capabilities to str, and metadata to a fresh dict.

        Args:
            raw: Dictionary with all 10 Skill field keys and JSON-compatible values.

        Returns:
            A fully constructed immutable Skill object.
        """
        return Skill(
            id=str(raw["id"]),
            name=str(raw["name"]),
            platform=str(raw["platform"]),
            source_path=str(raw["source_path"]),
            capabilities=[str(c) for c in raw["capabilities"]],
            trigger_context=str(raw["trigger_context"]),
            raw_content=str(raw["raw_content"]),
            embedding=[float(x) for x in raw["embedding"]],
            metadata=dict(raw["metadata"]),
            loaded_at=str(raw["loaded_at"]),
        )
