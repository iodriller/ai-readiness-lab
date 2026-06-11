const SECTIONS = [
  'Executive Summary',
  'Company Context',
  'Competitive and Peer AI Signals',
  'AI Opportunity Map',
  'Selected Pilot Recommendation',
  'Readiness Scorecard',
  'Data Requirements',
  'Tool and Agent Boundaries',
  'Risk Register',
  'Evaluation Plan',
  '30/60/90-Day Roadmap',
  'Technical Leader Questions',
  'Sources and Confidence Notes',
]

export default function ReportPreview() {
  return (
    <section className="report-preview">
      <h2>Report preview</h2>
      <p className="muted">
        The exportable executive report is generated in a later phase. It will include:
      </p>
      <ol className="report-toc">
        {SECTIONS.map((section) => (
          <li key={section}>{section}</li>
        ))}
      </ol>
      <button type="button" disabled>
        Export PDF (coming soon)
      </button>
    </section>
  )
}
