'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { LayoutDashboard, Newspaper, Layers, FolderTree, Rss, Workflow } from 'lucide-react'
import { cn } from '@/lib/utils'

const NAV_ITEMS = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/articles', label: '文章', icon: Newspaper },
  { href: '/clusters', label: '事件聚类', icon: Layers },
  { href: '/categories', label: '行业分类', icon: FolderTree },
  { href: '/sources', label: 'RSS 源', icon: Rss },
  { href: '/pipeline', label: '流水线', icon: Workflow },
]

export function SidebarNav() {
  const pathname = usePathname()

  return (
    <nav className="space-y-1 p-3">
      {NAV_ITEMS.map((item) => {
        const isActive =
          item.href === '/'
            ? pathname === '/'
            : pathname.startsWith(item.href)
        const Icon = item.icon
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
              isActive
                ? 'bg-zinc-800 font-medium text-zinc-100'
                : 'text-zinc-400 hover:bg-zinc-800 hover:text-zinc-100',
            )}
          >
            <Icon size={16} />
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}
