# AdResearchAI — Feature Specification

**Status**: Draft  
**Last updated**: 2025-07  
**Author**: joshiujjwal

---

## 1. Problem Statement

Marketers, researchers, and competitive intelligence teams spend hours manually deconstructing competitor advertisements. The process is subjective, slow, and inconsistent. AdResearchAI automates this reverse analysis — ingesting any advertisement and returning a structured, evidence-grounded breakdown of what it's doing and why.

---

## 2. Scope

### In scope (v1)
- Image ads (JPEG, PNG, WebP, GIF)
- Video ads (YouTube URL, MP4 upload)
- Text-only ad copy (plain text or HTML snippet)
- Audio ads (MP3/WAV upload)
- Web landing page as ad context (URL → screenshot + copy extraction)

### Out of scope (v1)
- Real-time live ad monitoring
- Platform-specific ad library integrations (Meta Ad Library, Google Ads Transparency)
- Programmatic ad bidding data

---

## 3. Functional Requirements

### 3.1 Ingestion
- [ ] Accept image upload (max 20MB) or image URL
- [ ] Accept video URL (YouTube, Vimeo, direct MP4) — download via yt-dlp
- [ ] Accept raw ad copy as plain text (max 10,000 chars)
- [ ] Accept audio file upload (max 50MB) — transcribe via Whisper
- [ ] Accept landing page URL — screenshot via Playwright, extract visible text
- [ ] Validate all inputs; reject unsupported formats with descriptive errors
- [ ] Store original media + metadata in DB; return `ad_id` on success

### 3.2 Analysis Dimensions

Each analysis must return a structured object with:

| Field | Type | Description |
|---|---|---|
| `persuasion_techniques` | `list[str]` | Named techniques (e.g. `"social_proof"`, `"scarcity"`, `"authority"`) with explanation |
| `target_demographic` | `object` | `age_range`, `gender_skew`, `income_bracket`, `psychographic_tags` |
| `emotional_triggers` | `list[str]` | Primary + secondary emotions (e.g. `"aspiration"`, `"fomo"`, `"nostalgia"`) |
| `brand_positioning` | `object` | `usp`, `tone_of_voice`, `competitive_framing`, `archetype` |
| `messaging_strategy` | `object` | `hook`, `value_proposition`, `cta_mechanic`, `aida_stage` |
| `visual_cues` | `object` | `dominant_colors`, `color_psychology`, `casting_signals`, `composition` |
| `audio_cues` | `object` | `music_tempo_bpm`, `music_mood`, `voiceover_tone`, `silence_usage` |
| `confidence_score` | `float` | 0–1, model's self-reported confidence |
| `evidence_quotes` | `list[str]` | Verbatim excerpts from the ad supporting the analysis |

- [ ] `visual_cues` and `audio_cues` only populated when media is present
- [ ] All fields returned as JSON; `null` when not applicable
- [ ] Analysis must cite evidence from the ad (not hallucinate general marketing theory)

### 3.3 API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/token` | Get JWT token |
| `POST` | `/ads/ingest` | Ingest an ad (multipart or JSON body) |
| `GET` | `/ads` | List ads (paginated, auth required) |
| `GET` | `/ads/{id}` | Get ad detail |
| `POST` | `/ads/{id}/analyze` | Trigger analysis (async, returns task_id) |
| `GET` | `/ads/{id}/analysis` | Get completed analysis |
| `GET` | `/tasks/{task_id}` | Poll async task status |
| `POST` | `/batches` | Submit batch of URLs |
| `GET` | `/batches/{id}` | Batch progress + results |
| `POST` | `/compare` | Side-by-side diff of 2 ad analyses |
| `GET` | `/health` | Liveness + readiness |

### 3.4 Auth
- [ ] JWT bearer tokens, 24h expiry
- [ ] `POST /auth/token` accepts `api_key` in request body (pre-issued, no self-serve registration in v1)
- [ ] All routes except `/health` require valid token

