import type { InterimEvent, ResearchStep, SourceEvent } from '../api/client'
import { Task, TaskItem } from './ai/Task'
import { Sources } from './ai/Sources'

// The streaming research console: shows the executive what the agent is doing in
// real time — step task list with live interim findings, plus a growing source list.

interface Props {
  steps: ResearchStep[]
  interims: InterimEvent[]
  sources: SourceEvent[]
  done: boolean
}

export default function ResearchConsole({ steps, interims, sources, done }: Props) {
  const total = steps[0]?.total
  return (
    <section className="research-console">
      <div className="mb-4 flex items-baseline justify-between">
        <h2 className="text-lg font-semibold text-slate-900">Researching…</h2>
        {total && (
          <span className="text-sm text-slate-500">
            {Math.min(steps.length, total)} of {total}
          </span>
        )}
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Task title="Live progress">
          {steps.length === 0 && <TaskItem status="active" label="Starting…" />}
          {steps.map((step, i) => {
            const isLast = i === steps.length - 1
            const status = done ? 'done' : isLast ? 'active' : 'done'
            return (
              <TaskItem key={step.index} status={status} label={step.label}>
                {isLast &&
                  !done &&
                  interims.slice(-3).map((it, j) => (
                    <p key={j} className="text-xs text-slate-500">
                      ↳ {it.label}
                      {it.detail ? ` — ${it.detail}` : ''}
                    </p>
                  ))}
              </TaskItem>
            )
          })}
        </Task>

        <Sources sources={sources} />
      </div>
    </section>
  )
}
