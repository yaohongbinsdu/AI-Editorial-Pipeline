import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatRelativeTime(dateStr: string | null): string {
  if (!dateStr) return '未知'
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffMin = Math.floor(diffMs / 60000)
  const diffHour = Math.floor(diffMs / 3600000)
  const diffDay = Math.floor(diffMs / 86400000)

  if (diffMin < 1) return '刚刚'
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  if (diffDay < 7) return `${diffDay}天前`
  return date.toLocaleDateString('zh-CN')
}

export function truncate(str: string, maxLen: number): string {
  if (str.length <= maxLen) return str
  return str.slice(0, maxLen - 1) + '…'
}

export function scoreColor(score: number | null): string {
  if (score === null) return 'text-muted-foreground'
  if (score >= 8) return 'text-red-500'
  if (score >= 6) return 'text-orange-500'
  if (score >= 4) return 'text-yellow-500'
  return 'text-muted-foreground'
}

export function voteColor(vote: string | null): string {
  switch (vote) {
    case 'must_read':
      return 'bg-red-500/10 text-red-500 border-red-500/20'
    case 'interesting':
      return 'bg-blue-500/10 text-blue-500 border-blue-500/20'
    case 'skip':
      return 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
    default:
      return 'bg-zinc-500/10 text-zinc-400 border-zinc-500/20'
  }
}
