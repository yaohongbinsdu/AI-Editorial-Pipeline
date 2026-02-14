'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Layers } from 'lucide-react'
import { getClusters, type ClusterListParams } from '@/lib/api'
import type { ClusterBrief, PaginatedResponse, CategorySlug } from '@/types'
import { CATEGORY_LABELS } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

export default function ClustersPage() {
  const [data, setData] = useState<PaginatedResponse<ClusterBrief> | null>(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [category, setCategory] = useState<string>('')

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const params: ClusterListParams = { page, page_size: 20 }
        if (category) params.category = category
        const result = await getClusters(params)
        setData(result)
      } catch (err) {
        console.error('Failed to load clusters:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [page, category])

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">事件聚类</h1>
        {data && (
          <p className="mt-1 text-sm text-zinc-500">共 {data.total} 个聚类</p>
        )}
      </div>

      <div className="mb-4">
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
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
      ) : !data || data.items.length === 0 ? (
        <div className="py-12 text-center text-sm text-zinc-500">
          暂无聚类，运行流水线后系统会自动将相似文章聚合为事件
        </div>
      ) : (
        <>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((cluster) => (
              <Link
                key={cluster.id}
                href={`/clusters/${cluster.id}`}
                className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
              >
                <div className="mb-2 flex items-center gap-2">
                  <Layers size={14} className="text-zinc-500" />
                  <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
                    {CATEGORY_LABELS[cluster.category as CategorySlug] || cluster.category}
                  </span>
                  <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-400">
                    {cluster.article_count} 篇
                  </span>
                </div>
                <h3 className="mb-1 line-clamp-2 text-sm font-medium text-zinc-200">
                  {cluster.title}
                </h3>
                <p className="text-[11px] text-zinc-600">
                  更新于 {formatRelativeTime(cluster.last_updated_at)}
                </p>
              </Link>
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
