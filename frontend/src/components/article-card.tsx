import Link from 'next/link'
import type { ArticleBrief } from '@/types'
import { CATEGORY_LABELS } from '@/types'
import { cn, formatRelativeTime, scoreColor, truncate, voteColor } from '@/lib/utils'

interface ArticleCardProps {
  article: ArticleBrief
}

export function ArticleCard({ article }: ArticleCardProps) {
  const title = article.rewritten_title || article.final_title
  const score = article.composite_score

  return (
    <Link
      href={`/articles/${article.id}`}
      className="group block rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
    >
      <div className="flex gap-4">
        {article.final_image_url && (
          <div className="hidden h-20 w-28 shrink-0 overflow-hidden rounded-md sm:block">
            <img
              src={article.final_image_url}
              alt=""
              className="h-full w-full object-cover"
              loading="lazy"
            />
          </div>
        )}

        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-2">
            {article.editorial_vote && (
              <span
                className={cn(
                  'inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase',
                  voteColor(article.editorial_vote),
                )}
              >
                {article.editorial_vote === 'must_read'
                  ? '必读'
                  : article.editorial_vote === 'interesting'
                    ? '有趣'
                    : '略过'}
              </span>
            )}
            {article.category && (
              <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-[10px] font-medium text-zinc-400">
                {CATEGORY_LABELS[article.category] || article.category}
              </span>
            )}
            {score !== null && score !== undefined && (
              <span className={cn('text-xs font-bold', scoreColor(score))}>
                {score.toFixed(1)}
              </span>
            )}
          </div>

          <h3 className="mb-1 line-clamp-2 text-sm font-medium leading-snug text-zinc-200 group-hover:text-white">
            {title}
          </h3>

          {article.human_tldr && (
            <p className="mb-2 line-clamp-2 text-xs text-zinc-500">
              {truncate(article.human_tldr, 120)}
            </p>
          )}

          <div className="flex items-center gap-2 text-[11px] text-zinc-600">
            <span>{article.source_name}</span>
            <span>·</span>
            <span>{formatRelativeTime(article.published_at)}</span>
            {article.tags.length > 0 && (
              <>
                <span>·</span>
                <div className="flex gap-1">
                  {article.tags.slice(0, 3).map((tag) => (
                    <span
                      key={tag}
                      className="rounded bg-zinc-800 px-1.5 py-0.5 text-[10px] text-zinc-500"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </Link>
  )
}
