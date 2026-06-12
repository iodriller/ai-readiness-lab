import { useEffect, useState } from 'react'
import { getPilot } from '../api/client'
import type { BriefResponse, OpportunityCard, PilotPlan, SourceEvent } from '../api/client'
import { Sources } from './ai/Sources'
import type { SourceLike } from './ai/Sources'
import OpportunityCardView from './OpportunityCardView'
import PilotDrillDown from './PilotDrillDown'
import QAPanel from './QAPanel'
import ReadinessGauge from './ReadinessGauge'
import ReportPreview from './ReportPreview'

const NARRATIVE: { title: string; key: keyof BriefResponse }[] = [
  { title: 'What matters', key: 'what_matters' },
  { title: 'Competitive pressure', key: 'competitive_pressure' },
  { title: 'The opening', key: 'the_opening' },
  { title: 'Recommended next move', key: 'recommended_next_move' },
]

export default function Brief({
  brief,
  projectId,
  sources = [],
}: {
  brief: BriefResponse
  projectId: string
  sources?: SourceEvent[]
}) {
  const [selected, setSelected] = useState<OpportunityCard | null>(null)
  const [pilot, setPilot] = useState<PilotPlan | null>(null)

  useEffect(() => {
    getPilot(projectId)
      .then(setPilot)
      .catch(() => setPilot(null))
  }, [projectId])

  // Prefer the evidence persisted on the brief (survives reload); fall back to the
  // sources collected live during this session.
  const evidence: SourceLike[] = brief.sources?.length ? brief.sources : sources

  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <header className="flex items-center gap-3">
        <h1 className="text-2xl font-semibold text-slate-900">
          AI Readiness Brief: {brief.company_name}
        </h1>
        {brief.is_sample && (
          <span
            className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-medium text-amber-800"
            title="Illustrative content until live research is connected"
          >
            Sample
          </span>
        )}
      </header>

      {pilot && (
        <div className="mt-5 flex items-center gap-4 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
          <ReadinessGauge score={pilot.scorecard.overall_score} size={72} />
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Pilot readiness
            </p>
            <p className="font-semibold text-slate-900">{pilot.profile.opportunity_name}</p>
            <p className="text-sm capitalize text-slate-500">
              {pilot.scorecard.recommendation.replace(/_/g, ' ')}
            </p>
          </div>
        </div>
      )}

      <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        {NARRATIVE.map(({ title, key }) => (
          <div key={title}>
            <h2 className="text-sm font-semibold text-slate-500">{title}</h2>
            <p className="mt-1 text-slate-700">{String(brief[key])}</p>
          </div>
        ))}
      </section>

      <section className="mt-8">
        <h2 className="mb-3 text-lg font-semibold text-slate-800">Recommended opportunities</h2>
        <div className="grid gap-4 sm:grid-cols-2">
          {brief.opportunities.map((card) => (
            <OpportunityCardView key={card.name} card={card} onPlan={setSelected} />
          ))}
        </div>
        {selected && (
          <PilotDrillDown
            projectId={projectId}
            card={selected}
            onPlanned={setPilot}
            onClose={() => setSelected(null)}
          />
        )}
      </section>

      {evidence.length > 0 && (
        <section className="mt-8">
          <h2 className="mb-3 text-lg font-semibold text-slate-800">Evidence</h2>
          <Sources sources={evidence} title={`${evidence.length} public sources reviewed`} />
        </section>
      )}

      <QAPanel projectId={projectId} />

      <ReportPreview projectId={projectId} />
    </div>
  )
}
