'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  Banknote,
  Cpu,
  Rocket,
  Zap,
  Heart,
  Wheat,
  ShoppingCart,
  Building2,
  Factory,
  Bitcoin,
  TrendingUp,
  Scale,
  LayoutDashboard,
  Rss,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import type { CategorySlug } from '@/types'

interface CategoryNavItem {
  slug: CategorySlug | string
  label: string
  icon: React.ReactNode
  href: string
}

const NAV_ITEMS: CategoryNavItem[] = [
  { slug: 'home', label: '市场总览', icon: <LayoutDashboard size={18} />, href: '/' },
  { slug: 'finance', label: '金融', icon: <Banknote size={18} />, href: '/categories/finance' },
  {
    slug: 'technology',
    label: '科技',
    icon: <Cpu size={18} />,
    href: '/categories/technology',
  },
  {
    slug: 'commercial_space',
    label: '商业航天',
    icon: <Rocket size={18} />,
    href: '/categories/commercial_space',
  },
  {
    slug: 'new_energy',
    label: '新能源',
    icon: <Zap size={18} />,
    href: '/categories/new_energy',
  },
  {
    slug: 'healthcare',
    label: '医疗健康',
    icon: <Heart size={18} />,
    href: '/categories/healthcare',
  },
  {
    slug: 'agriculture',
    label: '农业',
    icon: <Wheat size={18} />,
    href: '/categories/agriculture',
  },
  {
    slug: 'consumer',
    label: '消费',
    icon: <ShoppingCart size={18} />,
    href: '/categories/consumer',
  },
  {
    slug: 'real_estate',
    label: '房地产',
    icon: <Building2 size={18} />,
    href: '/categories/real_estate',
  },
  {
    slug: 'manufacturing',
    label: '制造业',
    icon: <Factory size={18} />,
    href: '/categories/manufacturing',
  },
  { slug: 'crypto', label: '加密货币', icon: <Bitcoin size={18} />, href: '/categories/crypto' },
  {
    slug: 'macro_economy',
    label: '宏观经济',
    icon: <TrendingUp size={18} />,
    href: '/categories/macro_economy',
  },
  {
    slug: 'regulation',
    label: '监管政策',
    icon: <Scale size={18} />,
    href: '/categories/regulation',
  },
]

const SYSTEM_ITEMS: CategoryNavItem[] = [
  { slug: 'sources', label: 'RSS源管理', icon: <Rss size={18} />, href: '/sources' },
  { slug: 'pipeline', label: '流水线监控', icon: <Activity size={18} />, href: '/pipeline' },
]

export function CategoryNav() {
  const pathname = usePathname()

  return (
    <div className="flex flex-col gap-1">
      <div className="mb-1 px-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
        行业板块
      </div>
      {NAV_ITEMS.map((item) => {
        const isActive = pathname === item.href
        return (
          <Link
            key={item.slug}
            href={item.href}
            className={cn(
              'flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm transition-colors',
              isActive
                ? 'bg-zinc-800 text-zinc-100 font-medium'
                : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200',
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        )
      })}

      <div className="mb-1 mt-4 px-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
        系统
      </div>
      {SYSTEM_ITEMS.map((item) => {
        const isActive = pathname === item.href
        return (
          <Link
            key={item.slug}
            href={item.href}
            className={cn(
              'flex items-center gap-2.5 rounded-md px-2.5 py-1.5 text-sm transition-colors',
              isActive
                ? 'bg-zinc-800 text-zinc-100 font-medium'
                : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200',
            )}
          >
            {item.icon}
            {item.label}
          </Link>
        )
      })}
    </div>
  )
}
