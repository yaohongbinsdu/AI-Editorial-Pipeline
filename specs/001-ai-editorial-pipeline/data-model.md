# Data Model: AI Editorial Pipeline

**Date**: 2026-02-14
**Branch**: `001-ai-editorial-pipeline`
**Storage**: PostgreSQL 16 + pgvector

## Entity Relationship Overview

```text
RSSSource 1──────* Article
Article   1──────1 Summary
Article   1──────1 Vector
Article   1──────1 GravityScore
Article   *──────1 Cluster (nullable)
PipelineRun 1────* PipelineStepLog
```

---

## Entities

### RSSSource (RSS源)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| url | TEXT | UNIQUE, NOT NULL | RSS源URL |
| name | VARCHAR(255) | NOT NULL | 源名称（如"Reuters Finance"） |
| category | VARCHAR(50) | NOT NULL | 一级行业分类 |
| enabled | BOOLEAN | DEFAULT true | 是否启用 |
| fetch_interval_minutes | INTEGER | DEFAULT 60 | 拉取间隔(分钟) |
| last_fetched_at | TIMESTAMP | NULLABLE | 最后成功拉取时间 |
| last_error | TEXT | NULLABLE | 最近一次错误信息 |
| consecutive_failures | INTEGER | DEFAULT 0 | 连续失败次数 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

**Indexes**: `idx_rss_source_enabled` on (enabled), `idx_rss_source_category` on (category)

**Validation Rules**:
- url MUST be a valid URL format
- category MUST be one of the predefined industry categories
- consecutive_failures ≥ 5 triggers automatic disable + alert

---

### Article (文章)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| source_id | UUID | FK → RSSSource.id, NOT NULL | 来源RSS |
| original_url | TEXT | UNIQUE, NOT NULL | 原始文章URL (去重键) |
| original_title | VARCHAR(500) | NULLABLE | RSS原始标题 |
| original_content | TEXT | NULLABLE | RSS原始内容 |
| original_image_url | TEXT | NULLABLE | RSS原始图片 |
| firecrawl_title | VARCHAR(500) | NULLABLE | Firecrawl抓取的标题 |
| firecrawl_content | TEXT | NULLABLE | Firecrawl抓取的正文 |
| iframely_title | VARCHAR(500) | NULLABLE | iFramely抓取的标题 |
| iframely_content | TEXT | NULLABLE | iFramely抓取的正文 |
| iframely_image_url | TEXT | NULLABLE | iFramely抓取的图片 |
| gemini_title | VARCHAR(500) | NULLABLE | Gemini抓取的标题 |
| gemini_content | TEXT | NULLABLE | Gemini抓取的正文 |
| final_title | VARCHAR(500) | NOT NULL | 字段择优后的最终标题 |
| final_content | TEXT | NOT NULL | 字段择优后的最终正文 |
| final_image_url | TEXT | NULLABLE | 字段择优后的最终图片 |
| published_at | TIMESTAMP | NULLABLE | 文章发布时间 |
| author | VARCHAR(255) | NULLABLE | 作者 |
| status | VARCHAR(30) | NOT NULL, DEFAULT 'pending' | 处理状态 |
| cluster_id | UUID | FK → Cluster.id, NULLABLE | 所属聚类 |
| created_at | TIMESTAMP | NOT NULL | 入库时间 |
| updated_at | TIMESTAMP | NOT NULL | 更新时间 |

**Status State Machine**:
```text
pending → fetching → fetched → summarizing → summarized →
vectorizing → vectorized → scoring → completed
                                    ↘ fetch_failed
                          ↘ summary_failed
                                      ↘ score_failed
```

**Indexes**:
- `idx_article_url` UNIQUE on (original_url)
- `idx_article_status` on (status)
- `idx_article_source` on (source_id)
- `idx_article_cluster` on (cluster_id)
- `idx_article_published` on (published_at DESC)
- `idx_article_created` on (created_at DESC)

