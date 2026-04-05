"""Tests for the Weave FastAPI local server endpoints."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from weave.core.schema import Skill
from weave.server.app import _registry, app

CLAUDE_FIXTURES: str = str(Path(__file__).parent / "fixtures" / "claude_code")


@pytest.fixture(autouse=True)
def reset_registry() -> None:
    """Clear the module-level registry before each test for isolation."""
    _registry.clear()


@pytest.fixture
def client() -> TestClient:
    """Return a synchronous FastAPI TestClient for endpoint tests."""
    return TestClient(app)


@pytest.fixture
def skill() -> Skill:
    """Return a pre-built Skill with a known embedding for server tests."""
    return Skill(
        id="srv-test-001",
        name="Server Test Skill",
        platform="claude_code",
        source_path="/tmp/srv_test.md",
        capabilities=["server", "testing"],
        trigger_context="Test skill for server endpoint validation",
        raw_content="# Server Test Skill\nServer test content here.",
        embedding=[0.1, 0.2, 0.3],
        metadata={},
        loaded_at="2026-04-05T10:00:00+00:00",
    )


# ---------------------------------------------------------------------------
# GET /skills
# ---------------------------------------------------------------------------


def test_get_skills_empty_returns_empty_list(client: TestClient) -> None:
    """GET /skills returns an empty list when no skills are registered."""
    response = client.get("/skills")
    assert response.status_code == 200
    assert response.json() == []


def test_get_skills_after_registration_returns_skills(
    client: TestClient, skill: Skill
) -> None:
    """GET /skills returns all registered skills as SkillResponse objects."""
    _registry.register(skill)
    response = client.get("/skills")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == skill.name
    assert data[0]["platform"] == skill.platform


# ---------------------------------------------------------------------------
# POST /load
# ---------------------------------------------------------------------------


def test_post_load_valid_path_returns_loaded_count(client: TestClient) -> None:
    """POST /load with a valid fixture path returns loaded count and platform."""
    response = client.post(
        "/load", json={"path": CLAUDE_FIXTURES, "platform": "claude_code"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["loaded"] >= 1
    assert data["platform"] == "claude_code"


def test_post_load_invalid_platform_returns_400(client: TestClient) -> None:
    """POST /load with an unsupported platform returns 400."""
    response = client.post(
        "/load", json={"path": CLAUDE_FIXTURES, "platform": "gemini"}
    )
    assert response.status_code == 400
    assert "Unsupported platform" in response.json()["detail"]


def test_post_load_nonexistent_path_returns_404(client: TestClient) -> None:
    """POST /load with a non-existent directory path returns 404."""
    response = client.post("/load", json={"path": "/nonexistent/path/to/skills"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# POST /query
# ---------------------------------------------------------------------------


def test_post_query_empty_registry_returns_404(client: TestClient) -> None:
    """POST /query with no skills loaded returns 404 with a helpful message."""
    response = client.post("/query", json={"query": "design a component"})
    assert response.status_code == 404
    assert "No skills loaded" in response.json()["detail"]


def test_post_query_returns_skill_with_score(client: TestClient) -> None:
    """POST /query after loading skills returns QueryResult objects with scores."""
    client.post("/load", json={"path": CLAUDE_FIXTURES})
    response = client.post("/query", json={"query": "design a UI component"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "skill" in data[0]
    assert "score" in data[0]
    assert isinstance(data[0]["score"], float)


# ---------------------------------------------------------------------------
# POST /compose
# ---------------------------------------------------------------------------


def test_post_compose_returns_composed_string(
    client: TestClient, skill: Skill
) -> None:
    """POST /compose returns a non-empty composed context string."""
    _registry.register(skill)
    response = client.post(
        "/compose", json={"skill_ids": [skill.id], "scores": [0.95]}
    )
    assert response.status_code == 200
    data = response.json()
    assert "composed" in data
    assert len(data["composed"]) > 0


def test_post_compose_mismatched_lengths_returns_400(client: TestClient) -> None:
    """POST /compose with unequal skill_ids and scores lists returns 400."""
    response = client.post(
        "/compose", json={"skill_ids": ["id-1", "id-2"], "scores": [0.9]}
    )
    assert response.status_code == 400
    assert "equal length" in response.json()["detail"]


def test_post_compose_unknown_id_returns_404(client: TestClient) -> None:
    """POST /compose with an unknown skill_id returns 404."""
    response = client.post(
        "/compose", json={"skill_ids": ["nonexistent-id"], "scores": [0.9]}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# GET /status
# ---------------------------------------------------------------------------


def test_get_status_empty_registry(client: TestClient) -> None:
    """GET /status with empty registry returns zero totals and model name."""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["by_platform"] == {}
    assert data["model"] == "all-MiniLM-L6-v2"


def test_get_status_with_skills_returns_platform_breakdown(
    client: TestClient, skill: Skill
) -> None:
    """GET /status with a registered skill shows correct total and breakdown."""
    _registry.register(skill)
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["by_platform"]["claude_code"] == 1
