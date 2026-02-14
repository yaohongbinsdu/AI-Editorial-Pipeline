# Implementation Plan: AI Editorial Pipeline (全自动AI编辑部)

**Branch**: `001-ai-editorial-pipeline` | **Date**: 2026-02-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-editorial-pipeline/spec.md`

## Summary

构建一套面向股票投资者的全自动AI新闻编辑系统。后端使用 Python + FastAPI 实现7步全链路流水线（RSS采集→三路抓取→字段择优→AI摘要→向量聚类→聚类扩展→Gravity评分），前端使用 Next.js + TailwindCSS 构建投资导向的新闻仪表盘，按行业分类（金融、农业、商业航天等）展示文章，突出市场热点和重大新闻。使用 PostgreSQL + pgvector 存储文章和语义向量，Celery + Redis 驱动异步流水线调度。

## Technical Context

**Language/Version**: Python 3.12 (backend) + TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI, Celery, feedparser, httpx, openai, anthropic
- Frontend: Next.js 15, React 19, TailwindCSS 4, shadcn/ui, Recharts, Lucide Icons
**Storage**: PostgreSQL 16 + pgvector extension (向量存储与HNSW索引) + Redis 7 (任务队列与缓存)
**Testing**: pytest + pytest-asyncio (backend), Vitest + Playwright (frontend)
**Target Platform**: Linux server (Docker容器化部署), 浏览器端 (Chrome/Edge/Safari)
**Project Type**: Web application (backend + frontend)
**Performance Goals**: 每小时处理63个RSS源、单篇文章端到端≤5分钟、前端首屏≤2秒、API p95≤200ms
**Constraints**: 单篇文章处理成本控制（mini模型摘要≤$0.01、Sonnet评分≤$0.05）、pgvector支持≥100K向量
**Scale/Scope**: 63个RSS源、日均处理~500-1000篇文章、单用户投资仪表盘、~8个前端页面/视图

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Code Quality | ✅ PASS | Python: ruff + black; TypeScript: ESLint + Prettier; CI zero-warning policy |
| II. Testing Standards | ✅ PASS | pytest 80%+ coverage; Vitest for frontend; Playwright E2E for P1 stories; contract tests for API |
| III. UX Consistency | ✅ PASS | shadcn/ui design system; TailwindCSS统一样式; 行业配色方案一致; 响应式布局 |
| IV. Performance | ✅ PASS | pgvector HNSW索引; Redis缓存热数据; Next.js SSR首屏优化; API p95 <200ms目标 |

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-editorial-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (OpenAPI specs)
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app entry
│   ├── config.py                # Settings & env vars
│   ├── models/
│   │   ├── article.py           # Article ORM model
│   │   ├── summary.py           # Summary ORM model
│   │   ├── cluster.py           # Cluster ORM model
│   │   ├── gravity_score.py     # GravityScore ORM model
│   │   ├── rss_source.py        # RSSSource ORM model
│   │   └── pipeline_run.py      # PipelineRun ORM model
│   ├── services/
│   │   ├── rss_fetcher.py       # Step 1: RSS拉取
│   │   ├── content_scraper.py   # Step 2-3: 三路抓取 + 字段择优
│   │   ├── summarizer.py        # Step 4: AI摘要 (GPT-5-mini)
│   │   ├── vectorizer.py        # Step 5: 向量化 (OpenAI Embedding)
│   │   ├── clusterer.py         # Step 5-6: 聚类 + 扩展
│   │   ├── gravity_engine.py    # Step 7: Gravity评分 (Claude Sonnet)
│   │   └── pipeline.py          # 流水线编排
│   ├── api/
│   │   ├── routes/
│   │   │   ├── articles.py      # 文章API
│   │   │   ├── clusters.py      # 聚类API
│   │   │   ├── categories.py    # 分类API
│   │   │   ├── dashboard.py     # 仪表盘聚合API
│   │   │   ├── sources.py       # RSS源管理API
│   │   │   └── pipeline.py      # 流水线状态API
│   │   └── deps.py              # 依赖注入
│   ├── tasks/
│   │   ├── celery_app.py        # Celery配置
│   │   ├── periodic.py          # 定时任务(每小时触发)
│   │   └── workers.py           # 异步worker
│   └── utils/
│       ├── retry.py             # 重试机制
│       └── logging.py           # 结构化日志
├── alembic/                     # 数据库迁移
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── requirements.txt
├── Dockerfile
└── pyproject.toml

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # 首页: 市场热点总览
│   │   ├── categories/
│   │   │   └── [slug]/page.tsx  # 行业分类页 (金融/农业/航天...)
│   │   ├── clusters/
│   │   │   └── [id]/page.tsx    # 事件聚类详情页
│   │   ├── articles/
│   │   │   └── [id]/page.tsx    # 文章详情页
│   │   ├── pipeline/
│   │   │   └── page.tsx         # 流水线监控面板
│   │   └── sources/
│   │       └── page.tsx         # RSS源管理页
│   ├── components/
│   │   ├── ui/                  # shadcn/ui基础组件
│   │   ├── article-card.tsx     # 文章卡片
│   │   ├── cluster-group.tsx    # 聚类卡组
│   │   ├── gravity-badge.tsx    # Gravity评分徽章
│   │   ├── category-nav.tsx     # 行业分类导航
│   │   ├── market-heatmap.tsx   # 市场热度图
│   │   ├── trending-bar.tsx     # 热点趋势条
│   │   ├── score-radar.tsx      # 16维雷达图
│   │   └── pipeline-status.tsx  # 流水线状态组件
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   └── utils.ts             # 工具函数
│   └── types/
│       └── index.ts             # TypeScript类型定义
├── tests/
│   ├── unit/
│   └── e2e/
├── package.json
├── tailwind.config.ts
├── next.config.ts
└── Dockerfile

docker-compose.yml               # PostgreSQL + Redis + Backend + Frontend
```

**Structure Decision**: 采用 Web application 结构（Option 2），backend/ 和 frontend/ 分离。后端是数据密集型AI流水线，前端是投资导向的仪表盘。两者通过 REST API 通信，可独立部署和扩展。

## Complexity Tracking

> No Constitution Check violations. Complexity is justified by domain requirements.

| Decision | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|--------------------------------------|
| 4个独立AI模型 | 每个模型有不同的强项和成本特征 | 单一模型无法兼顾速度(摘要)、深度(评分)、专用性(向量化) |
| 三路并行抓取 | 内容质量和可用性保障 | 单工具抓取失败率高，无法保证24小时无人值守 |
| pgvector而非独立向量DB | 减少基础设施复杂度 | Pinecone/Weaviate增加外部依赖和成本，当前规模pgvector足够 |
