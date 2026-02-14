# AI Editorial Pipeline

全自动AI新闻编辑流水线 — 从RSS采集到智能评分的端到端解决方案。

## Architecture

```
RSS Sources (63个) → RSS Fetcher → Content Scraper (3路并行) → AI Summarizer
    → Vectorizer → Clusterer → Gravity Engine (16维评分) → Dashboard
```

### 7-Step Pipeline

1. **RSS Fetch** — 从启用的RSS源拉取新文章，URL去重
2. **Content Scrape** — Firecrawl + iFramely + Gemini 三路并行抓取，字段择优合并
3. **AI Summarize** — GPT-4o-mini 生成中文TLDR、英文向量TLDR、5要点、重写标题、分类标签
4. **Vectorize** — text-embedding-3-large 生成3072维向量
5. **Cluster** — pgvector余弦相似度聚类，≥3篇触发扩展搜索
6. **Gravity Score** — Claude Sonnet 16维度深度评分 + Editorial Vote + Novelty Gate
7. **Orchestrate** — Celery定时编排，每步独立容错，24小时无人值守

## Tech Stack

### Backend
- **Framework**: FastAPI + async SQLAlchemy
- **Database**: PostgreSQL + pgvector
- **Task Queue**: Celery + Redis
- **AI**: OpenAI (摘要+向量), Anthropic Claude (评分), Gemini (抓取)
- **Scraping**: Firecrawl, iFramely

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Styling**: TailwindCSS
- **Charts**: Recharts
- **Icons**: Lucide React

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+

### 1. Environment Setup

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start Services

```bash
docker-compose up -d
```

### 3. Seed RSS Sources

```bash
cd backend
python scripts/seed_sources.py
```

### 4. Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Industry Categories (12个行业)

| Slug | 中文名 | 示例源 |
|------|--------|--------|
| finance | 金融 | Reuters, Bloomberg, CNBC |
| technology | 科技 | TechCrunch, The Verge, Ars Technica |
| commercial_space | 商业航天 | SpaceNews, NASASpaceFlight |
| new_energy | 新能源 | CleanTechnica, Electrek |
| healthcare | 医疗健康 | STAT News, Fierce Biotech |
| agriculture | 农业 | AgFunder News |
| consumer | 消费 | Retail Dive, Modern Retail |
| real_estate | 房地产 | The Real Deal, Bisnow |
| manufacturing | 制造业 | The Robot Report |
| crypto | 加密货币 | CoinTelegraph, CoinDesk |
| macro_economy | 宏观经济 | Reuters Economy, The Economist |
| regulation | 监管政策 | Lawfare, Tech Policy Press |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/dashboard/overview | 首页概览数据 |
| GET | /api/v1/dashboard/trending | 实时趋势 |
| GET | /api/v1/articles | 文章列表(分页+过滤) |
| GET | /api/v1/articles/{id} | 文章详情 |
| GET | /api/v1/clusters | 聚类列表 |
| GET | /api/v1/clusters/{id} | 聚类详情 |
| GET | /api/v1/categories | 分类统计 |
| GET | /api/v1/sources | RSS源列表 |
| POST | /api/v1/sources | 添加RSS源 |
| GET | /api/v1/pipeline/status | 流水线状态 |
| POST | /api/v1/pipeline/trigger | 手动触发流水线 |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/routes/      # FastAPI路由
│   │   ├── models/          # SQLAlchemy ORM模型
│   │   ├── services/        # 业务逻辑服务
│   │   ├── tasks/           # Celery任务
│   │   └── utils/           # 工具函数
│   ├── alembic/             # 数据库迁移
│   └── scripts/             # 脚本
├── frontend/
│   └── src/
│       ├── app/             # Next.js页面
│       ├── components/      # React组件
│       ├── lib/             # API客户端+工具
│       └── types/           # TypeScript类型
├── specs/                   # 项目规格文档
└── docker-compose.yml
```
