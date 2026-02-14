'use client'

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import type { GravityScoreDetail } from '@/types'

interface ScoreRadarProps {
  gravity: GravityScoreDetail
}

const DIMENSIONS = [
  { key: 'industry_impact', label: '行业影响', group: 'impact' },
  { key: 'consumer_impact', label: '消费者影响', group: 'impact' },
  { key: 'actionability', label: '可操作性', group: 'impact' },
  { key: 'risk_urgency', label: '风险紧迫', group: 'impact' },
  { key: 'novelty', label: '新颖度', group: 'intellectual' },
  { key: 'technical_depth', label: '技术深度', group: 'intellectual' },
  { key: 'second_order_potential', label: '二阶效应', group: 'intellectual' },
  { key: 'builder_relevance', label: '建设者相关', group: 'intellectual' },
  { key: 'entertainment_value', label: '娱乐价值', group: 'overlay' },
  { key: 'signal_to_noise', label: '信噪比', group: 'overlay' },
  { key: 'viral_potential', label: '传播潜力', group: 'overlay' },
  { key: 'early_trend_signal', label: '早期趋势', group: 'overlay' },
  { key: 'concreteness', label: '具体程度', group: 'quality' },
  { key: 'pr_fluff', label: 'PR软文', group: 'quality' },
  { key: 'speculation', label: '臆测', group: 'quality' },
  { key: 'paid_sponsorship', label: '付费赞助', group: 'quality' },
]

const GROUP_COLORS: Record<string, string> = {
  impact: '#ef4444',
  intellectual: '#3b82f6',
  overlay: '#22c55e',
  quality: '#f97316',
}

export function ScoreRadar({ gravity }: ScoreRadarProps) {
  const data = DIMENSIONS.map((dim) => ({
    dimension: dim.label,
    value: (gravity as unknown as Record<string, number>)[dim.key] ?? 0,
    fullMark: 10,
    group: dim.group,
  }))

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={data}>
          <PolarGrid stroke="#333" />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: '#71717a', fontSize: 10 }}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 10]}
            tick={{ fill: '#52525b', fontSize: 9 }}
          />
          <Radar
            name="评分"
            dataKey="value"
            stroke="#ef4444"
            fill="#ef4444"
            fillOpacity={0.15}
            strokeWidth={1.5}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#18181b',
              border: '1px solid #3f3f46',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            labelStyle={{ color: '#a1a1aa' }}
          />
        </RadarChart>
      </ResponsiveContainer>

      <div className="mt-2 flex justify-center gap-4 text-[10px]">
        {Object.entries(GROUP_COLORS).map(([group, color]) => (
          <span key={group} className="flex items-center gap-1">
            <span
              className="inline-block h-2 w-2 rounded-full"
              style={{ backgroundColor: color }}
            />
            {group === 'impact'
              ? '影响力'
              : group === 'intellectual'
                ? '智识引力'
                : group === 'overlay'
                  ? '叠加信号'
                  : '质量标记'}
          </span>
        ))}
      </div>
    </div>
  )
}
