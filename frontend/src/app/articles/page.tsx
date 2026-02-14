'use client'

import { useEffect, useState } from 'react'
import { getArticles, type ArticleListParams } from '@/lib/api'
import type { ArticleBrief, PaginatedResponse, CategorySlug } from '@/types'
import { CATEGORY_LABELS } from '@/types'
import { ArticleCard } from '@/components/article-card'

export default function ArticlesPage() {
  const [data, setData] = useState<PaginatedResponse<ArticleBrief> | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState<string>('')
  const [sortBy, setSortBy] = useState<string>('created_at')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const params: ArticleListParams = {
          page,
          page_size: 20,
          sort_by: sortBy,
          order: 'desc',
        }
        if (category) params.category = category
        const result = await getArticles(params)
        setData(result)
      } catch (err) {
        console.error('Failed to load articles:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [page, category, sortBy])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">文章列表</h1>
        {data && (
          <p className="mt-1 text-sm text-zinc-500">共 {data.total} 篇文章</p>
        )}
      </div>

      {/* Filters */}
      <div className="mb-4 flex flex-wrap gap-3">
        <select
          value={category}
          onChange={(e) => { setCategory(e.target.value); setPage(1) }}
          className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 focus:border-red-500 focus:outline-none"
        >
          <option value="">全部分类</option>
          {(Object.entries(CATEGORY_LABELS) as [CategorySlug, string][]).map(
            ([slug, label]) => (
              <option key={slug} value={slug}>{label}</option>
            ),
          )}
        </select>
        <select
          value={sortBy}
          onChange={(e) => { setSortBy(e.target.value); setPage(1) }}
          className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 focus:border-red-500 focus:outline-none"
        >
          <option value="created_at">最新发现</option>
          <option value="published_at">发布时间</option>
          <option value="composite_score">评分</option>
        </select>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
      ) : !data || data.items.length === 0 ? (
        <div className="py-12 text-center text-sm text-zinc-500">
          暂无文章，请先添加RSS源并运行流水线
        </div>
      ) : (
        <>
          <div className="grid gap-3">
            {data.items.map((article) => (
              <ArticleCard key={article.id} article={article} />
            ))}
          </div>

          {data.total_pages > 1 && (
            <div className="mt-6 flex items-center justify-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1}
                className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700 disabled:opacity-40"
              >
                上一页
              </button>
              <span className="text-sm text-zinc-500">
                {page} / {data.total_pages}
              </span>
              <button
                onClick={() => setPage((p) => Math.min(data!.total_pages, p + 1))}
                disabled={page >= data.total_pages}
                className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700 disabled:opacity-40"
              >
                下一页
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
