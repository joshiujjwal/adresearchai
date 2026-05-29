# AdResearchAI — Task Breakdown

## How to Use This File

Work one task at a time. For every task:
1. **Write failing tests first** (red phase) — commit them
2. **Implement until tests pass** (green phase) — commit
3. **Review the diff manually** before pushing
4. **Update CLAUDE.md or AGENTS.md** if you discovered a non-obvious convention
5. **Gate each phase**: don't start Phase N+1 until all Phase N tests are green and you've reviewed the output manually

---

## Phase 0: Foundation ⬜

- [ ] `pyproject.toml` — define project metadata, dependencies, dev deps, ruff + black config
- [ ] `.env.example` — template for `OPENAI_API_KEY`, `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `ENV`
- [ ] `src/core/config.py` — Pydantic `Settings` class loading from env (no hardcoded secrets)
- [ ] `src/core/logging.py` — structured JSON logging via `structlog`
- [ ] `docker-compose.yml` — PostgreSQL 16 + Redis 7 services, named volumes
- [ ] `Dockerfile` — multi-stage build (builder → runtime), non-root user
- [ ] GitHub Actions CI: `.github/workflows/ci.yml` — ruff, black, pytest on push/PR
- [ ] First smoke test: `tests/unit/test_config.py` — settings load correctly from env
- [ ] Verify: `pytest tests/unit/test_config.py` passes ✅
- [ ] **GATE**: All Phase 0 tests green + CI passing before Phase 1

---

## Phase 1: Core Ingestion Pipeline ⬜

- [ ] **Spec review**: read `docs/spec.md` before writing any code
- [ ] `src/models/ad.py` — `Ad` ORM model (id, source_type, source_url, raw_text, media_path, status, created_at)
- [ ] `src/models/schemas.py` — Pydantic schemas: `AdCreate`, `AdResponse`, `AnalysisResult`
- [ ] `tests/unit/test_ad_model.py` — model validation tests (red)
- [ ] `src/services/ingestor.py` — accepts URL (image/video/webpage) or raw text, downloads/extracts media, saves to DB
- [ ] `tests/unit/test_ingestor.py` — unit tests with mocked HTTP calls and file I/O (red → green)
- [ ] `src/utils/media.py` — yt-dlp wrapper, Pillow resize/encode, ffmpeg audio extraction
- [ ] `tests/unit/test_media_utils.py` — test with fixture files in `tests/fixtures/`
- [ ] `src/api/routes/ads.py` — `POST /ads/ingest` endpoint
- [ ] `tests/integration/test_ingest_api.py` — httpx TestClient tests (red → green)
- [ ] Manual test: POST a real YouTube ad URL, confirm media downloaded and DB row created
- [ ] **GATE**: Ingest pipeline end-to-end working with evidence screenshot

---

## Phase 2: AI Analysis Engine ⬜

- [ ] `src/utils/prompt_builder.py` — build structured prompts for each analysis dimension
- [ ] `tests/unit/test_prompt_builder.py` — snapshot tests for prompt output (red → green)
- [ ] `src/services/analyzer.py` — orchestrates OpenAI GPT-4o calls (vision for images, text for copy, Whisper for audio)
- [ ] `tests/unit/test_analyzer.py` — mock OpenAI client, test each dimension extractor (red → green)
- [ ] `src/models/analysis.py` — `Analysis` ORM model (ad_id, dimensions JSON, model_used, tokens_used, created_at)
- [ ] Wire `POST /ads/{id}/analyze` — triggers async Celery task
- [ ] `tests/integration/test_analyze_api.py` — test endpoint returns 202 Accepted + task ID
- [ ] `src/services/reporter.py` — assembles raw LLM output into structured `AnalysisResult` schema
- [ ] Manual test: analyze a Nike ad, review each dimension in response JSON
- [ ] **GATE**: Full analysis pipeline returning structured JSON for at least 3 real ads

---

## Phase 3: API Polish & Retrieval ⬜

- [ ] `GET /ads` — paginated list of ingested ads
- [ ] `GET /ads/{id}` — ad detail + analysis result if complete
- [ ] `GET /ads/{id}/analysis` — full structured analysis breakdown
- [ ] Auth: JWT middleware — `POST /auth/token`, bearer token required on all `/ads` routes
- [ ] Rate limiting: slowapi middleware (10 req/min unauthenticated, 60 req/min authenticated)
- [ ] `tests/integration/test_auth.py` — auth flow tests (red → green)
- [ ] OpenAPI docs cleanup — descriptions, examples on all endpoints
- [ ] `GET /health` — liveness + readiness check (DB + Redis ping)
- [ ] Manual test: run full curl sequence: register → ingest → analyze → retrieve
- [ ] **GATE**: All endpoints returning correct status codes + validated response schemas

---

## Phase 4: Batch & Comparison Mode ⬜

- [ ] `POST /batches` — accept array of ad URLs, return batch_id
- [ ] Background task: process batch items with concurrency cap (max 5 parallel)
- [ ] `GET /batches/{id}` — progress + partial results
- [ ] `POST /compare` — compare 2 ads side-by-side, highlight differences per dimension
- [ ] `tests/integration/test_batch.py` + `tests/integration/test_compare.py`
- [ ] Manual test: submit 5 competitor ads, compare Brand A vs Brand B
- [ ] **GATE**: Batch of 5 ads completes without errors, compare returns structured diff

---

## Phase 5: Ship ⬜

- [ ] `CHANGELOG.md` — document all phases shipped
- [ ] Production `docker-compose.prod.yml` — secrets from env, no dev mounts
- [ ] Fly.io / Railway deployment config (or Dockerfile for self-host)
- [ ] `docs/adr/0002-llm-provider.md` — document why GPT-4o was chosen
- [ ] Load test: `locust` script for 50 concurrent ingests
- [ ] Security review: no secrets in logs, all inputs sanitized, SSRF protection on URL ingest
- [ ] Final README update with real usage examples + sample analysis output
- [ ] **GATE**: Deployed, smoke tested in production, at least one real analysis shown in README

---

## Parking Lot 🅿️

- Streaming analysis results via SSE (Server-Sent Events)
- Claude / Gemini as alternative LLM backends
- PDF export of analysis report
- Browser extension for in-page ad analysis
- Trend aggregation: track how persuasion techniques shift across industries over time
- Fine-tuned classifier for demographic targeting signals

---

## Lessons Learned 📝

> Fill this in as you go — gotchas, surprising behaviors, patterns that worked well.

- (none yet)
