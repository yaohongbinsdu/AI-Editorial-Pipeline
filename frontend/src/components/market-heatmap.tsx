'use client'

import Link from 'next/link'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'

interface CategoryData {
  slug: string
  article_count: number
}

interface MarketHeatmapProps {
  categories: CategoryData[]
}

const CATEGORY_COLORS: Record<string, string> = {
  finance: 'from-red-500/20 to-red-500/5',
  technology: 'from-blue-500/20 to-blue-500/5',
  commercial_space: 'from-purple-500/20 to-purple-500/5',
  new_energy: 'from-green-500/20 to-green-500/5',
  healthcare: 'from-pink-500/20 to-pink-500/5',
  agriculture: 'from-lime-500/20 to-lime-500/5',
  consumer: 'from-orange-500/20 to-orange-500/5',
  real_estate: 'from-amber-500/20 to-amber-500/5',
  manufacturing: 'from-cyan-500/20 to-cyan-500/5',
  crypto: 'from-yellow-500/20 to-yellow-500/5',
  macro_economy: 'from-indigo-500/20 to-indigo-500/5',
  regulation: 'from-slate-500/20 to-slate-500/5',
  other: 'from-zinc-500/20 to-zinc-500/5',
}

const CATEGORY_BORDER: Record<string, string> = {
  finance: 'border-red-500/30',
  technology: 'border-blue-500/30',
  commercial_space: 'border-purple-500/30',
  new_energy: 'border-green-500/30',
  healthcare: 'border-pink-500/30',
  agriculture: 'border-lime-500/30',
  consumer: 'border-orange-500/30',
  real_estate: 'border-amber-500/30',
  manufacturing: 'border-cyan-500/30',
  crypto: 'border-yellow-500/30',
  macro_economy: 'border-indigo-500/30',
  regulation: 'border-slate-500/30',
  other: 'border-zinc-500/30',
}

export function MarketHeatmap({ categories }: MarketHeatmapProps) {
  const maxCount = Math.max(...categories.map((c) => c.article_count), 1)

  if (categories.length === 0) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-6 text-center text-sm text-zinc-500">
        暂无行业数据
      </div>
    )
  }

  return (
    <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 lg:grid-cols-6">
      {categories.map((cat) => {
        const intensity = Math.max(0.3, cat.article_count / maxCount)
        const gradient = CATEGORY_COLORS[cat.slug] || CATEGORY_COLORS.other
        const border = CATEGORY_BORDER[cat.slug] || CATEGORY_BORDER.other

        return (
          <Link
            key={cat.slug}
            href={`/categories/${cat.slug}`}
            className={`group relative overflow-hidden rounded-lg border bg-gradient-to-br p-3 transition-all hover:scale-[1.02] hover:shadow-lg ${border} ${gradient}`}
            style={{ opacity: 0.5 + intensity * 0.5 }}
          >
            <div className="text-xs font-semibold text-zinc-200">
              {CATEGORY_LABELS[cat.slug as CategorySlug] || cat.slug}
            </div>
            <div className="mt-1 text-lg font-bold text-zinc-100">
              {cat.article_count}
            </div>
            <div className="text-[10px] text-zinc-500">篇文章</div>
          </Link>
        )
      })}
    </div>
  )
}
