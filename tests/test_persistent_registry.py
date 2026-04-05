"""Tests for PersistentRegistry: ChromaDB persistence and in-memory fallback."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from weave.core.persistent_registry import PersistentRegistry
from weave.core.schema import Skill


@pytest.fixture
def skill() -> Skill:
    """Return a fully-populated Skill with a known embedding for persistence tests."""
    return Skill(
        id="persist-test-001",
        name="Persistent Test Skill",
        platform="claude_code",
        source_path="/tmp/persist_test.md",
        capabilities=["persistence", "testing"],
        trigger_context="Test skill for persistence layer validation",
        raw_content="# Persistent Test Skill\nContent for persistence tests.",
        embedding=[0.1, 0.2, 0.3],
        metadata={"author": "Test Author"},
        loaded_at="2026-04-05T10:00:00+00:00",
    )


def test_persistent_registry_skills_survive_process_restart(
    skill: Skill, tmp_path: Path
) -> None:
    """Skills registered in one PersistentRegistry instance are visible in the next.

    Simulates a process restart by creating two separate PersistentRegistry
    instances pointing at the same persist_dir. The second instance represents
    a new process — it must load the skill from ChromaDB automatically on init.
    Skipped when chromadb is not installed.
    """
    pytest.importorskip("chromadb")

    persist_dir = str(tmp_path / "chroma")

    # First "process": register the skill, which upserts to ChromaDB.
    registry1 = PersistentRegistry(persist_dir=persist_dir)
    registry1.register(skill)
    assert registry1.count() == 1

    # Second "process": new instance, same persist_dir — must auto-load from ChromaDB.
    registry2 = PersistentRegistry(persist_dir=persist_dir)
    assert registry2.count() == 1

    restored = registry2.get_by_id(skill.id)
    assert restored is not None
    assert restored.name == skill.name
    assert restored.embedding == [0.1, 0.2, 0.3]


def test_persistent_registry_fallback_without_chromadb(
    skill: Skill, tmp_path: Path
) -> None:
    """PersistentRegistry falls back to in-memory SkillRegistry when chromadb is absent.

    Forces the ImportError path by injecting None into sys.modules for chromadb,
    regardless of whether chromadb is actually installed in the environment.
    All SkillRegistry operations (register, count, clear) must still work correctly.
    """
    persist_dir = str(tmp_path / "chroma")

    with patch.dict(sys.modules, {"chromadb": None}):
        registry = PersistentRegistry(persist_dir=persist_dir)

    assert not registry._chromadb_available
    assert registry._collection is None

    registry.register(skill)
    assert registry.count() == 1

    registry.clear()
    assert registry.count() == 0
