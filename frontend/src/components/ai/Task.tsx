import type { ReactNode } from 'react'
import { cn } from '../../lib/utils'

// AI Elements-style Task list: a titled panel of steps, each with a status icon.
// Owned in-repo so we can extend it freely (see docs/ARCHITECTURE.md).

export type TaskStatus = 'done' | 'active' | 'pending'

export function Task({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <p className="mb-3 text-sm font-semibold text-slate-700">{title}</p>
      <ol className="space-y-2">{children}</ol>
    </div>
  )
}

export function TaskItem({
  status,
  label,
  children,
}: {
  status: TaskStatus
  label: string
  children?: ReactNode
}) {
  return (
    <li className="text-sm">
      <div className="flex items-center gap-2">
        <StatusIcon status={status} />
        <span
          className={cn(
            status === 'pending' && 'text-slate-400',
            status === 'active' && 'font-medium text-slate-900',
            status === 'done' && 'text-slate-600',
          )}
        >
          {label}
        </span>
      </div>
      {children && <div className="ml-6 mt-1 space-y-1">{children}</div>}
    </li>
  )
}

function StatusIcon({ status }: { status: TaskStatus }) {
  if (status === 'done') {
    return (
      <span className="text-green-600" aria-label="done">
        ✓
      </span>
    )
  }
  if (status === 'active') {
    return (
      <span
        className="inline-block h-3 w-3 animate-spin rounded-full border-2 border-blue-500 border-t-transparent"
        role="status"
        aria-label="in progress"
      />
    )
  }
  return (
    <span className="text-slate-300" aria-label="pending">
      ○
    </span>
  )
}
