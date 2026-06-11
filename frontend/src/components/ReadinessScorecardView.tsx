import type { ReadinessScorecard } from '../api/client'
import { cn } from '../lib/utils'

const REC_STYLE: Record<string, string> = {
  proceed: 'bg-green-100 text-green-800',
  limited_pilot: 'bg-blue-100 text-blue-800',
  needs_discovery: 'bg-amber-100 text-amber-800',
  defer: 'bg-orange-100 text-orange-800',
  not_recommended: 'bg-red-100 text-red-800',
}

function barColor(value: number): string {
  if (value >= 80) return 'bg-green-500'
  if (value >= 50) return 'bg-amber-500'
  return 'bg-red-500'
}

export default function ReadinessScorecardView({ scorecard }: { scorecard: ReadinessScorecard }) {
  const dims = scorecard.dimensions as unknown as Record<string, number>
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
            Readiness scorecard
          </p>
          <p className="text-3xl font-semibold text-slate-900">{scorecard.overall_score}/100</p>
        </div>
        <span
          className={cn(
            'rounded-full px-3 py-1 text-sm font-medium',
            REC_STYLE[scorecard.recommendation] ?? 'bg-slate-100 text-slate-700',
          )}
        >
          {scorecard.recommendation.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="mt-4 space-y-2">
        {Object.entries(dims).map(([dim, value]) => (
          <div key={dim} className="flex items-center gap-3 text-sm">
            <span className="w-44 shrink-0 capitalize text-slate-600">{dim.replace(/_/g, ' ')}</span>
            <div className="h-2 flex-1 rounded-full bg-slate-100">
              <div
                className={cn('h-2 rounded-full', barColor(value))}
                style={{ width: `${value}%` }}
                data-testid={`bar-${dim}`}
              />
            </div>
            <span className="w-10 text-right tabular-nums text-slate-500">{value}</span>
          </div>
        ))}
      </div>

      <ScoreList title="Strengths" items={scorecard.strengths ?? []} tone="text-green-700" />
      <ScoreList title="Blockers" items={scorecard.blockers ?? []} tone="text-red-700" />
      <ScoreList title="Next actions" items={scorecard.next_actions ?? []} tone="text-slate-700" />
    </div>
  )
}

function ScoreList({ title, items, tone }: { title: string; items: string[]; tone: string }) {
  if (!items.length) return null
  return (
    <div className="mt-3">
      <p className="text-xs font-semibold text-slate-500">{title}</p>
      <ul className="mt-1 space-y-1">
        {items.map((item, i) => (
          <li key={i} className={cn('flex gap-2 text-sm', tone)}>
            <span className="text-slate-400">•</span>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
