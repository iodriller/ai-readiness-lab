import { reportUrl } from '../api/client'

const SECTIONS = ['Executive narrative', 'AI opportunity map', 'Strategy Q&A', 'Sources & confidence']

// Exportable executive report (spec §4.4). The brief, opportunity cards, and any
// Q&A are rendered server-side into a downloadable Markdown or PDF file.
export default function ReportPreview({ projectId }: { projectId: string }) {
  return (
    <section className="mt-8 rounded-xl border border-slate-200 bg-slate-50 p-5">
      <h2 className="text-lg font-semibold text-slate-800">Export report</h2>
      <p className="mt-1 text-sm text-slate-600">
        A shareable executive report covering: {SECTIONS.join(' · ')}.
      </p>
      <div className="mt-4 flex gap-3">
        <a
          href={reportUrl(projectId, 'pdf')}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          Download PDF
        </a>
        <a
          href={reportUrl(projectId, 'md')}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
        >
          Download Markdown
        </a>
      </div>
    </section>
  )
}