**Validation Rules**:
- original_url MUST be unique (去重)
- final_content length MUST be ≥ 50 characters for summarization to proceed
- status transitions follow the state machine above

---

### Summary (摘要包)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| article_id | UUID | FK → Article.id, UNIQUE, NOT NULL | 关联文章 |
| human_tldr | VARCHAR(300) | NOT NULL | 人类版TLDR (≤100字) |
| vector_tldr | TEXT | NOT NULL | 向量版TLDR (≤300字, 关键词密集) |
| key_points | JSONB | NOT NULL | 5个Key Points (JSON数组) |
| rewritten_title | VARCHAR(500) | NOT NULL | AI重写标题 |
| category | VARCHAR(50) | NOT NULL | 一级行业分类 |
| tags | JSONB | NOT NULL | 二级分类标签 (JSON数组) |
| model_used | VARCHAR(50) | NOT NULL | 使用的AI模型标识 |
| generation_time_ms | INTEGER | NOT NULL | 生成耗时(毫秒) |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

**Indexes**:
- `idx_summary_article` UNIQUE on (article_id)
- `idx_summary_category` on (category)

**Validation Rules**:
- key_points MUST be a JSON array with exactly 5 elements
- tags MUST be a non-empty JSON array
- category MUST be one of the predefined industry categories
- human_tldr length MUST be ≤ 300 characters

---

### Vector (语义向量)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| article_id | UUID | FK → Article.id, UNIQUE, NOT NULL | 关联文章 |
| embedding | vector(3072) | NOT NULL | 3072维语义向量 (text-embedding-3-large) |
| model_used | VARCHAR(50) | NOT NULL | 使用的Embedding模型标识 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

**Indexes**:
- `idx_vector_article` UNIQUE on (article_id)
- `idx_vector_embedding_hnsw` HNSW on (embedding vector_cosine_ops) WITH (m=16, ef_construction=200)

---

### Cluster (聚类/事件组)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| title | VARCHAR(500) | NOT NULL | 聚类标题 (由AI根据成员文章生成) |
| category | VARCHAR(50) | NOT NULL | 一级行业分类 |
| article_count | INTEGER | NOT NULL, DEFAULT 0 | 包含文章数 |
| centroid | vector(3072) | NULLABLE | 聚类质心向量 |
| expansion_triggered | BOOLEAN | DEFAULT false | 是否已触发扩展搜索 |
| expansion_query | TEXT | NULLABLE | 扩展搜索使用的查询词 |
| first_seen_at | TIMESTAMP | NOT NULL | 最早文章时间 |
| last_updated_at | TIMESTAMP | NOT NULL | 最新文章时间 |
| created_at | TIMESTAMP | NOT NULL | 聚类创建时间 |

**Indexes**:
- `idx_cluster_category` on (category)
- `idx_cluster_article_count` on (article_count DESC)
- `idx_cluster_updated` on (last_updated_at DESC)

**Validation Rules**:
- article_count ≥ 3 AND expansion_triggered = false → trigger expansion
- article_count > 50 → trigger sub-cluster split

---

