import Link from 'next/link'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

interface TrendingCluster {
  id: string
  title: string
  category: string
  article_count: number
  last_updated_at: string | null
}

interface TrendingBarProps {
  clusters: TrendingCluster[]
}

export function TrendingBar({ clusters }: TrendingBarProps) {
  if (clusters.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 text-center text-sm text-zinc-500">
        暂无热门事件
      </div>
    )
  }

  return (
    <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-track-zinc-900 scrollbar-thumb-zinc-700">
      {clusters.map((cluster) => (
        <Link
          key={cluster.id}
          href={`/clusters/${cluster.id}`}
          className="group flex-none rounded-lg border border-zinc-800 bg-zinc-900/50 p-3 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
          style={{ minWidth: '220px', maxWidth: '280px' }}
        >
          <div className="mb-1 flex items-center gap-2">
            <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
              {CATEGORY_LABELS[cluster.category as CategorySlug] || cluster.category}
            </span>
            <span className="rounded-full bg-red-500/10 px-1.5 py-0.5 text-[10px] font-semibold text-red-400">
              {cluster.article_count}篇
            </span>
          </div>
          <h3 className="line-clamp-2 text-xs font-medium text-zinc-200 group-hover:text-white">
            {cluster.title}
          </h3>
          <div className="mt-1 text-[10px] text-zinc-600">
            {formatRelativeTime(cluster.last_updated_at)}
          </div>
        </Link>
      ))}
    </div>
  )
}
