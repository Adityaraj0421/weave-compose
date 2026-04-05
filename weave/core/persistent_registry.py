"""Persistent skill registry backed by ChromaDB for cross-process durability."""

import json
import logging
from typing import Any

from weave.core.registry import SkillRegistry
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class PersistentRegistry(SkillRegistry):
    """ChromaDB-backed registry that survives process restarts.

    On initialisation, attempts to import ``chromadb`` and connect to a local
    persistent store at ``persist_dir``. Any skills already stored there are
    loaded into the in-memory store immediately, so queries work without a
    ``weave load`` call on subsequent runs.

    If ``chromadb`` is not installed the registry silently falls back to the
    parent ``SkillRegistry`` in-memory behaviour and logs a single warning.
    Install the optional extra to enable persistence::

        pip install weave-compose[persist]

    ChromaDB metadata fields must be scalar (``str | int | float | bool``).
    ``capabilities`` and ``skill.metadata`` are therefore stored as JSON
    strings and deserialised on retrieval.
    """

    def __init__(self, persist_dir: str = "./chroma") -> None:
        """Initialise the registry, connecting to ChromaDB if available.

        Args:
            persist_dir: Directory path for the ChromaDB persistent store.
                         Created automatically if it does not exist.
        """
        super().__init__()
        self._chromadb_available: bool = False
        self._collection: Any = None

        try:
            import chromadb

            client = chromadb.PersistentClient(path=persist_dir)
            self._collection = client.get_or_create_collection(name="weave_skills")
            self._chromadb_available = True
            self._load_from_chromadb()
            logger.info("PersistentRegistry using ChromaDB at %s", persist_dir)
        except ImportError:
            logger.warning(
                "chromadb not installed — falling back to in-memory registry. "
                "Install with: pip install weave-compose[persist]"
            )

    def register(self, skill: Skill) -> None:
        """Add or overwrite a skill in both the in-memory store and ChromaDB.

        Args:
            skill: The Skill object to register.
        """
        super().register(skill)
        if self._chromadb_available:
            self._upsert_to_chromadb(skill)

    def clear(self) -> None:
        """Remove all skills from the in-memory store and ChromaDB collection."""
        super().clear()
        if self._chromadb_available and self._collection is not None:
            try:
                result: dict[str, Any] = self._collection.get()
                all_ids: list[str] = result["ids"]
                if all_ids:
                    self._collection.delete(ids=all_ids)
                logger.info("ChromaDB collection cleared (%d entries removed)", len(all_ids))
            except Exception as exc:  # pragma: no cover
                logger.warning("Failed to clear ChromaDB collection: %s", exc)

    def _upsert_to_chromadb(self, skill: Skill) -> None:
        """Upsert a single skill into the ChromaDB collection.

        Serialises list and dict fields to JSON strings to satisfy ChromaDB's
        scalar-only metadata constraint.

        Args:
            skill: The Skill to persist.
        """
        if self._collection is None:
            return
        metadata: dict[str, Any] = {
            "name": skill.name,
            "platform": skill.platform,
            "source_path": skill.source_path,
            "trigger_context": skill.trigger_context,
            "loaded_at": skill.loaded_at,
            "capabilities_json": json.dumps(skill.capabilities),
            "skill_metadata_json": json.dumps(skill.metadata),
        }
        try:
            self._collection.upsert(
                ids=[skill.id],
                documents=[skill.raw_content],
                embeddings=[skill.embedding],
                metadatas=[metadata],
            )
        except Exception as exc:
            logger.warning("Failed to upsert skill %r to ChromaDB: %s", skill.name, exc)

    def _load_from_chromadb(self) -> None:
        """Load all existing skills from ChromaDB into the in-memory store.

        Called once during ``__init__`` to restore a previous session. Assigns
        directly to ``self._store`` to avoid triggering a redundant upsert loop
        back to ChromaDB.
        """
        if self._collection is None:
            return
        result: dict[str, Any] = self._collection.get(
            include=["documents", "embeddings", "metadatas"]
        )
        ids: list[str] = result["ids"]
        documents: list[str] = result["documents"] or []
        embeddings: list[list[float]] = result["embeddings"] or []
        metadatas: list[dict[str, Any]] = result["metadatas"] or []

        for skill_id, document, embedding, meta in zip(ids, documents, embeddings, metadatas):
            skill = self._skill_from_chromadb_row(skill_id, document, embedding, meta)
            self._store[skill.id] = skill

        logger.info("Loaded %d skill(s) from ChromaDB on init", len(ids))

    def _skill_from_chromadb_row(
        self,
        skill_id: str,
        document: str,
        embedding: list[float],
        meta: dict[str, Any],
    ) -> Skill:
        """Reconstruct a Skill from a ChromaDB row.

        Args:
            skill_id: The ChromaDB document id (equals Skill.id).
            document: The stored raw_content string.
            embedding: The stored embedding vector.
            meta: The flat ChromaDB metadata dict.

        Returns:
            A fully reconstructed immutable Skill object.
        """
        capabilities: list[str] = [
            str(c) for c in json.loads(str(meta["capabilities_json"]))
        ]
        skill_metadata: dict[str, Any] = dict(
            json.loads(str(meta["skill_metadata_json"]))
        )
        return Skill(
            id=str(skill_id),
            name=str(meta["name"]),
            platform=str(meta["platform"]),
            source_path=str(meta["source_path"]),
            capabilities=capabilities,
            trigger_context=str(meta["trigger_context"]),
            raw_content=document,
            embedding=[float(x) for x in embedding],
            metadata=skill_metadata,
            loaded_at=str(meta["loaded_at"]),
        )
