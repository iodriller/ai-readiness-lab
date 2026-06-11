import type { BriefResponse, SourceEvent } from '../api/client'
import { Sources } from './ai/Sources'
import OpportunityCardView from './OpportunityCardView'
import ReportPreview from './ReportPreview'

export default function Brief({
  brief,
  sources = [],
}: {
  brief: BriefResponse
  sources?: SourceEvent[]
}) {
  return (
    <div className="brief">
      <header className="brief-header">
        <h1>AI Readiness Brief: {brief.company_name}</h1>
        {brief.is_sample && (
          <span className="sample-badge" title="Illustrative content until research is connected">
            Sample
          </span>
        )}
      </header>

      <section className="brief-narrative">
        <h2>What matters</h2>
        <p>{brief.what_matters}</p>
        <h2>Competitive pressure</h2>
        <p>{brief.competitive_pressure}</p>
        <h2>The opening</h2>
        <p>{brief.the_opening}</p>
        <h2>Recommended next move</h2>
        <p>{brief.recommended_next_move}</p>
      </section>

      <section className="opportunities">
        <h2>Recommended opportunities</h2>
        <div className="opportunity-grid">
          {brief.opportunities.map((card) => (
            <OpportunityCardView key={card.name} card={card} />
          ))}
        </div>
      </section>

      {sources.length > 0 && (
        <section className="evidence">
          <h2>Evidence</h2>
          <Sources sources={sources} title={`${sources.length} public sources reviewed`} />
        </section>
      )}

      <ReportPreview />
    </div>
  )
}
