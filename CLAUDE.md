# Weave

**Platform-aware skill composition layer for AI coding tools.**

Weave is an open-source project that lets skills and plugins from different AI coding platforms (Claude Code, Cursor, Codex, Windsurf, Gemini CLI) discover each other, share context, and activate together — without the user manually managing handoffs, routing, or context injection.

> "Everyone's building skills. Weave makes them work together."

---

## What Problem Weave Solves

AI coding tools like Claude Code, Cursor, and Codex each have their own skill/plugin systems. A Claude Code skill is a `SKILL.md` file. A Cursor rule is a `.cursorrules` file. A Codex plugin has its own format. These are all isolated. If you're using two tools on the same project, or two skill sets inside the same tool, there is no coordination layer. You pick manually, you switch contexts manually, and you lose half the value of having specialized skills in the first place.

Weave is the missing coordination layer. It:

- Ingests skills from any supported platform and normalizes them into a universal schema
- Embeds every skill semantically so it can be selected by meaning, not by name
- At query time, dynamically picks the best skill(s) for the task — no manual routing
- When a task spans multiple skills, composes their contexts without contradiction or token bloat
- Works as a CLI, a config file, a local UI, and eventually as an agent-to-agent protocol

---

## Open Source Philosophy

Weave is fully open source under the MIT license. The goal is to become the standard composition layer for the AI coding tools ecosystem — the way skills talk to each other, regardless of which tool they were written for.

Contributions are welcome at every layer: new platform adapters, composition strategies, CLI improvements, UI, and documentation.

The project follows these open source principles:

- **No lock-in.** Weave does not prefer any platform. Every adapter is a first-class citizen.
- **Local-first.** Everything runs on your machine. No telemetry, no cloud dependency, no API keys required for core functionality.
- **Composable by design.** Every module is independently useful. Use just the selector. Use just an adapter. Use the whole stack.
- **Contributor-friendly.** Adding a new platform adapter should take under an hour. The base class does the heavy lifting.

---

## Git Conventions

Every chunk ends with a commit. No exceptions. This keeps the git history clean, reviewable, and useful for open source contributors reading the project's evolution.

### Commit message format

Weave uses conventional commits:

```
<type>(scope): <short description>

[optional body]
```

Types:
- `feat` — new functionality
- `fix` — bug fix
- `docs` — documentation only
- `test` — adding or updating tests
- `chore` — repo setup, CI, tooling, config
- `refactor` — code change with no behavior change

Scopes match the module or layer being changed: `schema`, `adapter`, `selector`, `composer`, `registry`, `cli`, `ci`, `docs`, `tests`, `server`, `ui`.

Examples:
```
chore(repo): initial scaffold, empty module structure
feat(schema): add Skill dataclass with validation
feat(adapter): implement BaseAdapter abstract class
feat(adapter): implement ClaudeCodeAdapter for SKILL.md files
test(adapter): add ClaudeCodeAdapter tests with fixtures
feat(cli): add weave load and weave query commands
docs(contributing): add contributor guide and adapter authoring docs
```

### Branch strategy

- `main` — always stable, always passing CI. Only receives merges at release tags.
- `dev` — active development branch. All chunk commits go here. Created in Chunk 0.1.1.
- Feature branches off `dev`: `feat/adapter-cursor`, `feat/composer`, `fix/selector-empty-registry`

**At every release tag:** merge `dev` into `main`, tag on `main`, push both:

```bash
git checkout main
git merge dev --no-ff -m "chore(release): merge dev into main for vX.X"
git tag vX.X -m "vX.X: [description]"
git push origin main
git push origin vX.X
git checkout dev
```

All day-to-day chunk commits use `dev`. Never commit directly to `main`.

---

## Project Structure

```
weave/
├── core/
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py               # Abstract base adapter
│   │   ├── claude_code.py        # Reads SKILL.md files
│   │   ├── cursor.py             # Reads .cursorrules / .mdc files
│   │   ├── codex.py              # Reads codex agent instructions
│   │   ├── windsurf.py           # Reads .windsurfrules files
│   │   └── gemini_cli.py         # Stub only until Phase 3
│   ├── __init__.py
│   ├── schema.py                 # Universal Skill object
│   ├── selector.py               # Embedding + dynamic skill selection
│   ├── composer.py               # Multi-skill context merging
│   ├── registry.py               # In-memory skill registry
│   └── detector.py               # Auto-detects platform from file structure
├── cli/
│   ├── __init__.py
│   └── main.py                   # typer CLI
├── server/                       # Phase 4 — FastAPI local server
│   ├── __init__.py
│   └── app.py
├── ui/                           # Phase 4 — React frontend
│   ├── src/
│   └── package.json
├── tests/
│   ├── fixtures/                 # Sample skill files for each platform
│   │   ├── claude_code/
│   │   ├── cursor/
│   │   ├── codex/
│   │   └── windsurf/             # .gitkeep until Wave 3.4
│   ├── test_schema.py
│   ├── test_adapters.py
│   ├── test_selector.py
│   ├── test_composer.py
│   ├── test_registry.py
│   ├── test_cli.py
│   └── test_e2e.py
├── docs/
│   ├── architecture.md
│   ├── contributing.md
│   ├── adapters.md               # How to write a new adapter
│   ├── roadmap.md
│   └── protocol.md               # Phase 5 — inter-skill protocol spec
├── examples/
│   ├── basic-composition/        # Two Claude Code skill sets composed
│   ├── cross-platform/           # Claude Code + Cursor skills together
│   └── weave.yaml.example
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── workflows/
│       ├── ci.yml                # Run tests on every PR
│       └── release.yml           # Publish to PyPI on tag
├── weave.yaml                    # User project config
├── pyproject.toml
├── LICENSE                       # MIT
├── README.md
├── CHANGELOG.md
├── CONTRIBUTORS.md
└── CLAUDE.md                     # This file
```

---

## Core Concepts

### Universal Skill Object (`core/schema.py`)

Every skill, regardless of platform, gets normalized into this:

```python
from typing import Any

@dataclass
class Skill:
    id: str                        # uuid4, generated on load
    name: str                      # human readable name
    platform: str                  # "claude_code" | "cursor" | "codex" | "windsurf"
    source_path: str               # absolute path to original file
    capabilities: list[str]        # extracted capability tags e.g. ["design", "components"]
    trigger_context: str           # natural language: what tasks this skill handles
    raw_content: str               # full original file content, unmodified
    embedding: list[float]         # computed on load via sentence-transformers
    metadata: dict[str, Any]       # platform-specific extras (version, author, etc.)
    loaded_at: str                 # ISO timestamp
```

`metadata` must be typed as `dict[str, Any]` — plain `dict` fails `mypy --strict`. Always import `Any` from `typing`.

No skill should ever be mutated after creation. Treat all Skill objects as immutable.

