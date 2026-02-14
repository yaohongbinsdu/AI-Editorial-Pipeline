# Research: AI Editorial Pipeline

**Date**: 2026-02-14
**Branch**: `001-ai-editorial-pipeline`

## R1: Backend Framework — FastAPI vs Django vs Flask

**Decision**: FastAPI

**Rationale**:
- 原生 async/await 支持，适合并行三路抓取和AI API调用
- 自动生成 OpenAPI 文档，前后端对接效率高
- Pydantic v2 内置数据验证，与AI模型返回的JSON schema天然契合
- 性能优于 Django REST Framework，适合高频流水线场景

**Alternatives considered**:
- **Django**: ORM成熟但async支持不如FastAPI原生，admin面板对本项目价值有限
- **Flask**: 太轻量，需要大量插件组装，async需要额外工作

---

## R2: 任务队列 — Celery + Redis vs Dramatiq vs APScheduler

**Decision**: Celery + Redis + celery-beat

**Rationale**:
- 成熟的分布式任务队列，支持任务链（chain）、组（group）、和弦（chord）编排复杂流水线
- celery-beat 原生支持定时调度（每小时触发）
- Redis 同时服务队列broker和结果backend，减少基础设施
- 丰富的监控工具（Flower）可满足流水线状态监控需求

**Alternatives considered**:
- **Dramatiq**: 更现代但社区更小，监控工具不如Celery成熟
- **APScheduler**: 仅调度器，无分布式任务队列能力，不适合多步骤流水线

---

## R3: 向量存储 — pgvector vs Pinecone vs Weaviate vs Qdrant

**Decision**: PostgreSQL + pgvector extension

**Rationale**:
- 与业务数据同库，减少数据同步复杂度和基础设施成本
- HNSW索引支持高效近似最近邻搜索，100K级向量规模完全胜任
- 单用户场景无需分布式向量数据库的弹性扩展能力
- SQL查询可同时过滤元数据（分类、时间、评分）和向量相似度

**Alternatives considered**:
- **Pinecone**: 托管服务，按量付费成本较高，增加外部依赖
- **Weaviate**: 功能强大但部署运维复杂，当前规模杀鸡用牛刀
- **Qdrant**: 性能优秀但需要独立部署和维护

---

## R4: 前端框架 — Next.js vs Nuxt vs SvelteKit vs Vite+React

**Decision**: Next.js 15 (App Router)

**Rationale**:
- SSR/SSG 混合渲染，首页市场热点总览可SSG+ISR，文章详情SSR
- App Router 支持 React Server Components，减少客户端JS体积
- shadcn/ui + TailwindCSS 生态完整，快速构建投资仪表盘UI
- Recharts 图表库与React深度集成，适合雷达图、热力图等数据可视化

**Alternatives considered**:
- **Nuxt (Vue)**: Vue生态的数据可视化库不如React生态丰富
- **SvelteKit**: 性能好但组件库和图表库生态较小
- **Vite+React (SPA)**: 无SSR，首屏加载慢，SEO弱（虽本项目SEO非刚需）

---

## R5: AI模型选型 — 摘要/评分/向量化/兜底

**Decision**: 4模型分工策略

| 角色 | 模型 | 选择理由 |
|------|------|----------|
| AI1 摘要生成 | GPT-5-mini | 速度快、成本低（~$0.005/篇）、结构化输出稳定 |
| AI2 向量化 | text-embedding-3-large | OpenAI最新embedding模型，3072维，语义理解强 |
| AI3 Gravity评分 | Claude 3.5 Sonnet | 深度推理能力强、输出结构化JSON稳定、16维度评分需要复杂判断 |
| AI4 兜底爬虫 | Gemini 2.0 Flash | 多模态能力强、可"看"网页截图提取正文、成本适中 |

