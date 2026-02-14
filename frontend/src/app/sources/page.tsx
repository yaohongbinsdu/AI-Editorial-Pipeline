'use client'

import { useEffect, useState } from 'react'
import { Plus, Trash2, RefreshCw } from 'lucide-react'
import { getSources, createSource, updateSource, deleteSource } from '@/lib/api'
import type { RSSSource, RSSSourceCreate } from '@/types'
import { CATEGORY_LABELS, type CategorySlug } from '@/types'
import { formatRelativeTime } from '@/lib/utils'

const CATEGORIES = Object.entries(CATEGORY_LABELS) as [CategorySlug, string][]

export default function SourcesPage() {
  const [sources, setSources] = useState<RSSSource[]>([])
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState<RSSSourceCreate>({
    url: '',
    name: '',
    category: 'technology',
  })
  const [submitting, setSubmitting] = useState(false)

  const loadSources = async () => {
    setLoading(true)
    try {
      const data = await getSources()
      setSources(data)
    } catch (err) {
      console.error('Failed to load sources:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSources()
  }, [])

  const handleAdd = async () => {
    if (!form.url || !form.name) return
    setSubmitting(true)
    try {
      await createSource(form)
      setForm({ url: '', name: '', category: 'technology' })
      setShowAdd(false)
      await loadSources()
    } catch (err) {
      console.error('Failed to create source:', err)
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggle = async (source: RSSSource) => {
    try {
      await updateSource(source.id, { enabled: !source.enabled })
      await loadSources()
    } catch (err) {
      console.error('Failed to toggle source:', err)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除此RSS源吗？')) return
    try {
      await deleteSource(id)
      await loadSources()
    } catch (err) {
      console.error('Failed to delete source:', err)
    }
  }

  return (
    <div>
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">RSS源管理</h1>
          <p className="mt-1 text-sm text-zinc-500">
            管理新闻采集源，共 {sources.length} 个
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadSources}
            className="inline-flex items-center gap-1.5 rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-300 hover:bg-zinc-700"
          >
            <RefreshCw size={14} />
            刷新
          </button>
          <button
            onClick={() => setShowAdd(!showAdd)}
            className="inline-flex items-center gap-1.5 rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-500"
          >
            <Plus size={14} />
            添加源
          </button>
        </div>
      </div>

      {showAdd && (
        <div className="mb-6 rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
          <h3 className="mb-3 text-sm font-medium">添加新RSS源</h3>
          <div className="grid gap-3 sm:grid-cols-4">
            <input
              type="text"
              placeholder="RSS URL"
              value={form.url}
              onChange={(e) => setForm({ ...form, url: e.target.value })}
              className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 placeholder:text-zinc-600 focus:border-red-500 focus:outline-none"
            />
            <input
              type="text"
              placeholder="名称"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 placeholder:text-zinc-600 focus:border-red-500 focus:outline-none"
            />
            <select
              value={form.category}
              onChange={(e) =>
                setForm({ ...form, category: e.target.value as CategorySlug })
              }
              className="rounded-md border border-zinc-700 bg-zinc-800 px-3 py-1.5 text-sm text-zinc-200 focus:border-red-500 focus:outline-none"
            >
              {CATEGORIES.map(([slug, label]) => (
                <option key={slug} value={slug}>
                  {label}
                </option>
              ))}
            </select>
            <button
              onClick={handleAdd}
              disabled={submitting || !form.url || !form.name}
              className="rounded-md bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-500 disabled:opacity-50"
            >
              {submitting ? '添加中...' : '确认添加'}
            </button>
          </div>
        </div>
      )}

      {loading ? (
        <div className="py-12 text-center text-sm text-zinc-500">加载中...</div>
      ) : sources.length === 0 ? (
        <div className="py-12 text-center text-sm text-zinc-500">
          暂无RSS源，点击"添加源"开始
        </div>
      ) : (
        <div className="overflow-hidden rounded-lg border border-zinc-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/80">
                <th className="px-4 py-2.5 text-left font-medium text-zinc-400">名称</th>
                <th className="hidden px-4 py-2.5 text-left font-medium text-zinc-400 md:table-cell">
                  分类
                </th>
                <th className="hidden px-4 py-2.5 text-left font-medium text-zinc-400 lg:table-cell">
                  上次拉取
                </th>
                <th className="px-4 py-2.5 text-center font-medium text-zinc-400">失败</th>
                <th className="px-4 py-2.5 text-center font-medium text-zinc-400">状态</th>
                <th className="px-4 py-2.5 text-right font-medium text-zinc-400">操作</th>
              </tr>
            </thead>
            <tbody>
              {sources.map((s) => (
                <tr key={s.id} className="border-b border-zinc-800/50 hover:bg-zinc-900/30">
                  <td className="px-4 py-2.5">
                    <div className="font-medium text-zinc-200">{s.name}</div>
                    <div className="truncate text-xs text-zinc-600" style={{ maxWidth: '300px' }}>
                      {s.url}
                    </div>
                  </td>
                  <td className="hidden px-4 py-2.5 md:table-cell">
                    <span className="rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400">
                      {CATEGORY_LABELS[s.category as CategorySlug] || s.category}
                    </span>
                  </td>
                  <td className="hidden px-4 py-2.5 text-zinc-500 lg:table-cell">
                    {formatRelativeTime(s.last_fetched_at)}
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <span
                      className={
                        s.consecutive_failures > 0
                          ? 'font-medium text-red-400'
                          : 'text-zinc-600'
                      }
                    >
                      {s.consecutive_failures}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-center">
                    <button
                      onClick={() => handleToggle(s)}
                      className={`inline-block h-5 w-9 rounded-full transition-colors ${
                        s.enabled ? 'bg-green-600' : 'bg-zinc-700'
                      }`}
                    >
                      <span
                        className={`block h-4 w-4 rounded-full bg-white transition-transform ${
                          s.enabled ? 'translate-x-4' : 'translate-x-0.5'
                        }`}
                      />
                    </button>
                  </td>
                  <td className="px-4 py-2.5 text-right">
                    <button
                      onClick={() => handleDelete(s.id)}
                      className="text-zinc-600 hover:text-red-400"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
