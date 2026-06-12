import { cn } from '../lib/utils'

// Circular readiness gauge. The ring fills to `score` (0–100) and is coloured by
// band so an executive reads "where are we" at a glance.
function band(score: number): { ring: string; text: string } {
  if (score >= 80) return { ring: 'stroke-green-500', text: 'text-green-700' }
  if (score >= 50) return { ring: 'stroke-amber-500', text: 'text-amber-700' }
  return { ring: 'stroke-red-500', text: 'text-red-700' }
}

export default function ReadinessGauge({
  score,
  size = 96,
}: {
  score: number
  size?: number
}) {
  const stroke = 8
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.max(0, Math.min(100, score))
  const offset = circumference * (1 - clamped / 100)
  const colors = band(clamped)

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          className="stroke-slate-100"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className={cn('transition-[stroke-dashoffset]', colors.ring)}
        />
      </svg>
      <span className={cn('absolute text-sm font-semibold tabular-nums', colors.text)}>
        {clamped}/100
      </span>
    </div>
  )
}
