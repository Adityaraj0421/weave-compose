"""FastAPI application for the Weave local server (Phase 4)."""

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from weave.core.adapters.claude_code import ClaudeCodeAdapter
from weave.core.composer import WeaveComposer
from weave.core.registry import SkillRegistry
from weave.core.schema import Skill
from weave.core.selector import WeaveSelector

logger = logging.getLogger(__name__)

SESSION_FILE: str = ".weave_session.json"


class SkillResponse(BaseModel):
    """Serialisable subset of a Skill for API responses."""

    id: str
    name: str
    platform: str
    trigger_context: str
    capabilities: list[str]
    source_path: str
    loaded_at: str


class LoadRequest(BaseModel):
    """Request body for POST /load."""

    path: str
    platform: str = "claude_code"


class LoadResponse(BaseModel):
    """Response body for POST /load."""

    loaded: int
    platform: str


class QueryRequest(BaseModel):
    """Request body for POST /query."""

    query: str
    top_n: int = 1
    confidence_threshold: float = 0.1
    max_active_skills: int = 2


class QueryResult(BaseModel):
    """A single skill paired with its similarity score."""

    skill: SkillResponse
    score: float


class ComposeRequest(BaseModel):
    """Request body for POST /compose. skill_ids and scores must have equal length."""

    skill_ids: list[str]
    scores: list[float]


class ComposeResponse(BaseModel):
    """Response body for POST /compose."""

    composed: str


class StatusResponse(BaseModel):
    """Response body for GET /status."""

    total: int
    by_platform: dict[str, int]
    model: str


app = FastAPI(
    title="Weave",
    description="Local skill composition server.",
    version="0.3.0",
)

_registry: SkillRegistry = SkillRegistry()
_registry.load_session(SESSION_FILE)

# NOTE: requires internet on first run, cached after
_selector: WeaveSelector = WeaveSelector()


def _skill_to_response(skill: Skill) -> SkillResponse:
    """Map a Skill dataclass to a SkillResponse Pydantic model.

    Args:
        skill: The Skill object to convert.

    Returns:
        A SkillResponse with all API-visible fields populated.
    """
    return SkillResponse(
        id=skill.id,
        name=skill.name,
        platform=skill.platform,
        trigger_context=skill.trigger_context,
        capabilities=skill.capabilities,
        source_path=skill.source_path,
        loaded_at=skill.loaded_at,
    )


@app.get("/skills", response_model=list[SkillResponse])
def get_skills() -> list[SkillResponse]:
    """Return all skills currently loaded in the registry."""
    return [_skill_to_response(s) for s in _registry.get_all()]


@app.post("/load", response_model=LoadResponse)
def post_load(request: LoadRequest) -> LoadResponse:
    """Load skills from a directory and register them. Saves session to disk.

    Raises 400 for unsupported platform; 404 if path does not exist.
    """
    if request.platform != "claude_code":
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported platform: {request.platform!r}. Supported: claude_code",
        )
    adapter = ClaudeCodeAdapter()
    try:
        skills = adapter.load(request.path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    for skill in skills:
        _registry.register(skill)
    _registry.save_session(SESSION_FILE)
    logger.info("Loaded %d skill(s) from %s via API", len(skills), request.path)
    return LoadResponse(loaded=len(skills), platform=request.platform)


@app.post("/query", response_model=list[QueryResult])
def post_query(request: QueryRequest) -> list[QueryResult]:
    """Query the registry for the best matching skill(s).

    Raises 404 if no skills are loaded.
    """
    if _registry.count() == 0:
        raise HTTPException(status_code=404, detail="No skills loaded. Call POST /load first.")
    results = _selector.select(
        request.query,
        _registry,
        top_n=request.top_n,
        confidence_threshold=request.confidence_threshold,
        max_active_skills=request.max_active_skills,
    )
    return [QueryResult(skill=_skill_to_response(s), score=score) for s, score in results]


@app.post("/compose", response_model=ComposeResponse)
def post_compose(request: ComposeRequest) -> ComposeResponse:
    """Compose selected skills into a single merged context string.

    Raises 400 if skill_ids and scores differ in length; 404 if any id is unknown.
    """
    if len(request.skill_ids) != len(request.scores):
        raise HTTPException(status_code=400, detail="skill_ids and scores must have equal length.")
    pairs: list[tuple[Skill, float]] = []
    for skill_id, score in zip(request.skill_ids, request.scores):
        skill = _registry.get_by_id(skill_id)
        if skill is None:
            raise HTTPException(status_code=404, detail=f"Skill id not found: {skill_id!r}")
        pairs.append((skill, score))
    return ComposeResponse(composed=WeaveComposer().compose(pairs))


@app.get("/status", response_model=StatusResponse)
def get_status() -> StatusResponse:
    """Return registry status: skill count, platform breakdown, embedding model."""
    by_platform: dict[str, int] = {}
    for skill in _registry.get_all():
        by_platform[skill.platform] = by_platform.get(skill.platform, 0) + 1
    return StatusResponse(
        total=_registry.count(),
        by_platform=by_platform,
        model="all-MiniLM-L6-v2",
    )
