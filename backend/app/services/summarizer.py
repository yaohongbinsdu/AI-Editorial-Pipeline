from __future__ import annotations

import json
import time
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.article import Article
from app.models.summary import Summary
from app.utils.logging import get_logger
from app.utils.retry import async_retry

logger = get_logger("summarizer")

CATEGORY_DEFINITIONS = """
行业分类定义(选择最匹配的一个):
- finance: 银行、保险、证券、基金、支付、金融科技
- technology: 软件、硬件、AI、半导体、互联网、云计算、SaaS
- commercial_space: 火箭、卫星、太空探索、航天制造
- new_energy: 太阳能、风能、电池、储能、氢能、电动车
- healthcare: 制药、生物技术、医疗器械、数字医疗、基因编辑
- agriculture: 农业科技、食品安全、农产品、智慧农业
- consumer: 零售、电商、品牌、餐饮、旅游、娱乐
- real_estate: 房地产开发、物业管理、REITs、建筑
- manufacturing: 工业自动化、机器人、3D打印、供应链
- crypto: 比特币、以太坊、DeFi、NFT、Web3、区块链
- macro_economy: GDP、利率、通胀、就业、贸易、央行政策
- regulation: 法规、监管政策、反垄断、数据隐私、合规
- other: 不属于以上任何分类
"""

SYSTEM_PROMPT = f"""你是一位专业的投资新闻编辑AI。为给定文章生成结构化摘要。

{CATEGORY_DEFINITIONS}

输出要求:
1. human_tldr: 用中文写一句话摘要(≤100字)，简洁直白，投资者一看就懂
2. vector_tldr: 用英文写SEO风格摘要(≤300字)，塞满关键词、实体名称、数字、日期
3. key_points: 恰好5个要点(中文)，突出投资相关信息、市场影响、数据变化
4. rewritten_title: 重写标题(中文)，比原标题更抓眼球，突出投资角度
5. category: 从上述分类中选择最匹配的一个slug
6. tags: 3-8个标签(中文)，用于文章检索和分类

严格按JSON schema输出。"""


class SummarySchema(BaseModel):
    human_tldr: str = Field(max_length=100, description="一句话中文摘要")
    vector_tldr: str = Field(max_length=300, description="英文SEO摘要")
    key_points: list[str] = Field(min_length=5, max_length=5, description="5个关键要点")
    rewritten_title: str = Field(description="重写标题")
    category: str = Field(description="行业分类slug")
    tags: list[str] = Field(min_length=3, max_length=8, description="标签列表")

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        valid = {
            "finance", "technology", "commercial_space", "new_energy",
            "healthcare", "agriculture", "consumer", "real_estate",
            "manufacturing", "crypto", "macro_economy", "regulation", "other",
        }
        if v not in valid:
            return "other"
        return v


class Summarizer:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    @async_retry(max_retries=3, backoff_base=2.0)
    async def generate_summary(self, article: Article, db: AsyncSession) -> Summary | None:
        content = article.final_content or ""
        if len(content.strip()) < 50:
            logger.warning(
                "content_insufficient",
                article_id=str(article.id),
                content_length=len(content),
            )
            return None

        title = article.final_title or ""
        user_message = f"标题: {title}\n\n正文:\n{content[:8000]}"

        start_time = time.monotonic()

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1500,
        )

        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        raw = response.choices[0].message.content or "{}"
        data = json.loads(raw)
        schema = SummarySchema(**data)

        summary = Summary(
            article_id=article.id,
            human_tldr=schema.human_tldr,
            vector_tldr=schema.vector_tldr,
            key_points=schema.key_points,
            rewritten_title=schema.rewritten_title,
            category=schema.category,
            tags=schema.tags,
            model_used=response.model or "gpt-4o-mini",
            generation_time_ms=elapsed_ms,
        )
        db.add(summary)

        article.status = "summarized"
        logger.info(
            "summary_generated",
            article_id=str(article.id),
            category=schema.category,
            elapsed_ms=elapsed_ms,
        )
        return summary

    async def summarize_article(self, article: Article, db: AsyncSession) -> None:
        article.status = "summarizing"
        try:
            result = await self.generate_summary(article, db)
            if result is None:
                article.status = "summary_failed"
        except Exception as exc:
            article.status = "summary_failed"
            logger.error("summarize_failed", article_id=str(article.id), error=str(exc))
            raise
