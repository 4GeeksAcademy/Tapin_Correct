**Summary:**

- **Repo:** `Tapin_Correct` (backend under `src/backend`).
- **Goal:** Hand off to a Claude agent to finish resolving editor diagnostics (pylint/flake8), run tests, and stabilize imports and linting so CI/test runs cleanly under Python 3.13.

**What I changed recently:**

- **LLM integration:** Added a clean implementation `src/backend/event_discovery/llm_impl.py` and replaced the corrupted `llm.py` with a minimal shim `src/backend/event_discovery/llm.py` that re-exports `HybridLLM`.
- **Cache manager:** `src/backend/event_discovery/cache_manager.py` updated to import the clean `HybridLLM`.
- **Tests/CI:** `src/backend/tests/conftest.py` updated to default `LLM_PROVIDER=mock` for tests; `.github/workflows/backend-ci.yml` updated to use Python 3.13 and mock provider.
- **Env / local:** Added `.env.example` and `scripts/check_ollama.py` + `docs/OLLAMA.md` to help set up local Ollama HTTP fallback.

**Current high-level problems visible in the editor diagnostics:**

- Many **pylint import errors** like `E0401` and `E0402` (e.g. "Attempted relative import beyond top-level package", "Unable to import 'app'", "Unable to import 'event_discovery.cache_manager'"). These are typically caused by the language server / pylint running without `src` on `PYTHONPATH`.
- **Flake8 / pycodestyle** complaints about lines longer than 79 characters (E501) across multiple files, notably:
  - `src/backend/event_discovery/cache_manager.py`
  - `src/backend/event_discovery/state_nonprofits.py`
  - `src/backend/alembic/versions/*` migration files
- **Pylint warnings** about catching broad `Exception` and style conventions (missing docstrings, invalid module naming in Alembic versions) — many are informational and can be triaged.
- Editor selection showed a possible incomplete import: `from email.message import` (verify `src/backend/app.py` top-of-file for any stray broken import lines).

**Files to inspect first (priority):**

- `src/backend/app.py` — verify top imports (editor selection suggested a broken `from email.message import` line). Ensure imports match actual symbols used.
- `src/backend/event_discovery/cache_manager.py` — fix long lines and remove relative-import issues if required.
- `src/backend/event_discovery/llm.py` and `src/backend/event_discovery/llm_impl.py` — verify `llm.py` shim and that `llm_impl` contains the canonical `HybridLLM` implementation.
- `src/backend/alembic/env.py` — Alembic errors complaining about `alembic.context` members may be analyzer artifact; run migrations/ale mbic in proper environment to confirm.
- `src/backend/alembic/versions/*.py` — migration files flagged for long lines and naming conventions (these are generated files; long lines can be wrapped but names usually left as-is).

**Concrete commands for Claude to run locally (macOS / zsh):**

- Quick syntax check for `app.py`:

```bash
python3 -m py_compile src/backend/app.py
```

- Run tests (use `src` as import root and ensure tests use `LLM_PROVIDER=mock`):

```bash
export PYTHONPATH=src
export LLM_PROVIDER=mock
python3 -m pytest -q
```

- Run flake8 and pylint (run from repo root; pass PYTHONPATH):

```bash
export PYTHONPATH=src
flake8 src/backend --max-line-length=79
pylint --load-plugins=pylint.extensions.docparams src/backend
```

(Adjust pylint flags to your environment; the key is running with `PYTHONPATH=src` so imports resolve.)

**Suggested quick fixes / priorities for the Claude agent:**

1. Verify `src/backend/app.py` top-of-file import — fix any incomplete import lines (e.g. replace broken `from email.message import` with `from email.message import EmailMessage`).
2. Configure/lint run with `PYTHONPATH=src` to avoid false-positive import errors. If the analyzer can't be reconfigured, add a small `sys.path` hack in top-level scripts used by static checks (or instruct the team to set VSCode `python.analysis.extraPaths` to include `${workspaceFolder}/src`).
3. Wrap or shorten long lines in files flagged by Flake8 (`state_nonprofits.py`, `cache_manager.py`, and migrations).
4. Triage broad-exception catches: where practical, narrow the exception class; where the broad catch is intentional for robustness (LLM initialization, optional imports), leave but add a comment explaining why.
5. Confirm `llm_impl` async/sync behavior: run tests that exercise the LLM fallback path (mock Ollama HTTP endpoint or unit test using `responses`/`httpx` mocking).
6. Run the full test suite under Python 3.13 and fix failing tests.

**Notes about environment & analyzer mismatches:**

- Most `Unable to import` / `Attempted relative import beyond top-level package` errors are caused by the editor/linters running without `src` on `PYTHONPATH`. The canonical fix is to run tools with `PYTHONPATH=src` or set the project's python path in IDE settings.
- Alembic env scripts sometimes import the application module; if running static analysis on those scripts directly, consider guarding imports or adding `sys.path` manipulation inside `alembic/env.py` to allow static analyzers to resolve imports.

**Current TODOs (hand-off):**

- [ ] Fix any stray incomplete import in `src/backend/app.py` (editor selection indicated `from email.message import`).
- [ ] Re-run linters/tests with `PYTHONPATH=src` and capture failure list.
- [ ] Shorten lines flagged by Flake8 (E501) in `cache_manager.py`, `state_nonprofits.py`, and migrations.
- [ ] Resolve or document `pylint` import false-positives (either configure analyzer or add `sys.path` handling).
- [ ] Add unit test(s) to mock Ollama HTTP fallback for `HybridLLM`.

**Files I changed recently (so Claude can skip re-editing unless needed):**

- `src/backend/event_discovery/llm_impl.py` (new, clean HybridLLM)
- `src/backend/event_discovery/llm.py` (shim re-export)
- `src/backend/event_discovery/cache_manager.py` (updated import)
- `src/backend/tests/conftest.py` (defaults LLM_PROVIDER=mock)
- `.github/workflows/backend-ci.yml` (set Python 3.13, LLM_PROVIDER=mock)
- `scripts/check_ollama.py`, `docs/OLLAMA.md`, `.env.example`

**Hand-off instructions for Claude (succinct):**

- Start by running the commands above (syntax check, pytest, flake8, pylint) with `PYTHONPATH=src`.
- Fix `app.py` incomplete import if present; then re-run `python -m py_compile`.
- Triage the lint failures (prioritize import errors and E501 long lines). Document or commit fixes.
- Add or run tests to validate `HybridLLM` HTTP fallback.

**Where I left off:**

- LLM module was recovered into `llm_impl.py` and consumers updated; tests are configured to avoid external premium APIs by default. Static/editor diagnostics remain and likely need the `PYTHONPATH` fix or line-wrapping edits.

---

If you want, I can now:

- run the syntax check and tests locally (I will set `PYTHONPATH=src`),
- or apply automated line wrap fixes to the most offending files (I can attempt minimal safe wraps to meet 79-char width).

Tell me which of those to do next and I will proceed.
