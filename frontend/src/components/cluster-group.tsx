import Link from 'next/link'
import type { ClusterBrief } from '@/types'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

interface ClusterGroupProps {
  cluster: ClusterBrief
}

export function ClusterGroup({ cluster }: ClusterGroupProps) {
  return (
    <Link
      href={`/clusters/${cluster.id}`}
      className="group block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
    >
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
            {CATEGORY_LABELS[cluster.category as CategorySlug] || cluster.category}
          </span>
          <span className="rounded-full bg-red-500/10 px-2 py-0.5 text-[10px] font-semibold text-red-400">
            {cluster.article_count} 篇
          </span>
        </div>
        <span className="text-[11px] text-zinc-600">
          {formatRelativeTime(cluster.last_updated_at)}
        </span>
      </div>

      <h3 className="mb-2 line-clamp-2 text-sm font-medium text-zinc-200 group-hover:text-white">
        {cluster.title}
      </h3>

      {cluster.top_article && (
        <div className="rounded-md bg-zinc-800/50 p-2">
          <p className="line-clamp-1 text-xs text-zinc-400">
            {cluster.top_article.rewritten_title || cluster.top_article.final_title}
          </p>
          {cluster.top_article.human_tldr && (
            <p className="mt-0.5 line-clamp-1 text-[11px] text-zinc-600">
              {cluster.top_article.human_tldr}
            </p>
          )}
        </div>
      )}
    </Link>
  )
}