### Adapters (`core/adapters/`)

Each adapter reads the native format of one platform and returns `list[Skill]`.

`base.py` defines:

```python
class BaseAdapter(ABC):
    @abstractmethod
    def load(self, path: str) -> list[Skill]:
        """Load all skills from a directory or file path."""
        pass

    def detect(self, path: str) -> bool:
        """Return True if this adapter can handle files at the given path."""
        pass
```

Rules for all adapters:
- Never crash on malformed input. Log a warning and skip the file.
- If a field cannot be extracted, use a sensible default (empty list, empty string).
- `trigger_context` is the most important field — extract it carefully from description, frontmatter, or first paragraph.
- Always return a list even if empty.

### Selector (`core/selector.py`)

- On load: embed each skill's `trigger_context` + joined `capabilities` using `sentence-transformers` model `all-MiniLM-L6-v2`
- On query: embed the incoming query text, compute cosine similarity against all skill embeddings
- Return top 1 by default
- If the confidence gap between rank 1 and rank 2 is less than `confidence_threshold` (default 0.1), return both for composition
- Hard cap: never return more than `max_active_skills` (default 2, configurable)
- Expose a `explain=True` flag that prints similarity scores for debugging

### Composer (`core/composer.py`)

Takes 2-3 selected skills and produces a single merged context string.

Merge strategy (default: `dynamic`):
1. Deduplicate instructions that appear in both skills
2. Prepend the higher-confidence skill's context
3. Append the secondary skill's unique context with a separator
4. Output is a single string, ready for system prompt injection

Other strategies:
- `manual` — user specifies which skills to activate, no auto-selection
- `always-merge` — always inject all loaded skills regardless of relevance

### Registry (`core/registry.py`)

In-memory store for the current session.

```python
class SkillRegistry:
    def register(self, skill: Skill) -> None
    def get_all(self) -> list[Skill]
    def get_by_platform(self, platform: str) -> list[Skill]
    def get_by_id(self, id: str) -> Skill | None
    def clear(self) -> None
    def count(self) -> int
    def save_session(self, path: str) -> None   # serializes to .weave_session.json
    def load_session(self, path: str) -> None   # restores from .weave_session.json
```

**CLI session persistence:** The registry is in-memory, which means `weave load` and `weave query` run as separate processes — the registry would be empty for the query. To solve this, the CLI writes a `.weave_session.json` file to the current working directory after every `weave load` call, and reads it at the start of every `weave query`, `weave list`, and `weave status` call.

Session file location: `./.weave_session.json` (current working directory). Add to `.gitignore`.

Session file format:
```json
{
  "version": "1",
  "saved_at": "2026-04-04T12:00:00",
  "skills": [
    { ...Skill.to_dict() output... }
  ]
}
```

`embedding` is included in the session file so skills do not need to be re-embedded on every query. This is the primary token/time saver — embedding runs once on `weave load`, not on every `weave query`.

No persistence in the registry class itself — `save_session` and `load_session` are helpers called by the CLI layer only.

### Detector (`core/detector.py`)

Auto-detects platform from directory structure:
- Contains `SKILL.md` or `skills/` with `.md` files → `claude_code`
- Contains `.cursorrules` or `.cursor/rules/` → `cursor`
- Contains `.codex/` or `AGENTS.md` → `codex`
- Contains `.windsurfrules` → `windsurf`

Returns `"unknown"` if no match. Never crashes.

---

## CLI (`cli/main.py`)

Built with `typer`. All commands:

```bash
# Load skills from a path
weave load <path> [--platform <platform>] [--verbose]

# Query for best skill
weave query "<text>" [--explain] [--top <n>]

# Show all loaded skills
weave list [--platform <platform>]

# Show registry status
weave status

# Start watch mode from weave.yaml
weave run [--config <path>]

# Clear registry
weave clear

# Detect platform of a directory
weave detect <path>
```

---

## Config (`weave.yaml`)

```yaml
version: "1"

skills:
  - path: ./naksha-studio
    platform: claude_code
  - path: ./backend-pack
    platform: codex

composition:
  strategy: dynamic
  max_active_skills: 2
  confidence_threshold: 0.1
  model: all-MiniLM-L6-v2

output:
  verbose: false
  explain: false
```

---

## Tech Stack

| Layer | Library | Reason |
|-------|---------|--------|
| CLI | `typer` | Clean, typed, auto-generates help |
| Embeddings | `sentence-transformers` | Local, no API key, fast |
| Embedding model | `all-MiniLM-L6-v2` | 80MB, good quality, runs on CPU |
| Similarity | `numpy` | cosine similarity, no vector DB needed in v0.1 |
| Config | `pyyaml` | Standard, simple |
| Testing | `pytest` | Standard |
| Packaging | `pyproject.toml` | Modern Python packaging |
| Linting | `ruff` | Fast, replaces flake8 + isort |
| Type checking | `mypy` | Strict mode |

No external vector database in v0.1. Fully local, fully offline. ChromaDB added in Phase 4.

---

## Coding Conventions

### Language and version
- Python 3.11+ only. Use `match` statements, `X | Y` union types, `tomllib`, and other 3.11 features freely.

### Type hints
- Every function and method signature must have full type hints — no exceptions, including `__init__`
- Use `list[str]` not `List[str]`, `dict[str, Any]` not `Dict[str, Any]` (PEP 585)
- Use `X | None` not `Optional[X]` (PEP 604)
- Return type `None` must be explicit on all methods that return nothing
- No `Any` unless absolutely unavoidable — if used, add a `# type: ignore[assignment]` comment explaining why

### Docstrings
- Format: Google style. No exceptions.
- Every module, class, and public method/function gets a docstring
- Private methods (underscore prefix) get a one-line docstring minimum

```python
def load(self, path: str) -> list[Skill]:
    """Load all skills from a directory path.

    Args:
        path: Absolute or relative path to the directory containing skill files.

    Returns:
        List of normalized Skill objects. Empty list if no skills found.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
```

### Imports
Order strictly as follows, separated by blank lines:
1. stdlib (`os`, `pathlib`, `logging`, `uuid`, `datetime`)
2. third-party (`typer`, `numpy`, `yaml`, `sentence_transformers`)
3. internal (`from weave.core.schema import Skill`)

No wildcard imports (`from x import *`). Ever.

### Logging
- No `print()` in any `core/` or `server/` module. Use `logging` only.
- Each module gets its own named logger at the top: `logger = logging.getLogger(__name__)`
- Log levels: `DEBUG` for internal state, `INFO` for user-visible operations (skill loaded, registry cleared), `WARNING` for skipped files or fallbacks, `ERROR` for failures that return empty results
- CLI layer (`cli/`) may use `typer.echo()` and `typer.style()` for user-facing output

