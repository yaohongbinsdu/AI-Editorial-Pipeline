'use client'

import { useEffect, useState } from 'react'
import { Play, RefreshCw } from 'lucide-react'
import {
  getPipelineStatus,
  getPipelineRuns,
  triggerPipeline,
} from '@/lib/api'
import { formatRelativeTime } from '@/lib/utils'

interface PipelineRun {
  id: string
  started_at: string
  completed_at: string | null
  status: string
  articles_discovered: number
  articles_processed: number
  articles_failed: number
  duration_seconds: number | null
}

interface StepStat {
  step_name: string
  status: string
  count: number
  avg_duration_ms: number
}

export default function PipelinePage() {
  const [isRunning, setIsRunning] = useState(false)
  const [runs, setRuns] = useState<PipelineRun[]>([])
  const [stepStats, setStepStats] = useState<StepStat[]>([])
  const [loading, setLoading] = useState(true)
  const [triggering, setTriggering] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const [status, runList] = await Promise.all([
        getPipelineStatus(),
        getPipelineRuns(24),
      ])
      setIsRunning(status.is_running)
      setStepStats(status.step_stats_24h)
      setRuns(runList)
    } catch (err) {
      console.error('Failed to load pipeline data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleTrigger = async () => {
    setTriggering(true)
    try {
      await triggerPipeline()
      setTimeout(loadData, 2000)
    } catch (err) {
      console.error('Failed to trigger pipeline:', err)
    } finally {
      setTriggering(false)
    }
  }

  const stepNames = [
    'rss_fetch',
    'content_scrape',
    'summarize',
    'vectorize',
    'cluster',
    'expansion_check',
    'gravity_score',
  ]
  const stepLabels: Record<string, string> = {
    rss_fetch: 'RSS拉取',
    content_scrape: '内容抓取',
    summarize: 'AI摘要',
    vectorize: '向量化',
    cluster: '聚类',
    expansion_check: '扩展检查',
    gravity_score: 'Gravity评分',
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">流水线监控</h1>
          <p className="mt-1 text-sm text-zinc-500">
            {isRunning ? (
              <span className="text-green-400">运行中...</span>
            ) : (
              '空闲'
            )}
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadData}
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700"
          >
            <RefreshCw size={14} />
            刷新
          </button>
          <button
            onClick={handleTrigger}
            disabled={triggering || isRunning}
            className="inline-flex items-center gap-1.5 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-500 disabled:opacity-50"
          >
            <Play size={14} />
            {triggering ? '触发中...' : '手动触发'}
          </button>
        </div>
      </div>

      {/* Step Stats */}
      <div className="mb-6">
        <h2 className="mb-3 text-sm font-semibold text-zinc-300">24小时步骤统计</h2>
        <div className="grid gap-2 sm:grid-cols-4 lg:grid-cols-7">
          {stepNames.map((step) => {
            const success = stepStats.find(
              (s) => s.step_name === step && s.status === 'success',
            )
            const failed = stepStats.find(
              (s) => s.step_name === step && s.status === 'failed',
            )
            return (
              <div
                key={step}
                className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-3"
              >
                <div className="mb-1 text-[10px] font-medium text-zinc-500">
                  {stepLabels[step] || step}
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-lg font-bold text-green-400">
                    {success?.count || 0}
                  </span>
                  {(failed?.count || 0) > 0 && (
                    <span className="text-xs text-red-400">
                      {failed?.count} 失败
                    </span>
                  )}
                </div>
                <div className="text-[10px] text-zinc-600">
                  avg {((success?.avg_duration_ms || 0) / 1000).toFixed(1)}s
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Run History */}
      <div>
        <h2 className="mb-3 text-sm font-semibold text-zinc-300">执行记录</h2>
        {loading ? (
          <div className="py-6 text-center text-sm text-zinc-500">加载中...</div>
        ) : runs.length === 0 ? (
          <div className="py-6 text-center text-sm text-zinc-500">暂无执行记录</div>
        ) : (
          <div className="overflow-hidden rounded-lg border border-zinc-800">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-800 bg-zinc-900/80 text-zinc-400">
                  <th className="px-3 py-2 text-left font-medium">时间</th>
                  <th className="px-3 py-2 text-center font-medium">状态</th>
                  <th className="px-3 py-2 text-center font-medium">发现</th>
                  <th className="px-3 py-2 text-center font-medium">处理</th>
                  <th className="px-3 py-2 text-center font-medium">失败</th>
                  <th className="px-3 py-2 text-right font-medium">耗时</th>
                </tr>
              </thead>
              <tbody>
                {runs.map((run) => (
                  <tr
                    key={run.id}
                    className="border-b border-zinc-800/50 hover:bg-zinc-900/30"
                  >
                    <td className="px-3 py-2 text-zinc-400">
                      {formatRelativeTime(run.started_at)}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span
                        className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                          run.status === 'completed'
                            ? 'bg-green-500/10 text-green-400'
                            : run.status === 'running'
                              ? 'bg-blue-500/10 text-blue-400'
                              : 'bg-red-500/10 text-red-400'
                        }`}
                      >
                        {run.status}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-center text-zinc-300">
                      {run.articles_discovered}
                    </td>
                    <td className="px-3 py-2 text-center text-zinc-300">
                      {run.articles_processed}
                    </td>
                    <td className="px-3 py-2 text-center">
                      <span className={run.articles_failed > 0 ? 'text-red-400' : 'text-zinc-600'}>
                        {run.articles_failed}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-right text-zinc-500">
                      {run.duration_seconds ? `${run.duration_seconds.toFixed(1)}s` : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