### GravityScore (编辑评分)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| article_id | UUID | FK → Article.id, UNIQUE, NOT NULL | 关联文章 |
| industry_impact | FLOAT | NOT NULL | 行业影响力 (0-10) |
| consumer_impact | FLOAT | NOT NULL | 消费者影响 (0-10) |
| actionability | FLOAT | NOT NULL | 行动性 (0-10) |
| risk_urgency | FLOAT | NOT NULL | 紧急程度 (0-10) |
| novelty | FLOAT | NOT NULL | 新颖性 (0-10) |
| technical_depth | FLOAT | NOT NULL | 技术深度 (0-10) |
| second_order_potential | FLOAT | NOT NULL | 二阶效应 (0-10) |
| builder_relevance | FLOAT | NOT NULL | 开发者价值 (0-10) |
| entertainment_value | FLOAT | NOT NULL | 谈资价值 (0-10) |
| signal_to_noise | FLOAT | NOT NULL | 信噪比 (0-10) |
| viral_potential | FLOAT | NOT NULL | 传播潜力 (0-10) |
| early_trend_signal | FLOAT | NOT NULL | 早期趋势 (0-10) |
| pr_fluff | FLOAT | NOT NULL | 公关水文标记 (0-10, 越高越水) |
| speculation | FLOAT | NOT NULL | 猜测程度 (0-10, 越高越猜) |
| concreteness | FLOAT | NOT NULL | 具体性 (0-10) |
| paid_sponsorship | FLOAT | NOT NULL | 付费赞助标记 (0-10, 越高越疑似) |
| editorial_vote | VARCHAR(20) | NOT NULL | 编辑投票: must_read/interesting/skip |
| novelty_gate | BOOLEAN | NOT NULL | 新颖性门槛: true=pass, false=fail |
| composite_score | FLOAT | NOT NULL | 综合评分 (加权计算) |
| reasoning | TEXT | NULLABLE | AI评分推理过程 |
| model_used | VARCHAR(50) | NOT NULL | 使用的AI模型标识 |
| scoring_time_ms | INTEGER | NOT NULL | 评分耗时(毫秒) |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

**Indexes**:
- `idx_gravity_article` UNIQUE on (article_id)
- `idx_gravity_composite` on (composite_score DESC)
- `idx_gravity_novelty_gate` on (novelty_gate)
- `idx_gravity_editorial_vote` on (editorial_vote)

**Validation Rules**:
- All dimension scores MUST be in range [0, 10]
- editorial_vote MUST be one of: must_read, interesting, skip
- novelty_gate = false → article excluded from display
- composite_score calculated as weighted sum of positive dimensions minus quality flags

---

### PipelineRun (流水线执行记录)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| started_at | TIMESTAMP | NOT NULL | 开始时间 |
| completed_at | TIMESTAMP | NULLABLE | 完成时间 |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'running' | running/completed/failed |
| articles_discovered | INTEGER | DEFAULT 0 | 发现的新文章数 |
| articles_processed | INTEGER | DEFAULT 0 | 成功处理数 |
| articles_failed | INTEGER | DEFAULT 0 | 处理失败数 |
| duration_seconds | FLOAT | NULLABLE | 总耗时(秒) |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

**Indexes**:
- `idx_pipeline_run_started` on (started_at DESC)
- `idx_pipeline_run_status` on (status)

---

### PipelineStepLog (流水线步骤日志)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 唯一标识 |
| pipeline_run_id | UUID | FK → PipelineRun.id, NOT NULL | 所属流水线 |
| article_id | UUID | FK → Article.id, NULLABLE | 关联文章 |
| step_name | VARCHAR(50) | NOT NULL | 步骤名: rss_fetch/scrape/summarize/vectorize/cluster/expand/score |
| status | VARCHAR(20) | NOT NULL | success/failed/skipped |
| duration_ms | INTEGER | NULLABLE | 步骤耗时(毫秒) |
| error_message | TEXT | NULLABLE | 错误信息 |
| retry_count | INTEGER | DEFAULT 0 | 重试次数 |
| metadata | JSONB | NULLABLE | 附加元数据 |
| created_at | TIMESTAMP | NOT NULL | 创建时间 |

**Indexes**:
- `idx_step_log_run` on (pipeline_run_id)
- `idx_step_log_article` on (article_id)
- `idx_step_log_step_status` on (step_name, status)

---

## Predefined Category Enum

```text
finance          # 金融
technology       # 科技
commercial_space # 商业航天
new_energy       # 新能源
healthcare       # 医疗健康
agriculture      # 农业
consumer         # 消费
real_estate      # 房地产
manufacturing    # 制造业
crypto           # 加密货币
macro_economy    # 宏观经济
regulation       # 监管政策
other            # 其他
```