**Rationale**:
- 分工让每个模型在自己最擅长的领域工作，成本和质量双优化
- GPT-5-mini 的结构化输出(structured output)功能确保摘要schema一致性
- Claude Sonnet 的推理链能力适合多维度复杂评分任务
- Gemini Flash 的视觉理解能力是其他模型不具备的网页理解优势

---

## R6: RSS解析 — feedparser vs atoma vs rawdog

**Decision**: feedparser

**Rationale**:
- Python生态最成熟的RSS/Atom解析库，支持RSS 0.9x/1.0/2.0和Atom 0.3/1.0
- 内置容错解析，处理非标准格式的能力强
- 自动处理编码、日期解析、HTML实体等常见问题
- 活跃维护，社区庞大

**Alternatives considered**:
- **atoma**: 更严格的解析，对非标准RSS容错差
- **rawdog**: 过于底层，需要大量手动处理

---

## R7: 三路内容抓取策略

**Decision**: Firecrawl API + iFramely API + Gemini视觉兜底

| 工具 | 强项 | 用于字段 |
|------|------|----------|
| Firecrawl | 正文提取准确、Markdown格式输出 | 正文(备选)、元数据 |
| iFramely | 结构化元数据(oEmbed/OpenGraph)、标题提取 | 标题(首选)、描述、缩略图 |
| Gemini Flash | 视觉理解网页、处理JS渲染页面 | 正文(兜底)、标题(兜底) |
| RSS原始数据 | 图片URL最可靠 | 图片(首选)、发布时间、作者 |

**字段级Winner选择逻辑**:
1. 标题: iFramely > Gemini > Firecrawl > RSS原始
2. 正文: Gemini > Firecrawl > RSS原始 (长度和质量评估)
3. 图片: RSS > iFramely > Firecrawl
4. 发布时间: RSS > iFramely > Firecrawl
5. 作者: iFramely > RSS > Firecrawl

每个字段的选择基于：非空 → 长度/质量评分 → 来源优先级

---

## R8: 行业分类体系（投资导向）

**Decision**: 预定义分类 + AI动态标签双层体系

**一级分类（投资行业板块）**:
- 金融 (Finance)
- 科技 (Technology)
- 商业航天 (Commercial Space)
- 新能源 (New Energy)
- 医疗健康 (Healthcare)
- 农业 (Agriculture)
- 消费 (Consumer)
- 房地产 (Real Estate)
- 制造业 (Manufacturing)
- 加密货币 (Crypto)
- 宏观经济 (Macro Economy)
- 监管政策 (Regulation)

**二级标签**: AI摘要引擎动态生成，如"芯片制裁"、"利率决议"、"SpaceX星舰"等

**Rationale**: 一级分类固定对应投资板块，便于快速扫描；二级标签灵活捕捉细分热点

---

## R9: 聚类算法 — HNSW参数与阈值

**Decision**: pgvector HNSW索引 + 余弦相似度 + 阈值0.82

**Rationale**:
- HNSW (Hierarchical Navigable Small World) 是当前最高效的ANN算法之一
- 余弦相似度适合文本语义向量（已归一化）
- 阈值0.82经验值：高于此值的文章大概率讨论同一事件，低于则独立
- pgvector的`ivfflat`和`hnsw`两种索引中，HNSW查询更快但构建更慢，适合本场景（写少读多）

**HNSW参数建议**:
- `m = 16` (每层连接数)
- `ef_construction = 200` (构建时搜索宽度)
- `ef_search = 100` (查询时搜索宽度)

---

## R10: 部署策略

**Decision**: Docker Compose 单机部署

**Rationale**:
- 单用户投资工具，无需Kubernetes等复杂编排
- 4个容器：PostgreSQL + Redis + Backend(FastAPI+Celery) + Frontend(Next.js)
- docker-compose.yml 一键启动全部服务
- 未来如需扩展可平滑迁移到K8s

**Alternatives considered**:
- **Kubernetes**: 当前规模过度工程
- **Serverless**: 流水线是长时间运行的定时任务，不适合serverless架构
- **裸机部署**: 缺乏隔离和可重复性