### Error handling
- Errors must always include: what failed, which file or path was involved, what was expected
- Core modules raise exceptions — they never catch and swallow silently
- CLI layer catches exceptions from core and prints them cleanly with `typer.echo(f"Error: {e}", err=True)`
- Never use bare `except:` — always catch specific exception types

```python
# Good
except FileNotFoundError as e:
    logger.warning("Skipping %s: file not found — %s", path, e)

# Bad
except Exception:
    pass
```

### File and module size
- Hard limit: 200 lines per file
- If a file approaches 180 lines, split it before it hits 200
- Splitting rule: extract the most cohesive subgroup of functions into a new module

### State
- No global mutable state outside `registry.py`
- `registry.py` is the single source of truth for session state
- All other modules are stateless — they take inputs and return outputs

### Testing
- Every public function must have at least one test
- Tests use real fixture files from `tests/fixtures/` — no mocks for file I/O
- Mock only: external network calls, system clock (use `freezegun` if needed), model inference in unit tests
- Test function names: `test_<function>_<scenario>` e.g. `test_load_returns_empty_list_for_missing_dir`
- One assertion per test where practical — split multi-assertion tests into multiple functions
- Use `pytest.raises` for exception testing, always check the message: `match="expected substring"`

### mypy strict mode
- All code must pass `mypy --strict`
- `sentence-transformers` has incomplete stubs — add `[[tool.mypy.overrides]] module = "sentence_transformers" ignore_missing_imports = true` to `pyproject.toml`
- Same override for `chromadb` in Phase 4
- Never suppress mypy errors with `type: ignore` without a comment explaining why
- `dict` without type parameters fails strict mode — always use `dict[str, Any]` and import `Any` from `typing`
- `tuple` without type parameters fails strict mode — always use `tuple[Skill, float]` etc.

### Session file (`.weave_session.json`)
- Written by `weave load`, read by `weave query`, `weave list`, `weave status`
- Always added to `.gitignore` — never committed
- When reading: wrap in try/except `json.JSONDecodeError` and `KeyError` — malformed file should log a warning and start fresh, never crash
- `embedding` field stores `list[float]` — JSON serializes this correctly via `json.dumps`
- **Critical:** when reading back from JSON, `json.loads` returns a plain `list` not `list[float]` — always cast explicitly when reconstructing the Skill: `embedding=[float(x) for x in data["embedding"]]`. Without this cast `mypy --strict` will fail on the `load_session` implementation.
- When the session file is stale (skill source files have changed since save), Weave does NOT auto-detect this in v0.1 — document this limitation in the README

### Handling mid-execution uncertainty
If Claude Code encounters something unexpected during execution — a missing dependency, an ambiguous spec, a conflict with prior code — it must **stop immediately** and report:

```
BLOCKER
-------
What I found: [description]
Which spec line is ambiguous or conflicting: [quote it]
Options I see: [list 2-3 options]
My recommendation: [one option with reason]
Waiting for your decision before continuing.
```

Do not silently pick an option and continue. Do not work around it. Stop and report.

### Session continuity
At the start of each new Claude Code session (not each chunk — each new terminal session), run:

```bash
git log --oneline -10
pytest --tb=short -q
```

Print the output before starting any chunk. This confirms what was built last session and that the codebase is still healthy.

---

## Open Source File Checklist

These files must exist before the v0.1 tag. Claude Code must create them as part of the chunks they belong to and never skip them:

- `LICENSE` — MIT, year 2026
- `README.md` — real usage, not placeholder, by v0.1
- `CHANGELOG.md` — updated at every release tag
- `CONTRIBUTORS.md` — scaffold created in Chunk 0.2.4, updated when contributors are added
- `docs/contributing.md` — full contributor guide
- `docs/adapters.md` — adapter authoring guide
- `docs/architecture.md` — high-level architecture diagram in ASCII or Mermaid
- `docs/roadmap.md` — links to release tags and what each phase delivered
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml`
- `examples/weave.yaml.example`

### CHANGELOG.md format

```markdown
# Changelog

## [v0.1] - 2026-XX-XX
### Added
- ClaudeCodeAdapter for SKILL.md files
- WeaveSelector with sentence-transformers embeddings
- CLI commands: weave load, weave query, weave list, weave status

## [Unreleased]
```

Update `CHANGELOG.md` as part of every release tag chunk. Commit message: `chore(repo): update CHANGELOG for vX.X`.

### CONTRIBUTORS.md format

```markdown
# Contributors