### 3.5 Async Task Handling
- [ ] Analysis jobs queued via Celery + Redis
- [ ] `POST /ads/{id}/analyze` returns `202 Accepted` + `{"task_id": "..."}`
- [ ] `GET /tasks/{task_id}` returns `{"status": "pending|running|complete|failed", "result": {...}}`
- [ ] Failed tasks include error message; retried once automatically

---

## 4. Non-Functional Requirements

- [ ] P95 ingestion latency < 2s (excluding media download time)
- [ ] P95 analysis latency < 30s for image/text; < 90s for video
- [ ] API uptime > 99.5%
- [ ] No raw OpenAI API keys in logs or error responses
- [ ] All media stored locally or in object storage — never passed directly to clients
- [ ] SSRF protection: URL inputs validated against allowlist of schemes (`http`, `https`) and blocked private IP ranges

---

## 5. Data Model

```
Ad
  id            UUID PK
  source_type   enum(image, video, text, audio, webpage)
  source_url    text nullable
  raw_text      text nullable
  media_path    text nullable  -- local path or S3 key
  status        enum(pending, processing, complete, failed)
  created_at    timestamp
  updated_at    timestamp

Analysis
  id            UUID PK
  ad_id         UUID FK → Ad.id
  dimensions    jsonb           -- full AnalysisResult as JSON
  model_used    text            -- e.g. "gpt-4o-2024-05-13"
  tokens_used   int
  created_at    timestamp

Task
  id            UUID PK
  ad_id         UUID FK → Ad.id
  status        enum(pending, running, complete, failed)
  error_msg     text nullable
  created_at    timestamp
  updated_at    timestamp
```

---

## 6. LLM Prompt Strategy

- **System prompt**: establishes the role of an expert ad analyst; instructs model to cite evidence, avoid speculation, use structured JSON output
- **User prompt**: constructed per input type — image (base64 + instructions), text (copy + instructions), audio (transcript + instructions)
- **Output format**: JSON Schema enforced via `response_format={"type": "json_object"}` (GPT-4o)
- **Temperature**: 0.2 (low, for consistency)
- **Max tokens**: 2048 per analysis call

---

## 7. Test Plan

### Unit tests
- [ ] `test_config.py` — settings load, required vars raise on missing
- [ ] `test_ad_model.py` — ORM field types, nullable constraints
- [ ] `test_ingestor.py` — URL validation, SSRF block, media save (mocked I/O)
- [ ] `test_media_utils.py` — yt-dlp wrapper, Pillow encode, ffmpeg extract (fixture files)
- [ ] `test_prompt_builder.py` — correct prompt structure per source_type (snapshot tests)
- [ ] `test_analyzer.py` — mock OpenAI client, assert each dimension key present in output
- [ ] `test_reporter.py` — raw LLM JSON → `AnalysisResult` schema, edge cases (missing keys)

### Integration tests
- [ ] `test_ingest_api.py` — POST image URL, POST raw text → 200 + ad_id
- [ ] `test_analyze_api.py` — POST /analyze → 202, GET /tasks/{id} → complete
- [ ] `test_auth.py` — missing token → 401, invalid token → 401, valid → 200
- [ ] `test_compare_api.py` — two ad IDs → structured diff response

### Edge cases
- [ ] Oversized upload → 413
- [ ] Private IP URL → 422 (SSRF block)
- [ ] Unsupported video format → 422
- [ ] OpenAI timeout → 503 with retry header
- [ ] Malformed ad copy (XSS attempt) → sanitized, no injection

---

## 8. Open Questions

- [ ] Should we store analysis history (multiple analyses per ad, versioned)? Or overwrite?
- [ ] What's the acceptable cost per analysis call? Set a token budget cap?
- [ ] Do we want a UI (React/Next.js) in v2, or stay API-only?
- [ ] Whisper local vs API — tradeoff: cost vs. latency vs. privacy
- [ ] GDPR: if users submit ads with PII (e.g. influencer faces), what's our data retention policy?
