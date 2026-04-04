# Contributing to Weave

Thanks for your interest in contributing! Weave is fully open source under the MIT license. Contributions are welcome at every layer: new platform adapters, composition strategies, CLI improvements, UI, and documentation.

**GitHub:** https://github.com/Adityaraj0421/weave-compose

---

## Dev Environment Setup

**Prerequisites:** Python 3.11+, git. `gh` CLI is optional but useful for PRs.

```bash
git clone https://github.com/Adityaraj0421/weave-compose.git
cd weave-compose
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the package in editable mode along with all dev dependencies (`pytest`, `ruff`, `mypy`).

---

## Running Tests

```bash
pytest --tb=short -q             # run all tests
pytest tests/test_schema.py -v   # run a single file with full output
```

> **Note:** Exit code 5 means "no tests collected" — this is not a failure. It occurs when test files exist but contain no test functions yet.

Fixture files live in `tests/fixtures/` and are read-only. Tests must never write to or modify them.

---

## Writing a New Adapter

Adapters are how Weave ingests skills from a new platform. Each adapter reads the platform's native file format and returns a list of normalized `Skill` objects.

To add support for a new platform:

1. Create `weave/core/adapters/<platform>.py` extending `BaseAdapter`
2. Implement `load(path: str) -> list[Skill]` and `detect(path: str) -> bool`
3. Register the platform pattern in `weave/core/detector.py`
4. Add fixture files in `tests/fixtures/<platform>/`
5. Add tests in `tests/test_adapters.py`

See **[docs/adapters.md](adapters.md)** for the full authoring guide with a minimal working example.

---

## Code Style

All code must pass `ruff check .` and `mypy --strict .` with zero errors before opening a PR.

### Linting and type checking

```bash
ruff check .       # linting — must exit 0
mypy --strict .    # type checking — must exit 0
```

### Type hints

Every function and method signature must be fully annotated — including `__init__` and methods that return `None`:

```python
# Good
def register(self, skill: Skill) -> None: ...
def get_by_id(self, id: str) -> Skill | None: ...

# Bad
def register(self, skill): ...
```

Use PEP 585 built-in generics (`list[str]`, `dict[str, Any]`) not `List`/`Dict` from `typing`. Use `X | None` not `Optional[X]`.

### Docstrings

Google style on every module, class, and public method:

```python
def load(self, path: str) -> list[Skill]:
    """Load all skills from a directory path.

    Args:
        path: Absolute or relative path to the directory.

    Returns:
        List of normalized Skill objects. Empty if none found.

    Raises:
        FileNotFoundError: If the path does not exist.
    """
```

Private methods (underscore prefix) get a one-line docstring minimum.

### Imports

Three groups, separated by blank lines, in this order:

```python
import os
import pathlib

import numpy as np
import yaml

from weave.core.schema import Skill
```

No wildcard imports (`from x import *`) — ever.

### Logging

No `print()` in `core/` or `server/` modules. Use `logging`:

```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Embedding skill: %s", skill.name)
logger.warning("Skipping %s: could not parse frontmatter", path)
```

Log levels: `DEBUG` for internal state, `INFO` for user-visible operations, `WARNING` for skipped files, `ERROR` for failures.

---

## Pull Request Process

- **Target branch:** `dev` — never open a PR against `main`
- **Commit format:** conventional commits — `<type>(scope): <description>`
- **Types:** `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
- **Scopes:** `schema`, `adapter`, `selector`, `composer`, `registry`, `cli`, `ci`, `docs`, `tests`, `server`, `ui`
- Keep PRs focused — one logical change per PR
- CI must pass (`ruff` + `mypy` + `pytest`) before merge

Example commit messages:

```
feat(adapter): implement CursorAdapter for .cursorrules files
test(adapter): add CursorAdapter tests with fixtures
docs(adapters): add Cursor adapter to authoring guide
```

---

## Questions

Open an issue on GitHub: https://github.com/Adityaraj0421/weave-compose/issues
