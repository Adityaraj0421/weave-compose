# Changelog

## [v0.1] - 2026-04-05

### Added
- `Skill` dataclass (`frozen=True`) with `to_dict()`, `validate()`, and `__repr__`
- `BaseAdapter` abstract class with `_generate_id()`, `_timestamp()`, and `_extract_capabilities()` helpers
- `ClaudeCodeAdapter` for SKILL.md files with YAML frontmatter parsing and graceful fallbacks
- `SkillRegistry` in-memory store with `save_session()` / `load_session()` for `.weave_session.json` persistence
- `WeaveSelector` using `sentence-transformers` (`all-MiniLM-L6-v2`) and cosine similarity for semantic skill selection
- Dynamic multi-skill selection: when confidence gap between top two skills is below threshold, both are returned for composition
- CLI commands: `weave load`, `weave query`, `weave list`, `weave status`, `weave clear`
- Cross-process session persistence: `weave load` saves session; `weave query`, `weave list`, `weave status` restore it automatically — no re-embedding on every query
- End-to-end tests: design query → Naksha Design System; backend query → Backend API Engineer
- Full test suite: 38 tests across schema, adapters, registry, selector, CLI, and e2e modules
- Realistic Claude Code fixtures: `naksha_design.md` (design system) and `backend_api.md` (REST API)
- Open source scaffold: LICENSE (MIT), README, CHANGELOG, CONTRIBUTORS, docs/, GitHub issue templates, CI workflow

## [Unreleased]
