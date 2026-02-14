'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { getCategories } from '@/lib/api'
import type { CategoryStats, CategorySlug } from '@/types'
import { CATEGORY_LABELS } from '@/types'

export default function CategoriesPage() {
  const [categories, setCategories] = useState<CategoryStats[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getCategories()
        setCategories(data)
      } catch (err) {
        console.error('Failed to load categories:', err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const allSlugs: CategorySlug[] = [
    'finance', 'technology', 'commercial_space', 'new_energy',
    'healthcare', 'agriculture', 'consumer', 'real_estate',
    'manufacturing', 'crypto', 'macro_economy', 'regulation',
  ]

  const catMap = new Map(categories.map((c) => [c.slug, c]))

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">行业分类</h1>
        <p className="mt-1 text-sm text-zinc-500">12个行业板块</p>
      </div>

      {loading ? (
        <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {allSlugs.map((slug) => {
            const stats = catMap.get(slug)
            const articleCount = stats?.article_count ?? 0
            const clusterCount = stats?.cluster_count ?? 0
            return (
              <Link
                key={slug}
                href={`/categories/${slug}`}
                className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4 transition-colors hover:border-zinc-700 hover:bg-zinc-900"
              >
                <h3 className="mb-2 text-base font-semibold text-zinc-200">
                  {CATEGORY_LABELS[slug]}
                </h3>
                <div className="flex gap-4 text-xs text-zinc-500">
                  <span>
                    <span className="text-lg font-bold text-zinc-300">{articleCount}</span> 篇文章
                  </span>
                  <span>
                    <span className="text-lg font-bold text-zinc-300">{clusterCount}</span> 个聚类
                  </span>
                </div>
              </Link>
            )
          })}
        </div>
      )}
    </div>
  )
}
