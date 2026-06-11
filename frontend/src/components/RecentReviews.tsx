import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listProjects } from '../api/client'
import type { ProjectSummary } from '../api/client'

function timeAgo(iso: string): string {
  const seconds = Math.max(0, (Date.now() - new Date(iso).getTime()) / 1000)
  if (seconds < 60) return 'just now'
  const mins = Math.floor(seconds / 60)
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  return `${Math.floor(hours / 24)}d ago`
}

// Project history (spec §11 home): revisit past reviews instead of losing them
// when the window closes.
export default function RecentReviews() {
  const [projects, setProjects] = useState<ProjectSummary[]>([])

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(() => setProjects([]))
  }, [])

  if (projects.length === 0) return null

  return (
    <section className="mt-8">
      <h2 className="mb-2 text-sm font-semibold text-slate-500">Recent reviews</h2>
      <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white">
        {projects.slice(0, 6).map((p) => (
          <li key={p.project_id}>
            <Link
              to={`/projects/${p.project_id}`}
              className="flex items-center justify-between px-4 py-2.5 text-sm hover:bg-slate-50"
            >
              <span className="font-medium text-slate-800">{p.company_name}</span>
              <span className="text-slate-400">
                {p.user_role} · {timeAgo(p.created_at)}
              </span>
            </Link>
          </li>
        ))}
      </ul>
    </section>
  )
}