## Core Team
- Aditya Raj ([@Adityaraj0421](https://github.com/Adityaraj0421)) — creator

## Contributors
<!-- Added when first external PR is merged -->
```

---

## Known Library Gotchas

These are issues Claude Code will hit if not warned. Read this before every chunk that touches these libraries.

### sentence-transformers
- Model download happens on first `SentenceTransformer("all-MiniLM-L6-v2")` call — it requires internet on first run, then caches to `~/.cache/huggingface/`
- Add `# NOTE: requires internet on first run, cached after` comment wherever the model is instantiated
- mypy will fail on `sentence_transformers` imports — add the ignore override in `pyproject.toml` from day one (Chunk 0.1.2)
- `model.encode()` returns `numpy.ndarray` not `list[float]` — always call `.tolist()` before storing in the Skill object

### numpy
- `numpy` cosine similarity: always check for zero vectors before dividing — `np.linalg.norm(a) == 0` returns a numpy bool, use `float(np.linalg.norm(a)) == 0.0`
- Always import as `import numpy as np` — never `from numpy import *`

### typer
- `typer.Argument` vs `typer.Option` — paths are Arguments, flags are Options
- Always add `help=` strings to every Argument and Option — they appear in `--help`
- Use `typer.confirm()` for any destructive operation (e.g. `weave clear`)

### pyyaml
- Always use `yaml.safe_load()` — never `yaml.load()` (security risk, mypy will warn)
- Returns `None` for empty files — always guard: `config = yaml.safe_load(f) or {}`

### pytest
- Always run with `pytest -v` in REVIEW step for full output
- Use `tmp_path` fixture for any test that writes files — never write to the actual project directory in tests
- Fixture files in `tests/fixtures/` are read-only — tests must never modify them

---

---

# BUILD PLAN

---

## Phase 0 — Foundation
**Goal:** Repo exists, installs cleanly, CI runs, contributor experience is ready.
**No application logic in this phase.**

---

### Wave 0.1 — Repo Bootstrap

**Chunk 0.1.1 — Directory scaffold + Git init**
- Create the full directory and file structure as defined in Project Structure above
- All Python files: empty with module-level docstring only
- No logic, no imports beyond stdlib
- Ensure `tests/fixtures/windsurf/` directory is created with a `.gitkeep` file (fixtures added in Wave 3.4)
- Run `git init`
- Create `dev` branch: `git checkout -b dev`
- Create `.gitignore` covering: `__pycache__/`, `*.pyc`, `.env`, `dist/`, `*.egg-info/`, `.mypy_cache/`, `.ruff_cache/`, `chroma/`, `node_modules/`, `ui/dist/`, `.weave_session.json`
- Run `git add .` and commit: `chore(repo): initial scaffold, empty module structure`
- Create GitHub repo with fallback handling:

```bash
# Attempt automated repo creation
gh repo create weave-compose --public \
  --description "Platform-aware skill composition layer for AI coding tools" \
  --push

# If the above fails for any reason, print this FALLBACK block and stop:
```

```
FALLBACK — GitHub repo creation failed
---------------------------------------
Possible reasons:
  - Name "weave-compose" already taken on your account
  - gh CLI not authenticated (run: gh auth login)
  - Network issue

Manual steps to recover:
  1. Go to https://github.com/new
  2. Create a public repo named "weave-compose"
  3. Do NOT initialize with README, .gitignore, or license
  4. Then run:
       git remote add origin https://github.com/<your-username>/weave-compose.git
       git push -u origin main
       git push -u origin dev

Once done, confirm with "repo created" to continue.
```

- Push both branches with fallback handling:

```bash
git push -u origin main && git push -u origin dev

# If push fails, print this FALLBACK block and stop:
```

```
FALLBACK — Push failed
-----------------------
Possible reasons:
  - Remote origin not set (gh create may have failed silently)
  - Authentication issue

Check remote: git remote -v
If no remote is listed, add it manually:
  git remote add origin https://github.com/<your-username>/weave-compose.git
  git push -u origin main
  git push -u origin dev

Once done, confirm with "push done" to continue.
```

- All subsequent work happens on `dev` — only merge to `main` at release tags

**Chunk 0.1.2 — pyproject.toml**
- Package name: `weave-compose`
- Entry point: `weave = "weave.cli.main:app"`
- Dependencies: `typer`, `sentence-transformers`, `numpy`, `pyyaml`
- Dev dependencies: `pytest`, `ruff`, `mypy`
- Python requires: `>=3.11`
- `pip install -e .` must work after this chunk
- Commit: `chore(repo): add pyproject.toml with dependencies and entry point`
- Push: `git push`

**Chunk 0.1.3 — LICENSE + README shell**
- LICENSE: MIT, year 2026, author Weave Contributors
- README.md: name, one-line description, installation placeholder, "coming soon" usage section
- Commit: `docs(repo): add MIT license and README shell`
- Push: `git push`

**Chunk 0.1.4 — CI workflow**
- `.github/workflows/ci.yml`
- Trigger: push to `main` and `dev`, and pull_request targeting any branch — use this exact trigger block:
```yaml
on:
  push:
    branches: [main, dev]
  pull_request:
    branches: ["**"]
```
- Steps: checkout, setup Python 3.11, install deps, run ruff, run mypy, run pytest
- Must pass on empty test suite
- Commit: `chore(ci): add GitHub Actions CI workflow`
- Push: `git push`

**Chunk 0.1.5 — Verify**
- `pip install -e .` succeeds
- `weave --help` prints app name
- `pytest` exits 0
- `ruff check .` exits 0
- No commit needed — this is a verification step only

---

### Wave 0.2 — Contributing Infrastructure

**Chunk 0.2.1 — docs/contributing.md**
Write contributor guide covering:
- Dev environment setup
- How to run tests
- How to write a new adapter (point to adapters.md)
- Code style rules (ruff, mypy, docstrings, type hints, Google style)
- PR process
- Commit: `docs(contributing): add contributor guide`
- Push: `git push`

**Chunk 0.2.2 — docs/adapters.md**
Write adapter authoring guide:
- Explain `BaseAdapter` interface
- Show a minimal working adapter (20 lines)
- Explain each Skill field and what to put in it
- Show how to register it in the detector
- Commit: `docs(contributing): add adapter authoring guide`
- Push: `git push`

**Chunk 0.2.3 — docs/architecture.md**
Write architecture overview:
- ASCII diagram showing: skill files → adapters → schema → registry → selector → composer → CLI/server/UI
- One paragraph per layer explaining its role
- Note the data flow for a single query end-to-end
- Commit: `docs(architecture): add architecture overview with data flow diagram`
- Push: `git push`

**Chunk 0.2.4 — CHANGELOG.md + CONTRIBUTORS.md + roadmap.md**
- Create `CHANGELOG.md` using the format defined in Open Source File Checklist
- Create `CONTRIBUTORS.md` using the format defined in Open Source File Checklist
- Create `docs/roadmap.md` listing all 5 phases, their release tags, and what each delivers — update this file at every release tag
- Commit: `docs(repo): add CHANGELOG, CONTRIBUTORS, and roadmap scaffolds`
- Push: `git push`

**Chunk 0.2.5 — GitHub issue templates**
- `bug_report.md`: platform, steps to reproduce, expected vs actual, logs
- `feature_request.md`: problem statement, proposed solution, alternatives
- Commit: `chore(repo): add GitHub issue templates`
- Push: `git push`

**Chunk 0.2.6 — Test fixtures**
Create sample skill files in `tests/fixtures/`:
- `claude_code/naksha_design.md` — realistic SKILL.md for a design skill
- `claude_code/backend_api.md` — realistic SKILL.md for a backend skill
- `cursor/frontend.cursorrules` — realistic Cursor rules file
- `codex/devops.md` — realistic Codex agent instruction file
- These fixtures are used by every test. Make them realistic, not placeholder text.
- Commit: `test(fixtures): add realistic skill fixtures for all supported platforms`
- Push: `git push`

---

## Phase 1 — Core Engine
**Goal:** Skills can be loaded, normalized, embedded, and queried from the CLI.
**This is the v0.1 release target.**

---

### Wave 1.1 — Schema

**Chunk 1.1.1 — Skill dataclass**
- Implement `core/schema.py` exactly as defined in Core Concepts
- Use `@dataclass` with `frozen=True` (immutable)
- Add `__repr__` that shows name, platform, capability count
- Add `to_dict()` for serialization
- Commit: `feat(schema): add Skill dataclass with frozen=True and to_dict()`
- Push: `git push`

**Chunk 1.1.2 — Schema validation**
- Add `validate()` method — checks required fields are non-empty
- Raises `ValueError` with descriptive message if invalid
- Does not mutate the object
- Commit: `feat(schema): add validate() method with descriptive errors`
- Push: `git push`

**Chunk 1.1.3 — Schema tests**
- Test: valid skill creation
- Test: `to_dict()` round-trips correctly
- Test: `validate()` raises on missing name
- Test: `validate()` raises on missing platform
- Test: `validate()` raises on empty raw_content
- Commit: `test(schema): add Skill dataclass and validation tests`
- Push: `git push`

---

### Wave 1.2 — Base Adapter

**Chunk 1.2.1 — BaseAdapter**
- Implement `core/adapters/base.py`
- Abstract class with `load(path)` and `detect(path)`
- Add `_generate_id()` helper returning uuid4 string
- Add `_extract_capabilities(text: str) -> list[str]` — simple keyword extraction, no ML
- Add `_timestamp() -> str` returning current ISO timestamp
- Commit: `feat(adapter): add BaseAdapter abstract class with helper methods`
- Push: `git push`

**Chunk 1.2.2 — Base adapter tests**
- Test: cannot instantiate BaseAdapter directly
- Test: `_generate_id()` returns unique values
- Test: `_timestamp()` returns valid ISO format
- Commit: `test(adapter): add BaseAdapter tests`
- Push: `git push`

---

### Wave 1.3 — Claude Code Adapter

**Chunk 1.3.1 — Claude Code adapter**
- Implement `core/adapters/claude_code.py`
- Reads SKILL.md files from a directory (recursive scan)
- Parses YAML frontmatter if present (name, description fields)
- Falls back to: filename as name, first paragraph as trigger_context
- Extracts capabilities from description frontmatter or first 200 chars of body
- Sets `platform = "claude_code"`
- Handles: missing frontmatter, empty files, non-UTF8 (skip with warning)
- Commit: `feat(adapter): implement ClaudeCodeAdapter for SKILL.md files`
- Push: `git push`

**Chunk 1.3.2 — Claude Code adapter tests**
- Uses fixtures from `tests/fixtures/claude_code/`
- Test: loads all SKILL.md files from a directory
- Test: correctly parses frontmatter name
- Test: falls back to filename when no frontmatter
- Test: handles empty file without crashing
- Test: handles directory with no SKILL.md files (returns empty list)
- Test: `detect()` returns True for directory with SKILL.md files
- Commit: `test(adapter): add ClaudeCodeAdapter tests`
- Push: `git push`

---

### Wave 1.4 — Registry

**Chunk 1.4.1 — SkillRegistry**
- Implement `core/registry.py` exactly as defined in Core Concepts
- Internal storage: `dict[str, Skill]` keyed by `skill.id`
- All methods type-hinted
- `register()` logs at INFO level
- `save_session(path: str) -> None` — serializes all skills to `.weave_session.json` using `Skill.to_dict()`
- `load_session(path: str) -> None` — restores skills from `.weave_session.json`, re-registers each one
- Handle missing or malformed session file gracefully: log a warning, start with empty registry
- Commit: `feat(registry): add SkillRegistry with save_session and load_session`
- Push: `git push`

**Chunk 1.4.2 — Registry tests**
- Test: register and retrieve by id
- Test: get_by_platform filters correctly
- Test: clear empties registry
- Test: count returns correct number
- Test: duplicate id overwrites (last write wins)
- Test: `save_session` writes a valid JSON file to `tmp_path`
- Test: `load_session` restores skills including embeddings
- Test: `load_session` on missing file logs warning and leaves registry empty
- Commit: `test(registry): add SkillRegistry tests including session persistence`
- Push: `git push`

---

### Wave 1.5 — Selector

**Chunk 1.5.1 — Embedder**
- Implement `core/selector.py`
- `SentenceTransformerEmbedder` class
- Model: `all-MiniLM-L6-v2`, loaded once, cached as class attribute
- `embed(text: str) -> list[float]`
- `embed_skill(skill: Skill) -> list[float]` — concatenates trigger_context + capabilities
- Lazy load model on first use, not on import
- Commit: `feat(selector): add SentenceTransformerEmbedder with lazy model loading`
- Push: `git push`

**Chunk 1.5.2 — Cosine similarity**
- `cosine_similarity(a: list[float], b: list[float]) -> float` using numpy
- Returns value between -1 and 1
- Handles zero vectors gracefully (returns 0.0)
- Commit: `feat(selector): add cosine_similarity utility`
- Push: `git push`

**Chunk 1.5.3 — WeaveSelector**
- `select(query, registry, top_n, confidence_threshold) -> list[tuple[Skill, float]]`
- Returns (Skill, score) tuples sorted by score descending
- If top_n=1 but second result is within confidence_threshold of first, return both
- Never returns more than max_active_skills (default 2)
- `explain=True` prints score table to stdout
- Commit: `feat(selector): implement WeaveSelector with dynamic multi-skill selection`
- Push: `git push`

**Chunk 1.5.4 — Selector tests**
- Test: returns correct skill for clear query (design query → design skill)
- Test: returns two skills when scores are close
- Test: returns empty list when registry is empty
- Test: explain flag does not crash
- Use real fixtures — load actual skill files, not mocks
- Commit: `test(selector): add WeaveSelector tests using real fixtures`
- Push: `git push`

---

### Wave 1.6 — CLI v0.1

**Chunk 1.6.1 — `weave load`**
- Calls detector if platform not specified
- Loads skills via correct adapter
- Registers all skills in registry
- Calls `registry.save_session(".weave_session.json")` after loading
- Prints: "Loaded N skills from <path> (platform: <platform>)"
- Prints: "Session saved to .weave_session.json"
- Verbose: prints each skill name and capability count
- Commit: `feat(cli): add weave load command with session persistence`
- Push: `git push`

**Chunk 1.6.2 — `weave query`**
- At startup: calls `registry.load_session(".weave_session.json")` if the file exists
- If no session file and no skills loaded: print clear error — "No skills loaded. Run `weave load <path>` first."
- Prints: skill name, platform, trigger_context, score
- `--explain` prints all scores
- Commit: `feat(cli): add weave query command with session restore`
- Push: `git push`

**Chunk 1.6.3 — `weave list`**
- At startup: restores session from `.weave_session.json` if it exists
- Table: name, platform, capabilities
- `--platform` filter
- Count at bottom
- Commit: `feat(cli): add weave list command`
- Push: `git push`

**Chunk 1.6.4 — `weave status`**
- At startup: restores session from `.weave_session.json` if it exists
- Total skills loaded, breakdown by platform, embedding model in use
- Shows session file path and last saved timestamp if session exists
- Commit: `feat(cli): add weave status command`
- Push: `git push`

**Chunk 1.6.5 — `weave clear`**
- Clears in-memory registry
- Deletes `.weave_session.json` if it exists
- Requires `typer.confirm()` before deleting: "Clear all loaded skills? [y/N]"
- Commit: `feat(cli): add weave clear command with session cleanup`
- Push: `git push`

**Chunk 1.6.6 — CLI tests**
- `tests/test_cli.py` using `typer.testing.CliRunner`
- Test: `weave load` with valid path succeeds and creates session file
- Test: `weave load` with invalid path prints error
- Test: `weave query` with no session file prints correct error message
- Test: `weave query` returns a result after loading (restores session)
- Test: `weave clear` deletes session file
- Commit: `test(cli): add CLI command tests including session persistence`
- Push: `git push`

---

### Wave 1.7 — v0.1 Verification

**Chunk 1.7.1 — End-to-end test**
- `tests/test_e2e.py`
- Load two Claude Code skill sets from fixtures
- Query design task → design skill returned
- Query backend task → backend skill returned
- Commit: `test(e2e): add end-to-end test for v0.1 core flow`
- Push: `git push`

**Chunk 1.7.2 — README update**
- Installation: `pip install weave-compose`
- Quickstart: 3 commands that actually work
- How it works: 3-sentence explanation
- Link to contributing guide
- Commit: `docs(readme): update README with real v0.1 usage`
- Push: `git push`

**Chunk 1.7.3 — v0.1 checklist**
Before tagging v0.1:
- [ ] `pip install -e .` succeeds from clean env
- [ ] `weave load ./tests/fixtures/claude_code` works
- [ ] `weave query "design a component"` returns correct skill
- [ ] `pytest` passes with 0 failures
- [ ] `ruff check .` passes
- [ ] `mypy --strict .` passes
- [ ] README reflects real functionality
- [ ] All files in Open Source File Checklist exist
- [ ] Update `CHANGELOG.md` with v0.1 release notes
- Commit: `chore(repo): update CHANGELOG for v0.1`
- Merge and tag:
```bash
git checkout main && git merge dev --no-ff -m "chore(release): merge dev into main for v0.1"
git tag v0.1 -m "v0.1: Claude Code adapter, selector, CLI load + query"
git push origin main && git push origin v0.1
git checkout dev
```

---

## Phase 2 — Composition Engine
**Goal:** Weave composes multiple skills together and injects a merged context.

---

### Wave 2.1 — Composer

**Chunk 2.1.1 — WeaveComposer**
- Implement `core/composer.py`
- `compose(skills: list[tuple[Skill, float]]) -> str`
  - Deduplicates overlapping lines
  - Higher-score skill content goes first
  - Separator between skills: `\n\n---\n\n`
- `compose_minimal(skills) -> str`
  - Only trigger_context + capabilities, not full raw_content
  - For tight context windows
- Commit: `feat(composer): implement WeaveComposer with dynamic and minimal strategies`
- Push: `git push`

**Chunk 2.1.2 — Composer tests**
- Test: single skill returns raw_content unchanged
- Test: two skills both present in output
- Test: duplicate lines appear only once
- Test: higher-score skill appears first
- Test: compose_minimal is shorter than compose
- Commit: `test(composer): add WeaveComposer tests`
- Push: `git push`

---

### Wave 2.2 — Config Support

**Chunk 2.2.1 — Config loader**
- Reads `weave.yaml` from current dir or `--config` flag
- Validates required fields
- Applies composition settings to selector and composer
- Commit: `feat(cli): add weave.yaml config loader`
- Push: `git push`

**Chunk 2.2.2 — `weave run`**
- Loads all skills from weave.yaml
- Starts interactive query loop (readline)
- Each line entered is treated as a query
- Prints selected skill(s) and merged context
- Ctrl+C to exit
- Commit: `feat(cli): add weave run interactive mode`
- Push: `git push`

**Chunk 2.2.3 — weave.yaml.example**
- `examples/weave.yaml.example` with comments on every field
- Commit: `docs(examples): add annotated weave.yaml.example`
- Push: `git push`

**Chunk 2.2.4 — Config tests**
- Test: valid weave.yaml loads without error
- Test: missing required field raises descriptive error
- Test: unknown platform raises error
- Commit: `test(cli): add config loader tests`
- Push: `git push`

---

### Wave 2.3 — Multi-Skill Selection

**Chunk 2.3.1 — Parallel activation strategies**
- Extend WeaveSelector for `always-merge` strategy (return all skills)
- `manual` strategy: accept skill names, return those by name lookup
- Commit: `feat(selector): add always-merge and manual activation strategies`
- Push: `git push`

**Chunk 2.3.2 — Composition output flag**
- `weave query --output composed` prints full merged context
- This is what gets injected into the AI tool
- Commit: `feat(cli): add --output composed flag to weave query`
- Push: `git push`

**Chunk 2.3.3 — Integration test**
- Load Claude Code skill set + Codex skill set
- Query a task spanning both
- Assert both skills selected
- Assert composed output contains content from both
- Update `CHANGELOG.md` with v0.2 release notes
- Commit: `test(e2e): add multi-skill composition integration test`
- Merge and tag:
```bash
git checkout main && git merge dev --no-ff -m "chore(release): merge dev into main for v0.2"
git tag v0.2 -m "v0.2: Composer, config, weave run"
git push origin main && git push origin v0.2
git checkout dev
```

---

## Phase 3 — Multi-Platform Adapters
**Goal:** Weave works with Cursor, Codex, and Windsurf out of the box.

---

### Wave 3.1 — Detector

**Chunk 3.1.1 — Platform detector**
- Implement `core/detector.py`
- `detect_platform(path: str) -> str`
- Checks directory contents against known patterns as defined in Core Concepts
- Commit: `feat(detector): implement platform auto-detection`
- Push: `git push`

**Chunk 3.1.2 — Detector tests**
- Test: detects claude_code from SKILL.md
- Test: detects cursor from .cursorrules
- Test: returns "unknown" for empty directory
- Test: does not crash on non-existent path
- Commit: `test(detector): add platform detection tests`
- Push: `git push`

**Chunk 3.1.3 — `weave detect` CLI command**
- Implement `weave detect <path>` in `cli/main.py`
- Calls `detect_platform(path)` and prints: "Detected platform: <platform>" or "Unknown platform — could not detect from directory contents"
- Test: `weave detect` on a claude_code fixture dir prints correct platform
- Test: `weave detect` on empty dir prints unknown message
- Commit: `feat(cli): add weave detect command`
- Push: `git push`

---

### Wave 3.2 — Cursor Adapter

**Chunk 3.2.1 — Cursor adapter**
- Reads `.cursorrules` (plain text rule lists)
- Reads `.cursor/rules/*.mdc` (MDC format with frontmatter)
- Extracts description from MDC frontmatter as trigger_context
- Falls back to first paragraph for .cursorrules
- `platform = "cursor"`
- Commit: `feat(adapter): implement CursorAdapter for .cursorrules and .mdc files`
- Push: `git push`

**Chunk 3.2.2 — Cursor fixtures + tests**
- `tests/fixtures/cursor/` with 2 realistic sample files
- Same test coverage pattern as Claude Code adapter
- Commit: `test(adapter): add CursorAdapter fixtures and tests`
- Push: `git push`

---

### Wave 3.3 — Codex Adapter

**Chunk 3.3.1 — Codex adapter**
- Reads `AGENTS.md` and `.codex/*.md` files
- Parses agent name and instructions
- `platform = "codex"`
- Commit: `feat(adapter): implement CodexAdapter for AGENTS.md files`
- Push: `git push`

**Chunk 3.3.2 — Codex fixtures + tests**
- `tests/fixtures/codex/` with 2 realistic sample files
- Commit: `test(adapter): add CodexAdapter fixtures and tests`
- Push: `git push`

---

### Wave 3.4 — Windsurf Adapter

**Chunk 3.4.1 — Windsurf adapter**
- Reads `.windsurfrules` files
- Same pattern as Cursor plain text rules
- `platform = "windsurf"`
- Commit: `feat(adapter): implement WindsurfAdapter for .windsurfrules files`
- Push: `git push`

**Chunk 3.4.2 — Windsurf fixtures + tests**
- `tests/fixtures/windsurf/` with 2 realistic sample files
- Commit: `test(adapter): add WindsurfAdapter fixtures and tests`
- Push: `git push`

---

### Wave 3.5 — Cross-Platform + PyPI Release

**Chunk 3.5.1 — Cross-platform end-to-end test**
- Load one skill from each of: claude_code, cursor, codex
- Query tasks matching each platform's strengths
- Assert correct platform's skill returned each time
- Assert cross-platform composition works
- Commit: `test(e2e): add cross-platform adapter integration tests`
- Push: `git push`

**Chunk 3.5.2 — examples/cross-platform/**
- Working example showing Claude Code + Cursor skills composing together
- README inside the example explaining what it demonstrates
- Commit: `docs(examples): add cross-platform composition example`
- Push: `git push`

**Chunk 3.5.3 — PyPI release prep**
- `.github/workflows/release.yml` — publish to PyPI on `v*` tag
- Update pyproject.toml with classifiers, homepage, repository links
- `pip install weave-compose` must work after this
- Update `CHANGELOG.md` with v0.3 release notes
- Commit: `chore(ci): add PyPI release workflow and update package metadata`
- Merge and tag:
```bash
git checkout main && git merge dev --no-ff -m "chore(release): merge dev into main for v0.3"
git tag v0.3 -m "v0.3: All platform adapters, PyPI release"
git push origin main && git push origin v0.3
git checkout dev
```

---

## Phase 4 — Persistence + UI
**Goal:** Skills persist between sessions. Visual composer for non-technical users.

---

### Wave 4.1 — Persistence

**Chunk 4.1.1 — ChromaDB integration**
- Add `chromadb` as optional: `pip install weave-compose[persist]`
- `PersistentRegistry` extending `SkillRegistry`
- Stores embeddings and metadata in local ChromaDB collection
- Falls back to in-memory if ChromaDB not installed
- Commit: `feat(registry): add PersistentRegistry with ChromaDB backend`
- Push: `git push`

**Chunk 4.1.2 — Session persistence**
- `weave load --persist` saves to ChromaDB
- `weave run --persist` reloads saved skills on startup
- `weave clear --persist` drops the collection
- Commit: `feat(cli): add --persist flag to load, run, and clear commands`
- Push: `git push`

**Chunk 4.1.3 — Persistence tests**
- Test: skills survive process restart when persisted
- Test: in-memory mode still works without chromadb
- Commit: `test(registry): add persistence and fallback tests`
- Push: `git push`

---

### Wave 4.2 — Local Server

**Chunk 4.2.1 — FastAPI server**
- `server/app.py`
- `GET /skills` — list all loaded skills
- `POST /load` — load skills from path
- `POST /query` — query for best skill(s)
- `POST /compose` — compose selected skills
- `GET /status` — registry status
- Commit: `feat(server): add FastAPI local server with core endpoints`
- Push: `git push`

**Chunk 4.2.2 — `weave serve`**
- New CLI command: `weave serve [--port 7842]`
- Starts FastAPI on localhost
- Prints URL on startup
- Commit: `feat(cli): add weave serve command`
- Push: `git push`

**Chunk 4.2.3 — Server tests**
- Test each endpoint with `httpx` test client
- Commit: `test(server): add FastAPI endpoint tests`
- Push: `git push`

---

### Wave 4.3 — UI

**Chunk 4.3.1 — React scaffold**
- `ui/` with Vite + React + TypeScript + Tailwind
- Connects to local FastAPI server
- Commit: `chore(ui): scaffold React + Vite + Tailwind frontend`
- Push: `git push`

**Chunk 4.3.2 — Skill browser**
- Card grid of all loaded skills
- Filter by platform
- Click card to see full content
- Commit: `feat(ui): add skill browser with platform filter`
- Push: `git push`

**Chunk 4.3.3 — Visual composer**
- Query input at top
- Shows matched skills with confidence scores
- Composed output in a code block with copy button
- Commit: `feat(ui): add visual composer with query input and composed output`
- Push: `git push`

**Chunk 4.3.4 — Load panel**
- Directory path input to load skills
- Shows loading progress and skill count
- Update `CHANGELOG.md` with v0.4 release notes
- Commit: `feat(ui): add skill load panel`
- Merge and tag:
```bash
git checkout main && git merge dev --no-ff -m "chore(release): merge dev into main for v0.4"
git tag v0.4 -m "v0.4: Persistence, local server, UI"
git push origin main && git push origin v0.4
git checkout dev
```

---

## Phase 5 — Agent-to-Agent Protocol
**Goal:** Skills can discover and call each other without human involvement.

---

### Wave 5.1 — Weave Protocol Spec

**Chunk 5.1.1 — Protocol document**
Write `docs/protocol.md`:
- Define inter-skill protocol
- How a skill advertises capabilities
- How a skill requests another skill's context
- JSON schema for advertisement and request/response
- Commit: `docs(protocol): define Weave inter-skill protocol spec`
- Push: `git push`

**Chunk 5.1.2 — Skill manifest**
- `weave.skill.json` as optional sidecar for any skill
- Fields: name, version, capabilities, trigger_patterns, author
- Adapters read this if present, prefer it over parsed content
- Commit: `feat(schema): add weave.skill.json manifest support in all adapters`
- Push: `git push`

---

### Wave 5.2 — Runtime Coordination

**Chunk 5.2.1 — Skill dependencies**
- Skills declare `dependencies: [skill_name]` in manifest
- Weave resolves dependencies at load time
- When skill A is selected, dependencies also injected at lower weight
- Commit: `feat(registry): add dependency resolution at skill load time`
- Push: `git push`

**Chunk 5.2.2 — Conflict resolution**
- Detect when two skills give contradictory instructions
- Detection: semantic similarity above 0.9 with opposing sentiment
- Strategy: prefer higher-confidence skill, log the conflict
- Update `CHANGELOG.md` with v1.0 release notes
- Commit: `feat(composer): add conflict detection and resolution`
- Merge and tag:
```bash
git checkout main && git merge dev --no-ff -m "chore(release): merge dev into main for v1.0"
git tag v1.0 -m "v1.0: Agent-to-agent protocol, skill manifests, conflict resolution"
git push origin main && git push origin v1.0
git checkout dev
```

---

## What NOT to Build

Explicitly out of scope until further decision:

- No cloud sync or remote skill registry
- No telemetry or usage tracking of any kind
- No authentication layer (local tool)
- No LLM calls inside Weave itself (Weave never calls any AI API)
- No GUI installer — CLI only until Phase 4
- No Windows-specific code paths (support via WSL)
- No Gemini CLI adapter until community contribution or Phase 5
- No skill marketplace UI until post-v1.0

---

## Release Tags

| Tag | Phase complete | What ships |
|-----|---------------|------------|
| `v0.1` | Phase 1 | Claude Code adapter, selector, CLI load + query |
| `v0.2` | Phase 2 | Composer, config, weave run |
| `v0.3` | Phase 3 | All platform adapters, PyPI release |
| `v0.4` | Phase 4 | Persistence, local server, UI |
| `v1.0` | Phase 5 | Agent-to-agent protocol, skill manifests |

---

## How to Work With Claude Code

Always give Claude Code one chunk at a time. Use this exact format:

> "Read CLAUDE.md fully. Then begin Phase X, Wave X.Y, Chunk X.Y.Z. Follow the full RPERC protocol. Do not proceed to the next chunk until I confirm."

Never ask Claude Code to execute multiple chunks at once. The chunk boundaries exist specifically to give you review checkpoints.

---

## The RPERC Protocol

Every single chunk — no exceptions — must follow this five-step protocol in order. Claude Code must not skip or compress any step.

---

### Step 1 — RESEARCH

Before writing a single line of code, Claude Code must:

- Read the specific chunk section in CLAUDE.md (not the whole file — just the relevant phase/wave/chunk)
- Read every file that this chunk will create or modify
- Read every file that this chunk depends on (imports, base classes, fixtures)
- Check `git log --oneline -5` to confirm what was built in prior chunks
- Run `pytest -q` to confirm the baseline is currently passing
- List what already exists vs what needs to be created
- Identify any conflicts, missing dependencies, or gaps between the spec and current state
- Check the Known Library Gotchas section for any libraries this chunk touches

Output format:

```
RESEARCH
--------
Chunk: [Phase X, Wave X.Y, Chunk X.Y.Z — title]
Files to create: [list]
Files to modify: [list]
Files read: [list]
Last 5 commits: [paste git log output]
Baseline test status: [X passed / failing — paste failures]
Dependencies confirmed: [list]
Potential conflicts: [list or "none"]
Library gotchas that apply: [list or "none"]
Notes from prior chunks: [any relevant context]
```

Claude Code must print this block and wait. Do not proceed until you reply "plan".

---

### Step 2 — PLAN

After research is confirmed, Claude Code must write a plain-English implementation plan:

- What each file will contain after this chunk is done
- What functions/classes will be added and their signatures
- What tests will be written and what they assert
- What the commit message will be
- Any deviations from the spec being proposed, with justification

Output format:

```
PLAN
----
[File name]
  - [What's being added]
  - [Key function/class signatures]

[Test file name]
  - [Test: description of what it asserts]

Commit message: [exact conventional commit string]

Deviations from spec: [list or "none"]
```

Claude Code must print this block and wait. Do not proceed until you reply "execute".

---

### Step 3 — EXECUTE

Only after "execute" is confirmed:

- Implement exactly what was described in the plan
- No scope creep — do not add anything not in the plan
- No refactoring of prior chunks unless the plan explicitly includes it
- If something unexpected comes up mid-execution, stop and report it — do not silently work around it

---

### Step 4 — REVIEW

A chunk is only done when ALL of the following are true:
- `pytest -v` exits 0 with no failures or warnings
- `ruff check .` exits 0 with no issues
- `mypy --strict .` exits 0 with no errors
- Every bullet point in the chunk spec is implemented
- No files exceed 200 lines
- All new public functions have docstrings in Google style
- All new functions have type hints

Immediately after execution, before committing, Claude Code must run all checks and produce:

Output format:

```
REVIEW
------
pytest:     [X passed, 0 failed — or paste failures in full]
ruff:       [clean — or paste issues in full]
mypy:       [clean — or paste errors in full]
Line counts: [list any file over 150 lines as a warning]

Spec compliance (every bullet from the chunk):
  [x] [spec bullet 1 — implemented]
  [x] [spec bullet 2 — implemented]
  [ ] [spec bullet 3 — NOT implemented — reason: ...]

Docstrings: [all present / missing on: ...]
Type hints: [all present / missing on: ...]
Library gotchas handled: [list or "n/a"]
Edge cases handled: [list or "none"]
Fragile areas / manual checks needed: [list or "none"]
Deviations from plan: [list or "none"]
```

If any check fails, fix it before printing the REVIEW block. Do not print a REVIEW block with known failures and ask to commit anyway.

Claude Code must print this block and wait. Do not proceed until you reply "commit".

---

### Step 5 — COMMIT

Only after "commit" is confirmed:

```bash
git add .
git commit -m "<exact message from plan>"
git push
```

Then print:

```
COMMITTED
---------
Commit: [hash] — [message]
Branch: [branch name]
Files changed: [list]
Next chunk: Phase X, Wave X.Y, Chunk X.Y.Z — [chunk title]
```

---

## Chunk Trigger Template

Copy and paste this to start any chunk:

```
Read CLAUDE.md — specifically the Coding Conventions, Known Library Gotchas, and Phase X / Wave X.Y / Chunk X.Y.Z sections. Then begin the RPERC protocol:

1. RESEARCH — run `git log --oneline -5` and `pytest -q` first, then print research block, wait for "plan"
2. PLAN — print plan block with exact function signatures and commit message, wait for "execute"
3. EXECUTE — implement only what's in the plan, stop and report any blockers immediately
4. REVIEW — run pytest/ruff/mypy --strict, check every spec bullet, print review block, wait for "commit"
5. COMMIT — commit and push only after I say "commit", print commit summary

Do not proceed past any step without my confirmation.
If anything is ambiguous or conflicts with prior code, print a BLOCKER block and wait.
```

---

## Recovery Commands

If Claude Code completes work but skips the protocol:

```bash
# Check what was changed
git diff

# Check test status manually
pytest
ruff check .
mypy .

# Commit manually using the chunk's specified message
git add .
git commit -m "<type>(scope): <description from chunk>"
git push
```

Use `git log --oneline` at any time to verify the commit history is progressing cleanly chunk by chunk.
