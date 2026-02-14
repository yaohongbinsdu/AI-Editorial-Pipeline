# Tasks: AI Editorial Pipeline (全自动AI编辑部)

**Input**: Design documents from `/specs/001-ai-editorial-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create project scaffolding, install dependencies, configure tooling

- [x] T001 Create backend project structure: `backend/app/{models,services,api/routes,tasks,utils}/` per plan.md
- [x] T002 Create `backend/pyproject.toml` with Python 3.12 config, ruff + black formatting rules
- [x] T003 Create `backend/requirements.txt` with pinned dependencies: fastapi, uvicorn, celery, redis, feedparser, httpx, openai, anthropic, google-generativeai, sqlalchemy, alembic, psycopg2-binary, pgvector, pydantic, structlog
- [x] T004 [P] Create `frontend/` with Next.js 15 App Router: `npx create-next-app@latest frontend --typescript --tailwind --app --src-dir`
- [x] T005 [P] Create `docker-compose.yml` with 4 services: postgres (16 + pgvector), redis (7), backend, frontend
- [x] T006 Create `.env.example` with all required environment variables per quickstart.md
- [x] T007 [P] Configure backend linting: `backend/ruff.toml` (rules, line-length=100, target-version=py312)
- [x] T008 [P] Configure frontend linting: `frontend/.eslintrc.json` + `frontend/.prettierrc` with project standards
- [x] T009 Install shadcn/ui in frontend: initialize with `npx shadcn@latest init` then add components: button, card, badge, table, tabs, dropdown-menu, sheet, separator, skeleton
- [x] T010 [P] Create `frontend/src/types/index.ts` with all TypeScript interfaces matching OpenAPI schemas: Article, ArticleBrief, ArticleDetail, Summary, GravityScore, Cluster, ClusterBrief, RSSSource, PipelineRun, DashboardOverview, CategoryStats, PaginatedResponse
- [x] T011 [P] Create `frontend/src/lib/api.ts` with API client: base URL config, typed fetch helpers for all endpoints in contracts/openapi.yaml

**Checkpoint**: Project scaffolding complete — both backend and frontend can start dev servers

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Database schema, core models, shared infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T012 Create `backend/app/config.py` with Pydantic Settings: DATABASE_URL, REDIS_URL, OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_AI_API_KEY, FIRECRAWL_API_KEY, IFRAMELY_API_KEY, PIPELINE_INTERVAL_MINUTES, LOG_LEVEL
- [x] T013 Create `backend/app/main.py` with FastAPI app: CORS middleware, lifespan handler (DB connection pool), API router mounts for /api/v1/{articles,clusters,categories,dashboard,sources,pipeline}
- [x] T014 Create SQLAlchemy Base and DB session in `backend/app/models/__init__.py` with async engine setup for PostgreSQL + pgvector
- [x] T015 Create `backend/app/models/rss_source.py` — RSSSource ORM model per data-model.md (all fields, indexes, category enum validation)
- [x] T016 [P] Create `backend/app/models/article.py` — Article ORM model per data-model.md (all fields including 3 scraper result sets, final fields, status state machine, indexes)
- [x] T017 [P] Create `backend/app/models/summary.py` — Summary ORM model per data-model.md (human_tldr, vector_tldr, key_points JSONB, rewritten_title, category, tags JSONB)
- [x] T018 [P] Create `backend/app/models/cluster.py` — Cluster ORM model per data-model.md (title, category, article_count, centroid vector(3072), expansion fields)
- [x] T019 [P] Create `backend/app/models/gravity_score.py` — GravityScore ORM model per data-model.md (16 dimension floats, editorial_vote, novelty_gate, composite_score, reasoning)
- [x] T020 [P] Create `backend/app/models/pipeline_run.py` — PipelineRun ORM model per data-model.md (status, counters, duration)
- [x] T021 [P] Create `backend/app/models/pipeline_step_log.py` — PipelineStepLog ORM model per data-model.md (step_name, status, duration_ms, error_message, retry_count, metadata JSONB)
- [x] T022 Create Alembic setup: `backend/alembic.ini` + `backend/alembic/env.py` configured for async SQLAlchemy, generate initial migration with all models including pgvector extension CREATE
- [x] T023 Create `backend/app/utils/logging.py` with structlog configuration: JSON output, timestamp, log level from config, context binding for pipeline_run_id and article_id
- [x] T024 [P] Create `backend/app/utils/retry.py` with async retry decorator: max_retries=3, exponential backoff, exception logging, configurable retry-on exceptions
- [x] T025 Create `backend/app/tasks/celery_app.py` with Celery configuration: Redis broker/backend, task serialization JSON, task routes, result expiry
- [x] T026 [P] Create `backend/app/api/deps.py` with FastAPI dependency injection: get_db session, get_redis, pagination params (page, page_size)
- [x] T027 Create `frontend/src/app/layout.tsx` with root layout: Inter font, dark theme support, sidebar navigation with category-nav component, responsive container
- [x] T028 [P] Create `frontend/src/components/category-nav.tsx` — sidebar/top navigation listing all 12 industry categories (金融/科技/商业航天/新能源/医疗健康/农业/消费/房地产/制造业/加密货币/宏观经济/监管政策) with icons from Lucide, active state, article counts

### Tests for Phase 2

- [ ] T071 Create `backend/tests/conftest.py` — 测试基础设施: async SQLite test DB, test client fixture (AsyncClient via httpx), mock settings, DB session fixture with rollback, factory fixtures for RSSSource/Article/Summary/GravityScore/Cluster
- [ ] T072 [P] Create `backend/tests/unit/test_models.py` — 模型单元测试: 验证所有7个ORM模型可实例化, 字段类型正确, 关系映射正确, Category枚举包含13个值, ArticleStatus枚举包含全部状态
- [ ] T073 [P] Create `backend/tests/unit/test_config.py` — 配置测试: Settings从环境变量加载, 默认值正确, 所有API key字段存在
- [ ] T074 Create `backend/tests/unit/test_utils.py` — 工具测试: retry装饰器重试逻辑, structlog日志格式化

**Checkpoint**: Foundation ready — database migrated, models defined, FastAPI and Next.js shells running, Celery configured

---

## Phase 3: User Story 1 — RSS新闻自动采集与内容抓取 (Priority: P1) 🎯 MVP

**Goal**: 从63个RSS源自动拉取文章，三路并行抓取，字段级择优合并

**Independent Test**: 配置5个RSS源，触发一次采集，验证文章正确拉取、三路抓取并行、字段择优合并输出

### Implementation for User Story 1

- [x] T029 [US1] Create `backend/app/services/rss_fetcher.py` — RSS拉取服务: async fetch_all_sources() 遍历启用的RSSSource, feedparser解析每个源, 提取title/link/published/summary/image, URL去重逻辑(检查Article.original_url), 返回新发现文章列表, 错误处理+consecutive_failures计数
- [x] T030 [US1] Create `backend/app/services/content_scraper.py` — 三路内容抓取服务:
  - async scrape_with_firecrawl(url) — 调用Firecrawl API提取标题+正文+元数据
  - async scrape_with_iframely(url) — 调用iFramely API提取标题+描述+缩略图+oEmbed
  - async scrape_with_gemini(url) — 调用Gemini 2.0 Flash视觉模式"看"网页提取标题+正文
  - async scrape_article(url) — asyncio.gather三路并行, 每路独立try/except不互相阻塞
  - select_best_field() — 字段级Winner选择: 标题(iFramely>Gemini>Firecrawl>RSS), 正文(Gemini>Firecrawl>RSS按长度质量), 图片(RSS>iFramely>Firecrawl)
  - 返回合并后的final_title, final_content, final_image_url
- [x] T031 [US1] Create `backend/app/api/routes/sources.py` — RSS源管理API per openapi.yaml:
  - GET /sources — 列表查询所有源
  - POST /sources — 添加新源(url唯一校验)
  - PATCH /sources/{id} — 更新源(name/category/enabled/interval)
  - DELETE /sources/{id} — 删除源
- [x] T032 [US1] Create `backend/app/api/routes/articles.py` — 文章列表API per openapi.yaml:
  - GET /articles — 分页+过滤(category, status, novelty_gate, editorial_vote, min_score, sort_by, order)
  - GET /articles/{id} — 文章详情(JOIN summary + gravity_score + cluster + source)
  - GET /articles/{id}/similar — 相似文章(暂返回空, US3实现向量后填充)
- [x] T033 [US1] Create `frontend/src/app/sources/page.tsx` — RSS源管理页面: 源列表表格(名称/URL/分类/状态/上次拉取/失败次数), 添加源对话框, 启用/禁用开关, 删除确认, 使用shadcn Table+Dialog+Switch组件
- [x] T034 [US1] Create `frontend/src/components/article-card.tsx` — 文章卡片组件: 显示rewritten_title(或final_title), human_tldr, category badge, tags, source_name, published_at时间戳, 图片缩略图, composite_score(如有), editorial_vote badge颜色(must_read=红/interesting=蓝/skip=灰)
- [x] T035 [US1] Create `frontend/src/app/articles/[id]/page.tsx` — 文章详情页: 标题, 正文全文, 图片, 来源链接, 发布时间, 作者, 摘要(human_tldr+key_points), 分类标签, 所属聚类链接(如有), Gravity评分展示区(US4实现后填充)

### Tests for Phase 3

- [ ] T075 [US1] Create `backend/tests/unit/test_rss_fetcher.py` — RSS拉取测试: mock feedparser解析, URL去重逻辑, 错误源跳过不中断, consecutive_failures递增
- [ ] T076 [US1] Create `backend/tests/unit/test_content_scraper.py` — 三路抓取测试: mock三路API调用, 字段择优选择逻辑, 单路失败不影响其他路, 全部失败返回RSS原始数据
- [ ] T077 [US1] Create `backend/tests/integration/test_sources_api.py` — Sources API集成测试: CRUD全流程(创建/列表/更新/删除), URL唯一性校验, 不存在的source返回404
- [ ] T078 [US1] Create `backend/tests/integration/test_articles_api.py` — Articles API集成测试: 列表分页, category过滤, 文章详情JOIN, 不存在的article返回404

**Checkpoint**: US1完成 — RSS源可管理, 文章可采集+抓取+合并+展示。这是可独立运行的MVP。

---

## Phase 4: User Story 2 — AI摘要生成与元数据标注 (Priority: P2)

**Goal**: 每篇文章自动生成人类版TLDR+向量版TLDR+5 Key Points+重写标题+分类标签

**Independent Test**: 输入10篇已采集文章, 验证每篇生成完整摘要包且输出符合schema

### Implementation for User Story 2

- [x] T036 [US2] Create `backend/app/services/summarizer.py` — AI摘要服务:
  - 定义SummarySchema(Pydantic): human_tldr(str, max 100字), vector_tldr(str, max 300字), key_points(list[str], exactly 5), rewritten_title(str), category(CategoryEnum), tags(list[str])
  - async generate_summary(article) — 调用OpenAI GPT-5-mini with structured output, system prompt包含12个行业分类定义让AI准确分类, 正文<50字则标记content_insufficient并跳过
  - prompt工程: 要求人类版TLDR简洁直白, 向量版TLDR塞满关键词+实体+数字, key_points突出投资相关信息
  - 错误处理: schema校验失败重试, 3次失败标记summary_failed
- [x] T037 [US2] Update `frontend/src/components/article-card.tsx` — 增强卡片显示: 添加rewritten_title为主标题, human_tldr作为摘要, category使用行业配色badge, tags作为小标签列表
- [x] T038 [US2] Create `frontend/src/app/categories/[slug]/page.tsx` — 行业分类页面: 按category过滤文章列表(调用GET /articles?category=slug), 页面顶部显示分类名称+文章数+热度趋势, 文章卡片网格布局, 分页加载
- [x] T039 [US2] Create `backend/app/api/routes/categories.py` — 分类API per openapi.yaml:
  - GET /categories — 所有分类及统计(文章数/聚类数/热度分/趋势方向)
  - GET /categories/{slug} — 单分类详情(含文章分页+聚类+热门关键词)

### Tests for Phase 4

- [ ] T079 [US2] Create `backend/tests/unit/test_summarizer.py` — 摘要服务测试: mock OpenAI调用, schema校验(5个key_points/category枚举/tags非空), 正文<50字跳过逻辑, 3次失败标记summary_failed
- [ ] T080 [US2] Create `backend/tests/integration/test_categories_api.py` — 分类API测试: 列表返回所有分类+统计, 单分类页含文章分页, 不存在slug返回空

**Checkpoint**: US2完成 — 文章有AI生成的摘要、分类标签, 可按行业板块浏览

---

## Phase 5: User Story 3 — 向量化聚类与聚类扩展 (Priority: P3)

**Goal**: 文章向量化, 语义聚类, ≥3篇触发扩展搜索

**Independent Test**: 20篇文章(5个事件各4篇), 验证同事件归入同组, ≥3篇触发扩展

### Implementation for User Story 3

- [x] T040 [US3] Create `backend/app/services/vectorizer.py` — 向量化服务:
  - async generate_embedding(text) — 调用OpenAI text-embedding-3-large (3072维), 输入为vector_tldr
  - async vectorize_article(article_id) — 获取Summary.vector_tldr, 生成embedding, 存入Vector表
  - 批量处理: async vectorize_batch(article_ids) 最多20篇并发
- [x] T041 [US3] Create `backend/app/services/clusterer.py` — 聚类服务:
  - async find_nearest_cluster(embedding, threshold=0.82) — pgvector余弦相似度查询Cluster.centroid, 返回最近聚类(若>阈值)
  - async assign_to_cluster(article_id) — 查找最近聚类, 匹配则加入并更新centroid(增量平均), 不匹配则创建新聚类
  - async check_expansion(cluster_id) — 若article_count≥3且expansion_triggered=false, 触发扩展搜索
  - async expand_cluster(cluster_id) — 根据聚类标题和成员文章关键词构造搜索query, 调用搜索API, 将相似度>阈值的新文章纳入聚类, 标记expansion_triggered=true
  - async split_large_cluster(cluster_id) — 若article_count>50, 用K-means分裂为子聚类
- [x] T042 [US3] Create `backend/app/api/routes/clusters.py` — 聚类API per openapi.yaml:
  - GET /clusters — 聚类列表(分页+按category过滤+排序)
  - GET /clusters/{id} — 聚类详情(含所有成员文章ArticleBrief列表)
- [x] T043 [US3] Create `frontend/src/components/cluster-group.tsx` — 聚类卡组组件: 聚类标题, 文章数badge, 分类标签, 成员文章缩略列表(前3篇), "查看全部"链接, 最后更新时间
- [x] T044 [US3] Create `frontend/src/app/clusters/[id]/page.tsx` — 聚类详情页: 聚类标题, 分类, 文章数, 是否已扩展搜索badge, 时间线视图(按published_at排序展示所有成员文章卡片), 聚类摘要(后续可AI生成)
- [x] T045 [US3] Update `backend/app/api/routes/articles.py` — 填充GET /articles/{id}/similar: 用pgvector余弦相似度查询top-N相似文章(排除自身和同聚类), 返回SimilarArticle列表含similarity分数

### Tests for Phase 5

- [ ] T081 [US3] Create `backend/tests/unit/test_vectorizer.py` — 向量化测试: mock OpenAI embedding调用, 返回3072维向量, 批量处理并发控制
- [ ] T082 [US3] Create `backend/tests/unit/test_clusterer.py` — 聚类测试: mock pgvector查询, 新聚类创建逻辑, 已有聚类合入+centroid更新, expansion触发条件(≥3篇)
- [ ] T083 [US3] Create `backend/tests/integration/test_clusters_api.py` — 聚类API测试: 列表分页, category过滤, 聚类详情含成员文章

**Checkpoint**: US3完成 — 文章自动聚类为事件组, 相似文章推荐可用, 聚类页面可浏览

---

## Phase 6: User Story 4 — Gravity Engine编辑评分与排序 (Priority: P4)

**Goal**: 16维度深度评分, Editorial Vote, Novelty Gate过滤

**Independent Test**: 30篇文章, 验证每篇获得完整评分, Novelty Gate=fail的不展示

### Implementation for User Story 4

- [x] T046 [US4] Create `backend/app/services/gravity_engine.py` — Gravity评分服务:
  - 定义GravitySchema(Pydantic): 16个float维度(0-10) + editorial_vote(must_read|interesting|skip) + novelty_gate(bool) + reasoning(str)
  - SYSTEM_PROMPT: 定义4层面16维度的评分标准, 要求JSON输出, 包含每个维度的评判指南
  - async score_article(article) — 调用Anthropic Claude 3.5 Sonnet with structured output, 输入final_title+final_content+human_tldr+category+tags
  - compute_composite_score(scores) — 加权计算: 正向维度加权求和(impact*0.15 + intellectual*0.2 + overlay*0.1) - 负向标记惩罚(pr_fluff + speculation + paid_sponsorship)*0.1
  - 错误处理: schema校验失败重试, 3次失败标记score_failed
- [x] T047 [US4] Create `frontend/src/components/score-radar.tsx` — 16维雷达图组件: 使用Recharts RadarChart, 4个层面用不同颜色区分(影响力=红/智识引力=蓝/叠加信号=绿/质量标记=橙), 悬停显示具体分值, 响应式尺寸
- [x] T048 [US4] Create `frontend/src/components/gravity-badge.tsx` — Gravity评分徽章组件: editorial_vote颜色编码(must_read=红色脉动/interesting=蓝色/skip=灰色), composite_score数值显示, Novelty Gate状态(pass=绿勾/fail=红叉), viral_potential映射为气泡大小CSS变量
- [x] T049 [US4] Update `frontend/src/app/articles/[id]/page.tsx` — 文章详情页增加Gravity评分区域: score-radar雷达图, 16维度分值列表(按层面分组), editorial_vote大号badge, reasoning推理过程折叠展示, composite_score排名
- [x] T050 [US4] Update `backend/app/api/routes/articles.py` — GET /articles 支持novelty_gate=true过滤(默认仅返回通过Novelty Gate的文章), 支持min_score过滤, 默认按composite_score DESC排序

### Tests for Phase 6

- [ ] T084 [US4] Create `backend/tests/unit/test_gravity_engine.py` — Gravity评分测试: mock Anthropic调用, 16维度schema校验(0-10范围), composite_score加权计算验证, editorial_vote枚举校验, novelty_gate布尔值

**Checkpoint**: US4完成 — 每篇文章有16维评分, must_read文章突出显示, 低质量文章被Novelty Gate过滤

---

## Phase 7: User Story 5 — 全链路编排与容错运行 (Priority: P5)

**Goal**: 7步流水线编排, 每小时触发, 独立容错, 24小时无人值守

**Independent Test**: 模拟完整周期, 人为让一步失败, 验证流水线继续运行

### Implementation for User Story 5

- [x] T051 [US5] Create `backend/app/services/pipeline.py` — 流水线编排服务:
  - async run_pipeline() — 完整周期编排:
    1. 创建PipelineRun记录
    2. rss_fetcher.fetch_all_sources() → 新文章列表
    3. 对每篇新文章: content_scraper.scrape_article() → 更新Article
    4. 对每篇fetched文章: summarizer.generate_summary() → 创建Summary
    5. 对每篇summarized文章: vectorizer.vectorize_article() → 创建Vector
    6. 对每篇vectorized文章: clusterer.assign_to_cluster() → 更新Cluster
    7. 对所有≥3篇聚类: clusterer.check_expansion()
    8. 对每篇clustered文章: gravity_engine.score_article() → 创建GravityScore
    9. 更新PipelineRun统计(processed/failed/duration)
  - 每个步骤用PipelineStepLog记录状态
  - 每个步骤独立try/except, 失败记录日志但不中断后续步骤
  - 单篇文章失败不影响其他文章处理
- [x] T052 [US5] Create `backend/app/tasks/workers.py` — Celery任务定义:
  - @celery_app.task run_full_pipeline() — 调用pipeline.run_pipeline()
  - @celery_app.task process_single_article(article_id) — 单篇文章全流程(用于重试)
  - @celery_app.task retry_failed_articles() — 查找所有*_failed状态文章并重试
- [x] T053 [US5] Create `backend/app/tasks/periodic.py` — Celery Beat定时任务:
  - 每PIPELINE_INTERVAL_MINUTES分钟触发run_full_pipeline
  - 每6小时触发retry_failed_articles
  - 每天触发清理>30天的PipelineStepLog
- [x] T054 [US5] Create `backend/app/api/routes/pipeline.py` — 流水线API per openapi.yaml:
  - GET /pipeline/status — 当前运行状态(is_running, current_run, last_completed, step_stats_24h)
  - GET /pipeline/runs — 执行历史列表(最近N次)
  - GET /pipeline/runs/{id} — 单次执行详情(含step_logs)
  - POST /pipeline/trigger — 手动触发一次流水线
- [x] T055 [US5] Create `frontend/src/components/pipeline-status.tsx` — 流水线状态组件: 运行中/空闲状态指示灯, 最近一次运行时间+结果, 24小时处理统计(文章数/成功率), 用于首页和监控页
- [x] T056 [US5] Create `frontend/src/app/pipeline/page.tsx` — 流水线监控页面:
  - 顶部: 当前状态+手动触发按钮
  - 中部: 7个步骤各自的24小时统计(成功/失败/平均耗时)用Recharts BarChart
  - 底部: 最近24次执行记录表格(开始时间/状态/发现/处理/失败/耗时), 点击展开step_logs详情

### Tests for Phase 7

- [ ] T085 [US5] Create `backend/tests/unit/test_pipeline.py` — 流水线编排测试: mock所有service调用, 单步失败不中断后续步骤, PipelineRun状态更新(running→completed), 统计计数正确
- [ ] T086 [US5] Create `backend/tests/integration/test_pipeline_api.py` — Pipeline API测试: GET status返回正确结构, GET runs列表, POST trigger创建新run, 不存在的run_id返回404

**Checkpoint**: US5完成 — 全自动流水线运行, 可监控, 可手动触发, 容错隔离

---

## Phase 8: Dashboard — 首页市场热点总览

**Goal**: 投资导向首页, 直观展示市场关注重点和大新闻

### Implementation for Dashboard

- [x] T057 Create `backend/app/api/routes/dashboard.py` — 仪表盘API per openapi.yaml:
  - GET /dashboard/overview — 聚合: 时间窗口内文章总数, 分类breakdown(文章数+热度+趋势), top5聚类, must_read文章, market_focus(按行业的热度分+关键词), pipeline_health
  - GET /dashboard/trending — 实时趋势: 按composite_score排序的top聚类和文章
- [x] T058 Create `frontend/src/components/market-heatmap.tsx` — 市场热度图组件: 12个行业板块的Treemap或热力格子(使用Recharts Treemap), 面积=文章数量, 颜色深浅=热度分, 点击跳转分类页
- [x] T059 Create `frontend/src/components/trending-bar.tsx` — 热点趋势条组件: 横向滚动的trending聚类卡片, 显示聚类标题+文章数+最近更新时间, 点击跳转聚类详情
- [x] T060 Create `frontend/src/app/page.tsx` — 首页市场热点总览:
  - 顶部: market-heatmap 行业热度图(一眼看出哪个板块最热)
  - 中部左: trending-bar 热门事件(聚类)滚动条
  - 中部右: must_read文章列表(Gravity Engine评为must_read的)
  - 底部: 最新文章流(按时间倒序, 含article-card+gravity-badge)
  - 右侧栏: pipeline-status组件 + 各分类文章数统计
  - 响应式: 移动端单列堆叠, 桌面端三栏布局

### Tests for Phase 8

- [ ] T087 Create `backend/tests/integration/test_dashboard_api.py` — Dashboard API测试: overview返回正确结构(total_articles/category_breakdown/top_clusters/must_read_articles/pipeline_health), trending返回clusters+articles列表

**Checkpoint**: 首页完成 — 投资者可一眼看到市场热点板块、重大事件聚类、must_read文章

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: 质量提升, 性能优化, 文档完善

- [x] T061 [P] Create `backend/Dockerfile` — multi-stage build: Python 3.12-slim, pip install, uvicorn启动, celery worker+beat supervisor
- [x] T062 [P] Create `frontend/Dockerfile` — multi-stage build: node:20-alpine, npm ci, next build, next start
- [ ] T063 Update `docker-compose.yml` (deferred) — 完善: 健康检查, 卷挂载(postgres data), 网络配置, 环境变量引用.env, depends_on条件
- [ ] T064 [P] Add Redis caching layer (deferred) in `backend/app/api/deps.py` — 缓存dashboard/overview(TTL 5min), categories(TTL 2min), 减少重复聚合查询
- [ ] T065 [P] Add loading skeletons (deferred) in frontend — 为article-card, cluster-group, market-heatmap, score-radar添加Skeleton loading状态
- [x] T066 [P] Create `frontend/src/app/not-found.tsx` + error boundaries — 统一404页面, 全局error boundary with retry button
- [ ] T067 [P] Add pagination component (deferred) `frontend/src/components/ui/pagination.tsx` — 通用分页组件, 用于文章列表和聚类列表
- [ ] T068 Performance optimization (deferred) — backend: 添加数据库查询索引验证(EXPLAIN ANALYZE), N+1查询检查, connection pool调优; frontend: Next.js Image优化, 动态import Recharts图表组件减少首屏JS
- [x] T069 [P] Create `README.md` at repo root — 项目介绍, 架构图(7步流水线), 技术栈, 快速启动引用quickstart.md, API文档链接, 行业分类说明
- [x] T070 [P] Create seed data script `backend/scripts/seed_sources.py` — 预置63个RSS源(覆盖12个行业分类): Reuters, Bloomberg, TechCrunch, SpaceNews, CNBC, 等主要财经科技新闻源

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — BLOCKS all user stories
- **Phase 3 (US1 RSS采集)**: Depends on Phase 2 — P1 MVP
- **Phase 4 (US2 AI摘要)**: Depends on Phase 2 + US1 Article data — can start models/services in parallel with US1 API work
- **Phase 5 (US3 向量聚类)**: Depends on Phase 2 + US2 Summary.vector_tldr
- **Phase 6 (US4 Gravity评分)**: Depends on Phase 2 + US1 Article data — can start in parallel with US2/US3
- **Phase 7 (US5 流水线编排)**: Depends on US1 + US2 + US3 + US4 (编排所有服务)
- **Phase 8 (Dashboard首页)**: Depends on US1(文章) + US2(分类) + US4(评分) at minimum
- **Phase 9 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **US1 (P1)**: Standalone — only needs Foundational phase
- **US2 (P2)**: Needs US1 articles as input — but service layer can be built in parallel
- **US3 (P3)**: Needs US2 vector_tldr — strictly sequential after US2
- **US4 (P4)**: Needs US1 articles — can be built in parallel with US2/US3
- **US5 (P5)**: Needs ALL services — must be last user story

### Within Each User Story

- Models before services (data structures first)
- Services before API routes (business logic first)
- Backend API before frontend pages (data source first)
- Core implementation before enhancements

### Parallel Opportunities

- Phase 1: T004, T005, T007, T008, T010, T011 can all run in parallel
- Phase 2: T015-T021 (all models) can run in parallel after T014
- US4 (Gravity Engine) can be built in parallel with US2+US3
- All frontend components marked [P] can be built in parallel
- Phase 9: T061, T062, T064-T067, T069, T070 can all run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (RSS采集)
4. **STOP and VALIDATE**: 添加5个RSS源, 触发采集, 验证文章正确拉取和展示
5. Deploy/demo if ready — 已有基本的文章浏览功能

### Incremental Delivery

1. Setup + Foundational → 基础框架就绪
2. US1 (RSS采集) → 文章可采集可浏览 (MVP!)
3. US2 (AI摘要) → 文章有摘要+分类, 行业页面可用
4. US3 (向量聚类) → 事件聚类, 相似推荐
5. US4 (Gravity评分) → 智能排序, 质量过滤
6. US5 (流水线编排) → 全自动运行
7. Dashboard首页 → 投资者完整视图
8. Polish → 生产就绪

### Recommended Execution Order (Solo Developer)

Phase 1 → Phase 2 → US1 → US2 → US4 → US3 → US5 → Dashboard → Polish

(注意: US4可以在US2之后立即开始, 因为它只需要Article数据; US3必须等US2完成)

---

## Phase 10: Frontend Optimization & End-to-End Verification

**Purpose**: Fix all frontend pages so every navigation link works correctly, add missing pages, enable direct pipeline execution without Celery, verify RSS monitoring produces visible content, and add tests for all of it.

**Goal**: 点击每个导航页面都能正确显示内容，RSS源能被真正监听并将内容展示在页面上，全部测试通过。

### Implementation

- [ ] T088 [P] Create `frontend/src/app/articles/page.tsx` — 文章列表页: 分页+过滤(category/status/sort), 使用ArticleCard组件, 空状态提示, 调用GET /articles API
- [ ] T089 [P] Create `frontend/src/app/clusters/page.tsx` — 聚类列表页: 分页+category过滤, 使用ClusterGroup组件, 空状态提示, 调用GET /clusters API
- [ ] T090 [P] Create `frontend/src/app/categories/page.tsx` — 行业分类索引页: 展示所有12个行业分类卡片(文章数+聚类数), 调用GET /categories API, 点击跳转到/categories/[slug]
- [ ] T091 Update `frontend/src/app/layout.tsx` — 侧边栏导航优化: 提取为客户端SidebarNav组件支持active state高亮(usePathname), 行业分类链接改为/categories索引页, 响应式移动端支持
- [ ] T092 Add direct pipeline trigger in `backend/app/api/routes/pipeline.py` — POST /pipeline/trigger 添加同步执行模式(sync=true参数), 直接调用run_pipeline而非依赖Celery worker, 使其在无Celery环境下也能运行
- [ ] T093 [P] Create `frontend/src/app/not-found.tsx` — 全局404页面, 包含返回首页链接

### Tests

- [ ] T094 Create `backend/tests/integration/test_pipeline_trigger.py` — Pipeline同步触发测试: POST /pipeline/trigger?sync=true 返回202, 验证PipelineRun被创建, RSS源被实际拉取
- [ ] T095 Create `backend/tests/integration/test_rss_fetch_e2e.py` — RSS抓取端到端测试: 插入测试RSS源, 调用run_pipeline, 验证articles表有新记录, 文章status正确
- [ ] T096 Create `frontend/tests/e2e/navigation.spec.ts` — Playwright导航测试: 验证所有6个导航链接可点击且页面正确加载(Dashboard/文章/聚类/分类/RSS源/流水线), 无console error
- [ ] T097 Create `frontend/tests/e2e/sources.spec.ts` — Playwright RSS源管理测试: 源列表显示已添加的46个源, 添加新源表单可用, 删除源确认对话框可用
- [ ] T098 Create `frontend/tests/e2e/pipeline.spec.ts` — Playwright流水线测试: 手动触发按钮可点击, 触发后执行记录表格显示新记录, 步骤统计显示数据
- [ ] T099 Create `backend/tests/integration/test_full_page_data.py` — 页面数据完整性测试: 验证GET /articles返回正确分页结构, GET /clusters返回列表, GET /categories返回12个分类, GET /sources返回已添加的源列表, GET /dashboard/overview和/trending返回正确结构

**Checkpoint**: 所有前端页面可正常访问和显示数据, RSS源被真正监听, Pipeline可手动触发并产出文章, 全部测试通过

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All AI API calls must handle rate limits gracefully with exponential backoff
- Frontend pages should show meaningful empty states when no data available yet
