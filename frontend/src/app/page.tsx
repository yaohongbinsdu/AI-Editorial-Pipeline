'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getDashboardOverview, getDashboardTrending, getArticles } from '@/lib/api'
import type { ArticleBrief } from '@/types'
import { ArticleCard } from '@/components/article-card'
import { MarketHeatmap } from '@/components/market-heatmap'
import { TrendingBar } from '@/components/trending-bar'
import { PipelineStatus } from '@/components/pipeline-status'

interface OverviewData {
  total_articles: number
  category_breakdown: { slug: string; article_count: number }[]
  top_clusters: { id: string; title: string; category: string; article_count: number }[]
  must_read_articles: {
    id: string
    final_title: string
    rewritten_title: string | null
    human_tldr: string | null
    source_name: string
    published_at: string | null
    final_image_url: string | null
  }[]
  pipeline_health: {
    last_run_at: string | null
    last_run_status: string | null
    articles_processed_24h: number
  }
}

interface TrendingData {
  trending_clusters: {
    id: string
    title: string
    category: string
    article_count: number
    last_updated_at: string | null
  }[]
  trending_articles: {
    id: string
    final_title: string
    rewritten_title: string | null
    human_tldr: string | null
    source_name: string
    published_at: string | null
  }[]
}

export default function HomePage() {
  const [overview, setOverview] = useState<OverviewData | null>(null)
  const [trending, setTrending] = useState<TrendingData | null>(null)
  const [latestArticles, setLatestArticles] = useState<ArticleBrief[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const [ov, tr, articles] = await Promise.all([
          getDashboardOverview(),
          getDashboardTrending(),
          getArticles({ page: 1, page_size: 20, sort_by: 'created_at', order: 'desc' }),
        ])
        setOverview(ov)
        setTrending(tr)
        setLatestArticles(articles.items)
      } catch (err) {
        console.error('Failed to load dashboard:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  if (loading) {
    return (
      <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
    )
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
      <div className="space-y-6">
        {/* Market Heatmap */}
        <section>
          <h2 className="mb-3 text-sm font-semibold text-zinc-300">行业热度</h2>
          <MarketHeatmap categories={overview?.category_breakdown || []} />
        </section>

        {/* Trending Events */}
        {trending && trending.trending_clusters.length > 0 && (
          <section>
            <h2 className="mb-3 text-sm font-semibold text-zinc-300">热门事件</h2>
            <TrendingBar clusters={trending.trending_clusters} />
          </section>
        )}

        {/* Must Read */}
        {overview && overview.must_read_articles.length > 0 && (
          <section>
            <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold text-zinc-300">
              <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-red-500" />
              必读文章
            </h2>
            <div className="space-y-2">
              {overview.must_read_articles.map((a) => (
                <Link
                  key={a.id}
                  href={`/articles/${a.id}`}
                  className="block rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
                >
                  <h3 className="text-sm font-medium text-zinc-200">
                    {a.rewritten_title || a.final_title}
                  </h3>
                  {a.human_tldr && (
                    <p className="mt-1 line-clamp-1 text-xs text-zinc-500">
                      {a.human_tldr}
                    </p>
                  )}
                  <div className="mt-1 text-[10px] text-zinc-600">
                    {a.source_name}
                  </div>
                </Link>
              ))}
            </div>
          </section>
        )}

        {/* Latest Articles */}
        <section>
          <h2 className="mb-3 text-sm font-semibold text-zinc-300">最新文章</h2>
          {latestArticles.length === 0 ? (
            <div className="py-8 text-center text-sm text-zinc-500">
              暂无文章，请先添加RSS源并运行流水线
            </div>
          ) : (
            <div className="space-y-2">
              {latestArticles.map((article) => (
                <ArticleCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </section>
      </div>

      {/* Right Sidebar */}
      <div className="space-y-4">
        <PipelineStatus />

        {overview && (
          <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
            <h3 className="mb-2 text-xs font-medium text-zinc-400">24小时统计</h3>
            <div className="text-2xl font-bold text-zinc-100">
              {overview.total_articles}
            </div>
            <div className="text-[11px] text-zinc-500">篇新文章</div>

            {overview.category_breakdown.length > 0 && (
              <div className="mt-3 space-y-1">
                {overview.category_breakdown.slice(0, 8).map((cat) => (
                  <Link
                    key={cat.slug}
                    href={`/categories/${cat.slug}`}
                    className="flex items-center justify-between text-[11px] hover:text-zinc-300"
                  >
                    <span className="text-zinc-500">{cat.slug}</span>
                    <span className="font-medium text-zinc-400">
                      {cat.article_count}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
