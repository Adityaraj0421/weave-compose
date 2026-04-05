# Known Limitations

This document lists known gaps in Weave v1.0 so users can find workarounds
quickly and avoid filing duplicate issues. Each limitation includes the reason
it exists and, where possible, a path forward.

---

## Session File Staleness

Weave writes `.weave_session.json` once when you run `weave load`. It does not
watch the filesystem or detect when source skill files change on disk after
that point. If you edit a `SKILL.md`, `.cursorrules`, or any other skill file,
the session is stale — Weave will continue using the old embeddings and
metadata until you reload.

**Workaround:** Re-run `weave load <path>` after modifying any skill file.
This re-embeds and overwrites the session file in full.

**Why:** Auto-detection via filesystem watching was explicitly out of scope for
v0.1 to keep the session model simple. The CLI is stateless by design — it
reads and writes a flat JSON file rather than running a background daemon.

---

## No Gemini CLI Adapter

`core/adapters/gemini_cli.py` is a stub. Gemini CLI skills are not loaded,
detected, or composed in any release through v1.0.

**Workaround:** None currently. Gemini CLI users cannot load skills from that
platform.

**Path forward:** This is an explicitly open community contribution target.
The adapter interface is simple — see [docs/adapters.md](adapters.md) for a
guide to writing a new adapter in under an hour. A Gemini CLI adapter would
be a welcome first PR.

---

## Embeddings Require Internet on First Run

Weave uses `sentence-transformers` with the `all-MiniLM-L6-v2` model (~80 MB).
On the very first run of `weave load`, the model is downloaded from
Hugging Face and cached to `~/.cache/huggingface/`. All subsequent runs are
fully offline.

**Workaround:** Run `weave load` once on a machine with internet access. After
the model is cached, Weave works entirely offline — including in air-gapped
environments, as long as the cache directory is present.

---

## No Windows Native Support

Weave is developed and tested on macOS and Linux. There are no
Windows-specific code paths. Running Weave natively on Windows (outside WSL)
is untested and unsupported.

**Workaround:** Use [WSL (Windows Subsystem for Linux)](https://learn.microsoft.com/en-us/windows/wsl/).
Weave works correctly inside a WSL environment with Python 3.11+.

**Why:** Supporting Windows natively would require testing infrastructure and
path-handling changes that are out of scope for the current maintainer
bandwidth. WSL provides a practical solution for Windows users without adding
complexity to the codebase.

---

## UI Requires `weave serve` to Be Running

The React UI (`ui/`) communicates with the local FastAPI server at
`http://localhost:7842`. It does not start the server automatically — both
processes must be launched independently.

**Workaround:** Open two terminals:

```bash
# Terminal 1
weave serve

# Terminal 2
cd ui && npm run dev
```

The UI will be available at `http://localhost:5173` once both are running.

**Why:** Auto-starting a background server from the UI process would require
a process manager or daemon, which adds significant complexity and
platform-specific behaviour. Keeping them separate makes each independently
restartable and debuggable.
