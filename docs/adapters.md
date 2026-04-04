# Adapter Authoring Guide

Adapters are the extension point for new platforms in Weave. Each adapter reads one platform's native skill format and normalizes it into the universal `Skill` schema. Adding a new adapter is the most common contribution — it should take under an hour using this guide.

---

## The BaseAdapter Interface

Every adapter extends `BaseAdapter` from `weave/core/adapters/base.py`:

```python
class BaseAdapter(ABC):
    @abstractmethod
    def load(self, path: str) -> list[Skill]:
        """Load all skills from a directory or file path."""
        ...

    def detect(self, path: str) -> bool:
        """Return True if this adapter can handle files at the given path."""
        ...
```

**Contract rules — all adapters must follow these:**

- **Never crash on malformed input.** Log a warning with `logger.warning(...)` and skip the file.
- **Use sensible defaults for unextractable fields.** Empty list for `capabilities`, empty string for `trigger_context` rather than raising.
- **`trigger_context` is the most important field.** Extract it carefully from frontmatter, description fields, or the first paragraph of content. The quality of skill selection depends on it.
- **Always return a list, even if empty.** Never return `None`.

---

## The Skill Schema

Every adapter must produce `Skill` objects. Here is what to put in each field:

| Field            | Type             | What to put here                                         |
|------------------|------------------|----------------------------------------------------------|
| `id`             | `str`            | UUID4 — call `self._generate_id()` (inherited)           |
| `name`           | `str`            | Human-readable name, e.g. from frontmatter or filename   |
| `platform`       | `str`            | Your platform string e.g. `"claude_code"`, `"cursor"`    |
| `source_path`    | `str`            | Absolute path to the source file — `str(file.resolve())` |
| `capabilities`   | `list[str]`      | Keyword tags e.g. `["design", "components", "react"]`    |
| `trigger_context`| `str`            | Natural language: what tasks this skill handles          |
| `raw_content`    | `str`            | Full original file content, completely unmodified        |
| `embedding`      | `list[float]`    | Always `[]` — the selector fills this on first query     |
| `metadata`       | `dict[str, Any]` | Platform-specific extras: author, version, tags, etc.    |
| `loaded_at`      | `str`            | ISO timestamp — call `self._timestamp()` (inherited)     |

> **Why `embedding=[]`?** Adapters are pure I/O — they never run ML. The `WeaveSelector` computes and caches embeddings from `trigger_context` + `capabilities` when the registry is first queried.

---

## Minimal Working Adapter

A complete adapter for a hypothetical platform that stores skills as `.skill.txt` files. Exactly 20 lines of implementation:

```python
import logging
from pathlib import Path
from typing import Any

from weave.core.adapters.base import BaseAdapter
from weave.core.schema import Skill

logger = logging.getLogger(__name__)


class PlainTextAdapter(BaseAdapter):
    """Adapter for .skill.txt plain-text skill files."""

    def detect(self, path: str) -> bool:
        """Return True if any .skill.txt files exist at path."""
        return any(Path(path).glob("*.skill.txt"))

    def load(self, path: str) -> list[Skill]:
        """Load all .skill.txt files from a directory."""
        skills: list[Skill] = []
        for file in Path(path).glob("*.skill.txt"):
            try:
                content = file.read_text(encoding="utf-8")
            except OSError as e:
                logger.warning("Skipping %s: %s", file, e)
                continue
            skills.append(Skill(
                id=self._generate_id(),
                name=file.stem,
                platform="plain_text",
                source_path=str(file.resolve()),
                capabilities=[],
                trigger_context=content[:200],  # fallback: first 200 chars
                raw_content=content,
                embedding=[],
                metadata={},
                loaded_at=self._timestamp(),
            ))
        return skills
```

**Key points:**
- `_generate_id()` and `_timestamp()` are helpers inherited from `BaseAdapter` — no need to implement them
- `trigger_context=content[:200]` is the fallback strategy — real adapters parse frontmatter or a dedicated description field
- `metadata={}` is fine for a minimal adapter; add platform-specific fields as needed (e.g. `{"author": "..."}`)

---

## Registering in the Detector

`weave/core/detector.py` auto-detects a platform by inspecting directory contents before `load()` is called. Add your platform's file signature pattern:

```python
# Inside detect_platform(path: str) -> str:
p = Path(path)

if any(p.glob("*.skill.txt")):
    return "plain_text"
```

Detection order matters — place more specific patterns before generic ones.

The `detect()` method on your adapter serves the same purpose but is called at runtime when the user explicitly passes `--platform`. Both should agree.

---

## Checklist for a New Adapter

Before opening a PR:

- [ ] Create `weave/core/adapters/<platform>.py` extending `BaseAdapter`
- [ ] Implement `load(path: str) -> list[Skill]` — handles missing files, encoding errors, empty dirs
- [ ] Implement `detect(path: str) -> bool` — returns `True` only for your platform's files
- [ ] Add detection pattern in `weave/core/detector.py`
- [ ] Add at least 2 realistic fixture files in `tests/fixtures/<platform>/`
- [ ] Add tests in `tests/test_adapters.py` — load, detect, fallback, empty dir cases
- [ ] All tests pass: `pytest --tb=short -q`
- [ ] Linting and types clean: `ruff check . && mypy --strict .`
- [ ] Open a PR targeting `dev`

See [contributing.md](contributing.md) for the full PR process and code style rules.
