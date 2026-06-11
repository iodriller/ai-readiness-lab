import type { ResearchStep } from '../api/client'

export default function ResearchProgress({ steps }: { steps: ResearchStep[] }) {
  const total = steps[0]?.total
  return (
    <section className="research-progress">
      <h2>Building AI readiness context…</h2>
      <ol>
        {steps.map((step) => (
          <li key={step.index}>
            <span className="check">✓</span> {step.label}
          </li>
        ))}
      </ol>
      {total ? (
        <p className="progress-count">
          {steps.length} of {total}
        </p>
      ) : (
        <p className="progress-count">Starting…</p>
      )}
    </section>
  )
}
