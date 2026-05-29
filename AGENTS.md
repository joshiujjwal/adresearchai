# AGENTS.md — AdResearchAI

## Setup

```bash
# Requirements: Python 3.11+, Docker, ffmpeg on PATH

# 1. Install project + dev deps
pip install -e ".[dev]"

# 2. Configure environment
cp .env.example .env
# Required: OPENAI_API_KEY, DATABASE_URL, REDIS_URL, SECRET_KEY

# 3. Start infrastructure
docker-compose up -d db redis

# 4. Apply DB migrations
alembic upgrade head

# 5. Verify setup
pytest tests/unit/test_config.py -v
```

---

## Running Tests

```bash
# All tests
pytest

# Unit tests only (fast, no infra needed)
pytest tests/unit/ -v

# Integration tests (requires docker-compose services up)
pytest tests/integration/ -v

# With coverage report
pytest --cov=src --cov-report=term-missing

# Single file
pytest tests/unit/test_analyzer.py -v -s
```

**Always run `pytest` before committing. Never push a red test.**

---

## Code Style

### Python Version
- Target Python 3.11+. Use `match/case`, `TypeAlias`, `Self` where appropriate.

### Typing
- Full type annotations on all functions and methods — no `Any` unless wrapping untyped third-party code
- Use `from __future__ import annotations` in every file

### Imports
- Absolute imports only: `from src.services.analyzer import AdAnalyzer`
- Group order (enforced by ruff): stdlib → third-party → local
- No wildcard imports

### Async
- All I/O-bound code must be `async def`
- Use `asyncio.gather()` for concurrent independent coroutines
- Never call blocking I/O (file, network, DB) from sync context

### Naming
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private helpers: `_single_leading_underscore`
- Pydantic models for API: suffix with `Request` or `Response` (e.g. `AnalyzeRequest`, `AnalysisResponse`)

### FastAPI
- Router per resource in `src/api/routes/`
- Inject dependencies via `Depends()` — no globals
- Use `status_code=` explicitly on every route decorator
- All response models must be Pydantic schemas (never return raw dicts)

### Error Responses
- Use `HTTPException(status_code=..., detail="human-readable message")`
- Detail strings must not expose internal paths, stack traces, or secrets

---

## TDD Instructions

1. **Write the test first** — make it fail (red)
2. **Commit the failing test**: `git commit -m "test: [description]"`
3. **Implement** the feature until the test passes (green)
4. **Commit the implementation**: `git commit -m "feat: [description]"`
5. **Refactor** if needed, keeping tests green
6. Never delete or skip a test to make the suite pass

### Mocking Rules
- Mock OpenAI client at the `httpx` transport layer, or use `unittest.mock.patch("src.services.analyzer.openai_client")`
- Mock `yt-dlp` calls with fixture file copies
- Use `pytest-mock`'s `mocker` fixture, not `unittest.mock.patch` directly

---

## PR Instructions

Every PR description must include:

```
## What
[one sentence]

## Why
[one sentence]

## Evidence
- [ ] `pytest` output pasted or screenshot
- [ ] Manual test performed: [describe what you tested]
- [ ] Relevant `curl` commands or Postman snapshots if API changed

## Checklist
- [ ] Tests written first (red → green)
- [ ] `ruff check . && black --check .` passes
- [ ] No secrets or API keys in code or logs
- [ ] CLAUDE.md updated if new convention discovered
```

- PRs must be small and focused: one feature or fix per PR
- Don't refactor unrelated code in a feature PR
- Don't remove existing tests unless the feature they test is explicitly removed
