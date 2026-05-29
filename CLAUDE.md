# CLAUDE.md — AdResearchAI

> Context file for AI coding agents. Keep under 200 lines. Update when you discover non-obvious conventions.

---

## Commands

```bash
# Install (dev mode with all extras)
pip install -e ".[dev]"

# Dev server (auto-reload)
uvicorn src.api.main:app --reload --port 8000

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_analyzer.py -v

# Lint
ruff check .

# Format check
black --check .

# Fix lint + format
ruff check . --fix && black .

# Start dependencies
docker-compose up -d db redis

# Stop dependencies
docker-compose down
```

---

## Directory Map

```
src/
  api/
    main.py          # FastAPI app factory, lifespan, middleware registration
    routes/          # One file per resource: ads.py, auth.py, batches.py, tasks.py
    deps.py          # FastAPI dependency injectors (get_db, get_current_user)
    middleware.py    # Rate limiting, request ID, CORS
  core/
    config.py        # Pydantic Settings — all config from env vars, never hardcoded
    logging.py       # structlog setup — always structured JSON in prod, pretty in dev
    database.py      # SQLAlchemy async engine + session factory
    security.py      # JWT encode/decode helpers
  models/
    ad.py            # Ad ORM model
    analysis.py      # Analysis ORM model
    task.py          # Task ORM model
    schemas.py       # All Pydantic request/response schemas
  services/
    ingestor.py      # Ingestion orchestrator — validates input, downloads media, saves Ad row
    analyzer.py      # LLM orchestrator — builds prompts, calls OpenAI, parses response
    reporter.py      # Converts raw LLM dict → validated AnalysisResult schema
  utils/
    media.py         # yt-dlp, Pillow, ffmpeg helpers
    prompt_builder.py # Prompt construction per source_type
    ssrf.py          # URL validation + private IP range blocking
tests/
  unit/              # Fast, no DB, no network — mock everything external
  integration/       # Uses TestClient + in-memory SQLite or test DB
  fixtures/          # Small sample media files for tests (committed to repo)
```

---

## Workflow

1. **Read TODO.md** — find the next unchecked task in the current phase
2. **Run existing tests first**: `pytest` — never break what's already passing
3. **Write failing tests** (red) — commit with message `test: [what you're testing]`
4. **Implement** until tests pass (green) — commit with message `feat: [what you built]`
5. **Lint + format**: `ruff check . --fix && black .`
6. **Review diff manually** before pushing — read every line changed
7. **Update this file** if you discovered something non-obvious

---

## Key Conventions

### Config
- All settings live in `src/core/config.py` as a `Settings(BaseSettings)` class
- Load with `get_settings()` (cached singleton via `@lru_cache`)
- Never import `os.environ` directly anywhere else

### Database
- Use `AsyncSession` everywhere — no sync SQLAlchemy
- DB sessions injected via `Depends(get_db)` in route handlers
- Migrations via Alembic: `alembic revision --autogenerate -m "description"`

### OpenAI Calls
- All OpenAI calls go through `src/services/analyzer.py` — no direct client usage in routes
- Use `response_format={"type": "json_object"}` — always parse with `json.loads()`
- Wrap every OpenAI call in try/except for `openai.APITimeoutError`, `openai.RateLimitError`

### Async Tasks
- Celery tasks defined in `src/tasks/` — one file per resource
- Tasks call services, not routes or models directly
- Use `task.apply_async()` — never `task.delay()` in tests (use `.apply()` for sync testing)

### Error Handling
- Raise `HTTPException` in routes only
- Services raise domain exceptions from `src/core/exceptions.py`
- Route handler catches domain exceptions → maps to HTTP status codes

### SSRF Protection
- Always pass URLs through `src/utils/ssrf.py:validate_url()` before any HTTP request
- Blocks: private IPs (10.x, 172.16–31.x, 192.168.x), localhost, file:// schemes

---

## Gotchas

- `yt-dlp` requires `ffmpeg` on PATH — install system-wide, not via pip
- Pillow's `Image.open()` is lazy — call `.load()` or use as context manager to avoid file handle leaks
- Celery workers need `PYTHONPATH=.` set to import `src.*` correctly
- `pytest-asyncio` requires `asyncio_mode = "auto"` in `pyproject.toml` — already configured
- OpenAI vision calls expect base64 PNG/JPEG — always re-encode, never trust uploaded format
- structlog must be configured before first log call — done in `src/core/logging.py` imported by `main.py`
