import type { OpportunityCard } from '../api/client'
import { cn } from '../lib/utils'

const TIME_LABEL: Record<OpportunityCard['time_to_pilot'], string> = {
  '30_days': '30 days',
  '60_days': '60 days',
  '90_days': '90 days',
  longer: 'longer',
}

const LEVEL_STYLE: Record<string, string> = {
  high: 'bg-green-100 text-green-800',
  medium: 'bg-amber-100 text-amber-800',
  low: 'bg-slate-100 text-slate-600',
}

function Badge({ label, level }: { label: string; level: string }) {
  return (
    <span
      className={cn(
        'rounded-full px-2 py-0.5 text-xs font-medium capitalize',
        LEVEL_STYLE[level] ?? 'bg-slate-100 text-slate-600',
      )}
    >
      {label}: {level}
    </span>
  )
}

export default function OpportunityCardView({
  card,
  onPlan,
}: {
  card: OpportunityCard
  onPlan?: (card: OpportunityCard) => void
}) {
  return (
    <article className="flex flex-col rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <header className="mb-2">
        <h3 className="font-semibold text-slate-900">{card.name}</h3>
        <span className="text-xs text-slate-400">{card.category}</span>
      </header>
      <p className="text-sm text-slate-700">{card.executive_summary}</p>
      <p className="mt-2 text-sm text-slate-600">
        <span className="font-medium text-slate-700">Why now:</span> {card.why_now}
      </p>
      <div className="mt-3 flex flex-wrap gap-1.5">
        <Badge label="Value" level={card.business_value} />
        <Badge label="Feasibility" level={card.pilot_feasibility} />
        <Badge label="Risk" level={card.risk_level} />
        <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
          {TIME_LABEL[card.time_to_pilot]}
        </span>
      </div>
      <p className="mt-3 text-sm text-slate-600">
        <span className="font-medium text-slate-700">First step:</span>{' '}
        {card.recommended_first_step}
      </p>
      {onPlan && (
        <button
          type="button"
          onClick={() => onPlan(card)}
          className="mt-3 self-start rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Plan this pilot →
        </button>
      )}
    </article>
  )
}
