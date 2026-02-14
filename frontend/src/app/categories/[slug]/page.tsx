'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import { getArticles, type ArticleListParams } from '@/lib/api'
import type { ArticleBrief, PaginatedResponse } from '@/types'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { ArticleCard } from '@/components/article-card'

export default function CategoryPage() {
  const params = useParams()
  const slug = params.slug as string
  const [data, setData] = useState<PaginatedResponse<ArticleBrief> | null>(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const result = await getArticles({ category: slug, page, page_size: 20 })
        setData(result)
      } catch (err) {
        console.error('Failed to load articles:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [slug, page])

  const label = CATEGORY_LABELS[slug as CategorySlug] || slug

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">{label}</h1>
        {data && (
          <p className="mt-1 text-sm text-zinc-500">
            共 {data.total} 篇文章
          </p>
        )}
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
      ) : !data || data.items.length === 0 ? (
        <div className="py-12 text-center text-sm text-zinc-500">
          该分类暂无文章
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
