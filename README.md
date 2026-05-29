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
