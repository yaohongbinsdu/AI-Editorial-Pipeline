# Quickstart: AI Editorial Pipeline

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- API Keys:
  - OpenAI API Key (GPT-5-mini + text-embedding-3-large)
  - Anthropic API Key (Claude 3.5 Sonnet)
  - Google AI API Key (Gemini 2.0 Flash)
  - Firecrawl API Key
  - iFramely API Key

## 1. Clone & Setup

```bash
git clone <repo-url>
cd ai-editorial-pipeline
git checkout 001-ai-editorial-pipeline
```

## 2. Environment Configuration

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/editorial
REDIS_URL=redis://localhost:6379/0

# AI Models
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_AI_API_KEY=...

# Content Scraping
FIRECRAWL_API_KEY=fc-...
IFRAMELY_API_KEY=...

# App Config
PIPELINE_INTERVAL_MINUTES=60
LOG_LEVEL=INFO
```

## 3. Start Infrastructure (Docker)

```bash
docker-compose up -d postgres redis
```

This starts:
- PostgreSQL 16 with pgvector extension on port 5432
- Redis 7 on port 6379

## 4. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start FastAPI dev server
uvicorn app.main:app --reload --port 8000
```

In a separate terminal, start Celery worker + beat:

```bash
cd backend
source .venv/bin/activate

# Worker (processes tasks)
celery -A app.tasks.celery_app worker --loglevel=info

# Beat (schedules periodic tasks) - in another terminal
celery -A app.tasks.celery_app beat --loglevel=info
```

## 5. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

Frontend runs on http://localhost:3000

## 6. Verify Setup

1. Open http://localhost:3000 — should see the dashboard (empty initially)
2. Open http://localhost:8000/docs — FastAPI Swagger UI
3. Add RSS sources via API or Sources management page
4. Trigger a pipeline run: `POST http://localhost:8000/api/v1/pipeline/trigger`
5. Watch articles flow through the 7-step pipeline

## 7. Full Docker Deployment

For production-like single-command startup:

```bash
docker-compose up -d
```

This starts all 4 services:
- PostgreSQL + pgvector (port 5432)
- Redis (port 6379)
- Backend: FastAPI + Celery worker + Celery beat (port 8000)
- Frontend: Next.js (port 3000)

## Key URLs

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | 投资仪表盘 |
| API Docs | http://localhost:8000/docs | Swagger UI |
| API Base | http://localhost:8000/api/v1 | REST API |
| Celery Monitor | http://localhost:5555 | Flower (optional) |

## Smoke Test

```bash
# 1. Check API health
curl http://localhost:8000/api/v1/pipeline/status

# 2. Add a test RSS source
curl -X POST http://localhost:8000/api/v1/sources \
  -H "Content-Type: application/json" \
  -d '{"url": "https://feeds.reuters.com/reuters/businessNews", "name": "Reuters Business", "category": "finance"}'

# 3. Trigger pipeline
curl -X POST http://localhost:8000/api/v1/pipeline/trigger

# 4. Check results after ~2-3 minutes
curl http://localhost:8000/api/v1/dashboard/overview
```
