# GitHub Copilot Instructions — AdResearchAI

## Project Context

AdResearchAI is a Python/FastAPI service that reverse-engineers advertisements using GPT-4o (vision + text) and Whisper. It ingests image/video/audio/text ads and returns structured analysis covering persuasion techniques, target demographics, emotional triggers, brand positioning, and messaging strategy.

---

## Stack

- **Python 3.11+** with full type annotations (`from __future__ import annotations` in every file)
- **FastAPI** — async routes, Pydantic v2 schemas, Depends() for injection
- **SQLAlchemy 2.x** — async ORM with `AsyncSession`
- **Pydantic v2** — `model_config = ConfigDict(...)`, not class `Config`
- **OpenAI Python SDK v1+** — `from openai import AsyncOpenAI`
- **Celery 5+** with Redis broker
- **pytest + pytest-asyncio** — `asyncio_mode = "auto"` in pyproject.toml
- **ruff** for linting, **black** for formatting

---

## Coding Conventions

- All database access via `AsyncSession` — never use sync SQLAlchemy
- All OpenAI calls in `src/services/analyzer.py` only — never inline in routes
- URL inputs must pass through `src/utils/ssrf.py:validate_url()` before any HTTP request
- Config only from `src/core/config.py:get_settings()` — never `os.environ` directly
- Pydantic response models on all FastAPI routes — never return raw `dict`
- Raise `HTTPException` only in route handlers — services raise domain exceptions
- Use `asyncio.gather()` for concurrent calls, never `await` in a loop when calls are independent

---

## Testing Conventions

- Write tests BEFORE implementation (red/green TDD)
- Unit tests: no DB, no network — mock all external calls
- Integration tests: use FastAPI `TestClient` (httpx-based), test DB via SQLite or test Postgres
- Fixture files (sample images, audio) live in `tests/fixtures/` — committed to repo
- Snapshot tests for prompt output in `test_prompt_builder.py`
- Every new service method must have at least one unit test

---

## Boundaries (Do NOT do these unless explicitly asked)

- Do not refactor working code in a PR that's adding a new feature
- Do not remove, skip (`@pytest.mark.skip`), or comment out existing tests
- Do not change `pyproject.toml` dependencies without being asked
- Do not add `print()` statements — use `structlog.get_logger()` instead
- Do not hardcode API keys, URLs, or credentials — always use `get_settings()`
- Do not use `requests` library — use `httpx.AsyncClient` for all HTTP calls
- Do not call `openai` client directly from routes — always go through `analyzer.py`
- Do not expose raw exception messages or stack traces in API responses
