import { useState } from 'react'
import type { StructuredAnswer } from '../api/client'
import { askQuestion } from '../api/client'
import { cn } from '../lib/utils'

// Open-ended executive Q&A (spec §10).
// Renders a question input and a structured answer panel.

export default function QAPanel({ projectId }: { projectId: string }) {
  const [question, setQuestion] = useState('')
  const [loading, setLoading] = useState(false)
  const [answer, setAnswer] = useState<StructuredAnswer | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    const q = question.trim()
    if (!q) return
    setLoading(true)
    setError(null)
    try {
      const result = await askQuestion(projectId, q)
      setAnswer(result)
    } catch {
      setError('Could not get an answer. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="mt-8">
      <h2 className="mb-3 text-lg font-semibold text-slate-800">Ask a strategy question</h2>
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="e.g. What can we do for drilling engineers?"
          className={cn(
            'flex-1 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm',
            'placeholder:text-slate-400 focus:border-blue-500 focus:outline-none',
          )}
          disabled={loading}
          aria-label="Strategy question"
        />
        <button
          type="submit"
          disabled={loading || !question.trim()}
          className={cn(
            'rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white',
            'hover:bg-blue-700 disabled:opacity-50',
          )}
        >
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>

      {error && <p className="mt-2 text-sm text-red-600">{error}</p>}
      {answer && <AnswerCard answer={answer} />}
    </section>
  )
}

function AnswerCard({ answer }: { answer: StructuredAnswer }) {
  return (
    <div
      className="mt-4 rounded-xl border border-slate-200 bg-white p-5 shadow-sm"
      data-testid="answer-card"
    >
      <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">
        {answer.question_type.replace(/_/g, ' ')}
      </p>
      <p className="mb-4 text-base font-medium text-slate-900">{answer.direct_answer}</p>

      <Section title="Why it matters" items={[answer.why_it_matters]} prose />

      {answer.peer_signals.length > 0 && (
        <Section title="Peer &amp; industry signals" items={answer.peer_signals} />
      )}

      <Section title="Pilot options" items={answer.pilot_options} />

      <div className="mt-3 rounded-lg bg-blue-50 px-4 py-3">
        <p className="text-xs font-medium text-blue-700">Recommended first pilot</p>
        <p className="text-sm text-blue-900">{answer.recommended_first_pilot}</p>
      </div>

      <Section title="Data needed" items={answer.data_needed} />
      <Section title="Risks to control" items={answer.risks_to_control} />
      <Section title="Questions for technical leaders" items={answer.technical_questions} />
    </div>
  )
}

function Section({
  title,
  items,
  prose = false,
}: {
  title: string
  items: string[]
  prose?: boolean
}) {
  if (!items.length) return null
  return (
    <div className="mt-3">
      <p className="mb-1 text-xs font-semibold text-slate-500">{title}</p>
      {prose ? (
        <p className="text-sm text-slate-700">{items[0]}</p>
      ) : (
        <ul className="space-y-1">
          {items.map((item, i) => (
            <li key={i} className="flex gap-2 text-sm text-slate-700">
              <span className="mt-0.5 text-slate-400">•</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
