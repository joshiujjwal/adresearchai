# AdResearchAI

> 🧠 Reverse-engineer advertisements — exposing persuasion techniques, target demographics, emotional triggers, brand positioning, and messaging strategy.

![Status](https://img.shields.io/badge/status-🚧%20Early%20Development-orange)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-green)
![License](https://img.shields.io/badge/license-private-red)

---

## What It Does

AdResearchAI ingests an advertisement (image, video URL, audio clip, or raw ad copy) and returns a structured reverse-analysis covering:

| Dimension | What's Extracted |
|---|---|
| **Persuasion Techniques** | Social proof, scarcity, authority, reciprocity, fear/aspiration appeals |
| **Target Demographics** | Age range, gender skew, income bracket, psychographic profile |
| **Emotional Triggers** | Primary and secondary emotions being activated |
| **Brand Positioning** | USP, competitive framing, tone of voice |
| **Messaging Strategy** | Hook, value proposition, CTA mechanics, AIDA mapping |
| **Visual/Audio Cues** | Color psychology, music tempo, pacing, casting signals |

---

## Tech Stack

- **Runtime**: Python 3.11+
- **API Layer**: FastAPI + Uvicorn
- **AI / LLM**: OpenAI GPT-4o (vision + text), Whisper (audio transcription)
- **Media Handling**: yt-dlp (video download), Pillow (image processing), ffmpeg-python
- **Data Layer**: PostgreSQL + SQLAlchemy (async), Redis (job queue / cache)
- **Task Queue**: Celery + Redis
- **Auth**: JWT (python-jose)
- **Testing**: pytest + pytest-asyncio + httpx
- **Linting/Format**: ruff + black
- **Containerization**: Docker + docker-compose
- **CI**: GitHub Actions

---

## Getting Started

```bash
# Clone
git clone git@github.com:joshiujjwal/adresearchai.git
cd adresearchai

# Install dependencies
pip install -e ".[dev]"

# Copy and configure environment
cp .env.example .env
# Edit .env — set OPENAI_API_KEY, DATABASE_URL, REDIS_URL

# Start dependencies
docker-compose up -d db redis

# Run dev server
uvicorn src.api.main:app --reload --port 8000

# Run tests
pytest
```

---

## Project Structure

```
adresearchai/
├── src/
│   ├── api/            # FastAPI routes, middleware, lifespan
│   ├── core/           # Config, logging, DB session, settings
│   ├── models/         # SQLAlchemy ORM models + Pydantic schemas
│   ├── services/       # Business logic (analyzer, ingestor, reporter)
│   └── utils/          # Media downloading, file helpers, prompt builders
├── tests/
│   ├── unit/           # Pure-logic tests (services, utils)
│   └── integration/    # API endpoint tests (TestClient / httpx)
├── docs/
│   ├── spec.md         # Feature specification
│   └── adr/            # Architecture Decision Records
├── .github/
│   ├── copilot-instructions.md
│   ├── instructions/   # Path-specific Copilot instructions
│   └── skills/
├── README.md
├── TODO.md
├── CLAUDE.md
├── AGENTS.md
├── pyproject.toml
├── docker-compose.yml
└── .gitignore
```

---

## Contributing

- **Write tests first** (red phase) before any implementation
- **PR evidence required**: include `pytest` output + manual test screenshot in PR description
- **Small focused PRs**: one feature or fix per PR
- **No dead code**: remove or comment with `# TODO` if deferring
- **Run the full lint + test suite** before pushing: `ruff check . && black --check . && pytest`

## 🚀 Improvement Proposals

### First-Principles Analysis
- The core value proposition is **insight commoditization** — making professional-grade ad deconstruction available on demand; the moat is prompt quality and output structure, not the pipeline itself.
- The system is fundamentally an **LLM wrapper with rich I/O formatting**: GPT-4o is doing most of the analytical work, so differentiation must come from structured rubrics, output consistency, and comparison/history features.
- The async job queue is helpful for video/audio inputs but adds operational overhead that is disproportionate for early-stage use; a synchronous path for image/text inputs would lower friction.
- There is no feedback loop: once an analysis is returned, there is no mechanism for users to correct, annotate, or improve outputs.

### Key Risks & Assumptions
- **GPT-4o vision accuracy on ad analysis is assumed to be high** — persuasion labeling is subjective, and the model may produce confident but inconsistent taxonomies.
- **Video ingestion via yt-dlp assumes permissive content access** — many ad-hosting platforms have rate limits, geo-restrictions, or ToS issues with automated scraping.
- **No ground truth exists** — there is no labeled dataset of "correct" ad analyses to validate output quality or regression-test prompt changes.
- **The private license limits ecosystem growth** — community-contributed prompt and rubric improvements could be valuable here.

### Concrete Improvement Ideas
1. **Add an analyst rubric YAML** — externalize the analysis dimensions into a versioned config file so the prompt structure can be improved and A/B tested without code changes.
2. **Build a synchronous fast-path** — for image and text inputs, skip Celery entirely and return results inline; reserve async jobs only for video/audio.
3. **Add a comparison mode** — accept two ads and return a structured diff of their strategies; this is a natural fit for agency and competitive research use cases.
4. **Implement output confidence scoring** — have the model rate its certainty per dimension so users can calibrate trust.
5. **Create a human-correction loop** — allow users to edit any analysis field and store corrections to build a proprietary improvement dataset.
6. **Add a public demo endpoint** — a zero-auth, rate-limited demo reveals real-world failure cases early and improves distribution.
