import { cn } from '../../lib/utils'

// AI Elements-style Sources panel: a live count badge + a credibility-tagged list.
// Colors follow the backend SourceType confidence hierarchy (filing > official > …).
// Accepts any source-like row (live SourceEvent or a persisted BriefSource).

export interface SourceLike {
  url: string
  title?: string
  source_type: string
  confidence: number
}

const TYPE_COLOR: Record<string, string> = {
  filing: 'bg-emerald-100 text-emerald-700',
  official: 'bg-blue-100 text-blue-700',
  analyst: 'bg-violet-100 text-violet-700',
  news: 'bg-amber-100 text-amber-700',
  academic: 'bg-cyan-100 text-cyan-700',
  job_posting: 'bg-pink-100 text-pink-700',
  vendor: 'bg-slate-100 text-slate-600',
  blog: 'bg-slate-100 text-slate-500',
}

export function Sources({ sources, title = 'Sources gathered' }: { sources: SourceLike[]; title?: string }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-semibold text-slate-700">{title}</p>
        <span className="rounded-full bg-slate-900 px-2 py-0.5 text-xs font-semibold text-white">
          {sources.length}
        </span>
      </div>
      {sources.length === 0 ? (
        <p className="text-sm text-slate-400">Searching…</p>
      ) : (
        <ul className="space-y-1.5">
          {sources.map((s) => (
            <li key={s.url} className="flex items-center gap-2 text-sm">
              <span
                className={cn(
                  'rounded px-1.5 py-0.5 text-[11px] font-medium',
                  TYPE_COLOR[s.source_type] ?? TYPE_COLOR.blog,
                )}
              >
                {s.source_type}
              </span>
              <a
                href={s.url}
                target="_blank"
                rel="noreferrer"
                className="truncate text-blue-600 hover:underline"
              >
                {s.title || s.url}
              </a>
              <span className="ml-auto shrink-0 text-xs text-slate-400">
                {Math.round(s.confidence * 100)}%
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
