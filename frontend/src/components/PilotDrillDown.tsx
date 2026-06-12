import { useEffect, useState } from 'react'
import { getPilotQuestions, submitPilot } from '../api/client'
import type { OpportunityCard, PilotPlan, PilotQuestion } from '../api/client'
import ReadinessScorecardView from './ReadinessScorecardView'

// Guided pilot drill-down (spec §11): the 7 plain-English questions, then a
// readiness scorecard and the technical-leader checklist.
export default function PilotDrillDown({
  projectId,
  card,
  onClose,
  onPlanned,
}: {
  projectId: string
  card: OpportunityCard
  onClose: () => void
  onPlanned?: (plan: PilotPlan) => void
}) {
  const [questions, setQuestions] = useState<PilotQuestion[]>([])
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [plan, setPlan] = useState<PilotPlan | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    getPilotQuestions(projectId, card.name)
      .then((r) => setQuestions(r.questions))
      .catch(() => setError('Could not load the pilot questions.'))
  }, [projectId, card.name])

  async function handleSubmit() {
    setBusy(true)
    setError(null)
    try {
      const result = await submitPilot(projectId, card.name, answers)
      setPlan(result)
      onPlanned?.(result)
    } catch {
      setError('Could not build the pilot plan.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="mt-6 rounded-xl border border-blue-200 bg-blue-50/40 p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-blue-500">Plan a pilot</p>
          <h3 className="text-lg font-semibold text-slate-900">{card.name}</h3>
        </div>
        <button type="button" onClick={onClose} className="text-sm text-slate-500 hover:underline">
          Close
        </button>
      </div>

      {!plan ? (
        <>
          <div className="mt-4 space-y-4">
            {questions.map((q) => (
              <label key={q.id} className="block">
                <span className="text-sm font-medium text-slate-700">{q.prompt}</span>
                <textarea
                  value={answers[q.id] ?? ''}
                  onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                  rows={2}
                  className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
                  aria-label={q.prompt}
                />
              </label>
            ))}
          </div>
          {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
          <button
            type="button"
            onClick={handleSubmit}
            disabled={busy || questions.length === 0}
            className="mt-4 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {busy ? 'Scoring…' : 'Build pilot plan'}
          </button>
        </>
      ) : (
        <div className="mt-4 space-y-5">
          <ReadinessScorecardView scorecard={plan.scorecard} />
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h4 className="text-sm font-semibold text-slate-700">Questions for technical leaders</h4>
            {plan.technical_checklist.map((group) => (
              <div key={group.category} className="mt-3">
                <p className="text-xs font-semibold text-slate-500">{group.category}</p>
                <ul className="mt-1 space-y-1">
                  {group.items.map((item, i) => (
                    <li key={i} className="flex gap-2 text-sm text-slate-700">
                      <span className="text-slate-400">•</span>
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
          <button
            type="button"
            onClick={() => setPlan(null)}
            className="text-sm text-slate-500 hover:underline"
          >
            ← Edit answers
          </button>
        </div>
      )}
    </section>
  )
}
