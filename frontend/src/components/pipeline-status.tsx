'use client'

import { useEffect, useState } from 'react'
import { Activity, CheckCircle, XCircle, Clock } from 'lucide-react'
import { getPipelineStatus } from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'

interface PipelineStatusData {
  is_running: boolean
  current_run: {
    id: string
    started_at: string
    status: string
  } | null
  last_completed_run: {
    id: string
    completed_at: string
    articles_discovered: number
    articles_processed: number
    articles_failed: number
    duration_ms: number
  } | null
  step_stats_24h: {
    step_name: string
    status: string
    count: number
    avg_duration_ms: number
  }[]
}

export function PipelineStatus() {
  const [data, setData] = useState<PipelineStatusData | null>(null)

  useEffect(() => {
    const load = async () => {
      try {
        const result = await getPipelineStatus()
        setData(result)
      } catch (err) {
        console.error('Failed to load pipeline status:', err)
      }
    }
    load()
    const interval = setInterval(load, 30000)
    return () => clearInterval(interval)
  }, [])

  if (!data) {
    return (
      <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
        <div className="text-xs text-zinc-600">加载流水线状态...</div>
      </div>
    )
  }

  const last = data.last_completed_run
  const totalSuccess = data.step_stats_24h
    .filter((s) => s.status === 'success')
    .reduce((sum, s) => sum + s.count, 0)
  const totalFailed = data.step_stats_24h
    .filter((s) => s.status === 'failed')
    .reduce((sum, s) => sum + s.count, 0)

  return (
    <div className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3">
      <div className="mb-2 flex items-center justify-between">
        <span className="text-xs font-medium text-zinc-400">流水线</span>
        <span
          className={`inline-flex items-center gap-1 text-xs font-medium ${
            data.is_running ? 'text-green-400' : 'text-zinc-500'
          }`}
        >
          <Activity size={10} className={data.is_running ? 'animate-pulse' : ''} />
          {data.is_running ? '运行中' : '空闲'}
        </span>
      </div>

      {last && (
        <div className="mb-2 space-y-1 text-[11px]">
          <div className="flex items-center justify-between text-zinc-500">
            <span className="flex items-center gap-1">
              <Clock size={10} />
              上次运行
            </span>
            <span>{formatRelativeTime(last.completed_at)}</span>
          </div>
          <div className="flex items-center justify-between text-zinc-500">
            <span className="flex items-center gap-1">
              <CheckCircle size={10} className="text-green-500" />
              发现/处理
            </span>
            <span>
              {last.articles_discovered}/{last.articles_processed}
            </span>
          </div>
          {last.articles_failed > 0 && (
            <div className="flex items-center justify-between text-zinc-500">
              <span className="flex items-center gap-1">
                <XCircle size={10} className="text-red-400" />
                失败
              </span>
              <span className="text-red-400">{last.articles_failed}</span>
            </div>
          )}
        </div>
      )}

      <div className="flex gap-3 text-[10px]">
        <span className="text-green-500">24h成功: {totalSuccess}</span>
        {totalFailed > 0 && <span className="text-red-400">失败: {totalFailed}</span>}
      </div>
    </div>
  )
}
