import type { OpportunityCard } from '../api/client'

const TIME_LABEL: Record<OpportunityCard['time_to_pilot'], string> = {
  '30_days': '30 days',
  '60_days': '60 days',
  '90_days': '90 days',
  longer: 'longer',
}

export default function OpportunityCardView({
  card,
  onPlan,
}: {
  card: OpportunityCard
  onPlan?: (card: OpportunityCard) => void
}) {
  return (
    <article className="opportunity-card">
      <header>
        <h3>{card.name}</h3>
        <span className="category">{card.category}</span>
      </header>
      <p>{card.executive_summary}</p>
      <p className="why-now">
        <strong>Why now:</strong> {card.why_now}
      </p>
      <ul className="badges">
        <li className={`level level-${card.business_value}`}>Value: {card.business_value}</li>
        <li className={`level level-${card.pilot_feasibility}`}>
          Feasibility: {card.pilot_feasibility}
        </li>
        <li className={`level level-${card.risk_level}`}>Risk: {card.risk_level}</li>
        <li className="time">Time to pilot: {TIME_LABEL[card.time_to_pilot]}</li>
      </ul>
      <p className="first-step">
        <strong>First step:</strong> {card.recommended_first_step}
      </p>
      {onPlan && (
        <button
          type="button"
          onClick={() => onPlan(card)}
          className="mt-2 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700"
        >
          Plan this pilot →
        </button>
      )}
    </article>
  )
}
