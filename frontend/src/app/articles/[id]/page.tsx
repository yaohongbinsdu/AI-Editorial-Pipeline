'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, ExternalLink, Clock, User, Tag } from 'lucide-react'
import { getArticle } from '@/lib/api'
import type { ArticleDetail } from '@/types'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { cn, formatRelativeTime, scoreColor, voteColor } from '@/lib/utils'

export default function ArticleDetailPage() {
  const params = useParams()
  const [article, setArticle] = useState<ArticleDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!params.id) return
    const load = async () => {
      try {
        const data = await getArticle(params.id as string)
        setArticle(data)
      } catch (err) {
        console.error('Failed to load article:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [params.id])

  if (loading) {
    return (
      <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
    )
  }

  if (!article) {
    return (
      <div className="py-12 text-center text-sm text-zinc-500">文章未找到</div>
    )
  }

  const summary = article.summary
  const gravity = article.gravity_score

  return (
    <div className="mx-auto max-w-4xl">
      <Link
        href="/"
        className="mb-4 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300"
      >
        <ArrowLeft size={14} />
        返回
      </Link>

      {article.final_image_url && (
        <div className="mb-6 overflow-hidden rounded-lg">
          <img
            src={article.final_image_url}
            alt=""
            className="h-64 w-full object-cover"
          />
        </div>
      )}

      <h1 className="mb-3 text-2xl font-bold leading-tight text-zinc-100">
        {summary?.rewritten_title || article.final_title}
      </h1>

      <div className="mb-6 flex flex-wrap items-center gap-3 text-sm text-zinc-500">
        {article.source && (
          <span className="font-medium text-zinc-400">{article.source.name}</span>
        )}
        {article.published_at && (
          <span className="inline-flex items-center gap-1">
            <Clock size={12} />
            {formatRelativeTime(article.published_at)}
          </span>
        )}
        {article.author && (
          <span className="inline-flex items-center gap-1">
            <User size={12} />
            {article.author}
          </span>
        )}
        <a
          href={article.original_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1 text-blue-400 hover:text-blue-300"
        >
          <ExternalLink size={12} />
          原文
        </a>
      </div>

      {/* Summary section */}
      {summary && (
        <div className="mb-6 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h2 className="mb-2 text-sm font-semibold text-zinc-300">AI摘要</h2>
          <p className="mb-3 text-sm leading-relaxed text-zinc-400">
            {summary.human_tldr}
          </p>

          {summary.key_points && summary.key_points.length > 0 && (
            <div className="mb-3">
              <h3 className="mb-1.5 text-xs font-medium text-zinc-500">关键要点</h3>
              <ul className="space-y-1">
                {(summary.key_points as string[]).map((point, i) => (
                  <li key={i} className="flex gap-2 text-xs text-zinc-400">
                    <span className="mt-0.5 shrink-0 text-red-500">{i + 1}.</span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex flex-wrap gap-2">
            {summary.category && (
              <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-300">
                {CATEGORY_LABELS[summary.category as CategorySlug] || summary.category}
              </span>
            )}
            {summary.tags &&
              (summary.tags as string[]).map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center gap-1 rounded-full bg-zinc-800/50 px-2 py-0.5 text-[11px] text-zinc-500"
                >
                  <Tag size={10} />
                  {tag}
                </span>
              ))}
          </div>
        </div>
      )}

      {/* Gravity Score section */}
      {gravity && (
        <div className="mb-6 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-zinc-300">Gravity评分</h2>
            <div className="flex items-center gap-3">
              {gravity.editorial_vote && (
                <span
                  className={cn(
                    'rounded-full border px-2.5 py-0.5 text-xs font-semibold',
                    voteColor(gravity.editorial_vote),
                  )}
                >
                  {gravity.editorial_vote === 'must_read'
                    ? '必读'
                    : gravity.editorial_vote === 'interesting'
                      ? '有趣'
                      : '略过'}
                </span>
              )}
              <span className={cn('text-lg font-bold', scoreColor(gravity.composite_score))}>
                {gravity.composite_score.toFixed(1)}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
            {[
              { label: '行业影响', value: gravity.industry_impact },
              { label: '消费者影响', value: gravity.consumer_impact },
              { label: '可操作性', value: gravity.actionability },
              { label: '风险紧迫', value: gravity.risk_urgency },
              { label: '新颖度', value: gravity.novelty },
              { label: '技术深度', value: gravity.technical_depth },
              { label: '二阶效应', value: gravity.second_order_potential },
              { label: '建设者相关', value: gravity.builder_relevance },
              { label: '娱乐价值', value: gravity.entertainment_value },
              { label: '信噪比', value: gravity.signal_to_noise },
              { label: '传播潜力', value: gravity.viral_potential },
              { label: '早期趋势', value: gravity.early_trend_signal },
            ].map((dim) => (
              <div key={dim.label} className="flex items-center justify-between rounded bg-zinc-800/50 px-2 py-1.5">
                <span className="text-zinc-500">{dim.label}</span>
                <span className={scoreColor(dim.value)}>{dim.value.toFixed(1)}</span>
              </div>
            ))}
          </div>

          {gravity.reasoning && (
            <p className="mt-3 text-xs italic text-zinc-600">{gravity.reasoning}</p>
          )}
        </div>
      )}

      {/* Cluster link */}
      {article.cluster && (
        <div className="mb-6 rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
          <Link
            href={`/clusters/${article.cluster.id}`}
            className="flex items-center justify-between text-sm hover:text-zinc-200"
          >
            <span className="text-zinc-400">
              所属聚类: <span className="font-medium text-zinc-200">{article.cluster.title}</span>
            </span>
            <span className="text-xs text-zinc-600">
              {article.cluster.article_count} 篇文章
            </span>
          </Link>
        </div>
      )}

      {/* Article content */}
      <div className="prose prose-invert prose-zinc max-w-none text-sm leading-relaxed">
        <div dangerouslySetInnerHTML={{ __html: article.final_content }} />
      </div>
    </div>
  )
}
