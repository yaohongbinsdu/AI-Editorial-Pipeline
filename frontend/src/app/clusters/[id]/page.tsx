'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Zap } from 'lucide-react'
import { getCluster } from '@/lib/api'
import type { ClusterDetail } from '@/types'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { ArticleCard } from '@/components/article-card'
import { formatRelativeTime } from '@/lib/utils'

export default function ClusterDetailPage() {
  const params = useParams()
  const [cluster, setCluster] = useState<ClusterDetail | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!params.id) return
    const load = async () => {
      try {
        const data = await getCluster(params.id as string)
        setCluster(data)
      } catch (err) {
        console.error('Failed to load cluster:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [params.id])

  if (loading) {
    return <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
  }

  if (!cluster) {
    return <div className="py-12 text-center text-sm text-zinc-500">聚类未找到</div>
  }

  return (
    <div className="mx-auto max-w-4xl">
      <Link
        href="/"
        className="mb-4 inline-flex items-center gap-1 text-sm text-zinc-500 hover:text-zinc-300"
      >
        <ArrowLeft size={14} />
        返回
      </Link>

      <div className="mb-6">
        <div className="mb-2 flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-zinc-800 px-2.5 py-0.5 text-xs font-medium text-zinc-300">
            {CATEGORY_LABELS[cluster.category as CategorySlug] || cluster.category}
          </span>
          <span className="rounded-full bg-red-500/10 px-2.5 py-0.5 text-xs font-semibold text-red-400">
            {cluster.article_count} 篇文章
          </span>
          {cluster.expansion_triggered && (
            <span className="inline-flex items-center gap-1 rounded-full bg-yellow-500/10 px-2.5 py-0.5 text-xs font-medium text-yellow-400">
              <Zap size={10} />
              已扩展搜索
            </span>
          )}
        </div>

        <h1 className="mb-1 text-2xl font-bold text-zinc-100">{cluster.title}</h1>
        <p className="text-sm text-zinc-500">
          首次发现: {formatRelativeTime(cluster.first_seen_at)} · 最后更新:{' '}
          {formatRelativeTime(cluster.last_updated_at)}
        </p>
      </div>

      <div className="space-y-3">
        {cluster.articles.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>

      {cluster.articles.length === 0 && (
        <div className="py-12 text-center text-sm text-zinc-500">该聚类暂无文章</div>
      )}
    </div>
  )
}
