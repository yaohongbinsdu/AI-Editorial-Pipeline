from __future__ import annotations

import json
import time

import anthropic
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.article import Article
from app.models.gravity_score import GravityScore
from app.utils.logging import get_logger
from app.utils.retry import async_retry

logger = get_logger("gravity_engine")

SYSTEM_PROMPT = """你是Gravity Engine——一个投资新闻评分AI。对每篇文章进行16维度深度评分。

## 评分维度 (每个0-10分)

### 层面1: 影响力 (Impact)
1. industry_impact — 对该行业的变革影响程度
2. consumer_impact — 对消费者/用户的直接影响
3. actionability — 投资者是否可以据此采取行动
4. risk_urgency — 是否涉及紧迫风险或机会窗口

### 层面2: 智识引力 (Intellectual Gravity)
5. novelty — 信息新颖度,是否首次披露
6. technical_depth — 技术/分析深度
7. second_order_potential — 二阶效应潜力(连锁反应)
8. builder_relevance — 对创业者/建设者的相关性

### 层面3: 叠加信号 (Overlay Signals)
9. entertainment_value — 故事性/可读性
10. signal_to_noise — 信号vs噪音比
11. viral_potential — 传播潜力(0-10映射传播力)
12. early_trend_signal — 早期趋势信号强度

### 层面4: 质量标记 (Quality Markers) — 负向指标,越高越差
13. pr_fluff — PR软文程度
14. speculation — 无依据臆测程度
15. concreteness — 内容具体程度(反向:越高越好)
16. paid_sponsorship — 付费赞助可能性

## Editorial Vote
- must_read: 重大新闻,投资者必读
- interesting: 有价值信息,值得一看
- skip: 低价值或噪音

## Novelty Gate
- true: 包含新信息或新角度
- false: 纯重复报道或旧闻翻炒

严格输出JSON,包含所有16个维度分数 + editorial_vote + novelty_gate + reasoning(一句话解释评分逻辑)。"""


class GravitySchema(BaseModel):
    industry_impact: float = Field(ge=0, le=10)
    consumer_impact: float = Field(ge=0, le=10)
    actionability: float = Field(ge=0, le=10)
    risk_urgency: float = Field(ge=0, le=10)
    novelty: float = Field(ge=0, le=10)
    technical_depth: float = Field(ge=0, le=10)
    second_order_potential: float = Field(ge=0, le=10)
    builder_relevance: float = Field(ge=0, le=10)
    entertainment_value: float = Field(ge=0, le=10)
    signal_to_noise: float = Field(ge=0, le=10)
    viral_potential: float = Field(ge=0, le=10)
    early_trend_signal: float = Field(ge=0, le=10)
    pr_fluff: float = Field(ge=0, le=10)
    speculation: float = Field(ge=0, le=10)
    concreteness: float = Field(ge=0, le=10)
    paid_sponsorship: float = Field(ge=0, le=10)
    editorial_vote: str
    novelty_gate: bool
    reasoning: str = ""

    @field_validator("editorial_vote")
    @classmethod
    def validate_vote(cls, v: str) -> str:
        if v not in ("must_read", "interesting", "skip"):
            return "skip"
        return v


def compute_composite_score(s: GravitySchema) -> float:
    impact = (s.industry_impact + s.consumer_impact + s.actionability + s.risk_urgency) / 4
    intellectual = (s.novelty + s.technical_depth + s.second_order_potential + s.builder_relevance) / 4
    overlay = (s.entertainment_value + s.signal_to_noise + s.viral_potential + s.early_trend_signal) / 4
    penalty = (s.pr_fluff + s.speculation + s.paid_sponsorship) / 3

    score = impact * 0.35 + intellectual * 0.35 + overlay * 0.20 + s.concreteness * 0.10 - penalty * 0.10

    return round(max(0, min(10, score)), 2)


class GravityEngine:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

    @async_retry(max_retries=3, backoff_base=2.0)
    async def score_article(self, article: Article, db: AsyncSession) -> GravityScore | None:
        summary = article.summary
        content = article.final_content or ""

        if len(content.strip()) < 50:
            logger.warning("content_too_short_for_scoring", article_id=str(article.id))
            return None

        user_message = f"""标题: {article.final_title}
分类: {summary.category if summary else 'unknown'}
标签: {', '.join(summary.tags) if summary and summary.tags else 'N/A'}
摘要: {summary.human_tldr if summary else 'N/A'}

正文:
{content[:6000]}"""

        start_time = time.monotonic()

        response = await self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        schema = GravitySchema(**data)
        composite = compute_composite_score(schema)

        gravity = GravityScore(
            article_id=article.id,
            industry_impact=schema.industry_impact,
            consumer_impact=schema.consumer_impact,
            actionability=schema.actionability,
            risk_urgency=schema.risk_urgency,
            novelty=schema.novelty,
            technical_depth=schema.technical_depth,
            second_order_potential=schema.second_order_potential,
            builder_relevance=schema.builder_relevance,
            entertainment_value=schema.entertainment_value,
            signal_to_noise=schema.signal_to_noise,
            viral_potential=schema.viral_potential,
            early_trend_signal=schema.early_trend_signal,
            pr_fluff=schema.pr_fluff,
            speculation=schema.speculation,
            concreteness=schema.concreteness,
            paid_sponsorship=schema.paid_sponsorship,
            editorial_vote=schema.editorial_vote,
            novelty_gate=schema.novelty_gate,
            composite_score=composite,
            reasoning=schema.reasoning,
            model_used=response.model or "claude-sonnet-4-20250514",
            scoring_time_ms=elapsed_ms,
        )
        db.add(gravity)

        article.status = "scored"
        logger.info(
            "article_scored",
            article_id=str(article.id),
            composite_score=composite,
            editorial_vote=schema.editorial_vote,
            novelty_gate=schema.novelty_gate,
            elapsed_ms=elapsed_ms,
        )
        return gravity

    async def score_and_update(self, article: Article, db: AsyncSession) -> None:
        article.status = "scoring"
        try:
            result = await self.score_article(article, db)
            if result is None:
                article.status = "score_failed"
        except Exception as exc:
            article.status = "score_failed"
            logger.error("scoring_failed", article_id=str(article.id), error=str(exc))
            raise
