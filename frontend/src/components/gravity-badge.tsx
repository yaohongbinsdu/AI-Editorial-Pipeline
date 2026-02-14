import { Check, X } from 'lucide-react'
import { cn, scoreColor, voteColor } from '@/lib/utils'

interface GravityBadgeProps {
  compositeScore: number
  editorialVote: string | null
  noveltyGate: boolean | null
  viralPotential?: number
}

export function GravityBadge({
  compositeScore,
  editorialVote,
  noveltyGate,
  viralPotential,
}: GravityBadgeProps) {
  const bubbleSize = viralPotential
    ? Math.max(24, Math.min(48, 24 + viralPotential * 2.4))
    : 32

  return (
    <div className="inline-flex items-center gap-2">
      {editorialVote && (
        <span
          className={cn(
            'rounded-full border px-2.5 py-0.5 text-xs font-bold uppercase tracking-wider',
            voteColor(editorialVote),
            editorialVote === 'must_read' && 'animate-pulse',
          )}
        >
          {editorialVote === 'must_read'
            ? '必读'
            : editorialVote === 'interesting'
              ? '有趣'
              : '略过'}
        </span>
      )}

      <div
        className={cn(
          'flex items-center justify-center rounded-full font-bold',
          scoreColor(compositeScore),
        )}
        style={{
          width: `${bubbleSize}px`,
          height: `${bubbleSize}px`,
          fontSize: bubbleSize > 36 ? '14px' : '12px',
          '--viral-size': `${bubbleSize}px`,
        } as React.CSSProperties}
      >
        {compositeScore.toFixed(1)}
      </div>

      {noveltyGate !== null && (
        <span
          className={cn(
            'inline-flex items-center gap-0.5 text-xs font-medium',
            noveltyGate ? 'text-green-400' : 'text-red-400',
          )}
        >
          {noveltyGate ? <Check size={12} /> : <X size={12} />}
          {noveltyGate ? 'New' : 'Old'}
        </span>
      )}
    </div>
  )
}
