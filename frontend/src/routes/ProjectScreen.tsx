import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getBrief, subscribeResearch } from '../api/client'
import type { BriefResponse, InterimEvent, ResearchStep, SourceEvent } from '../api/client'
import Brief from '../components/Brief'
import ResearchConsole from '../components/ResearchConsole'

type Phase = 'researching' | 'ready' | 'error'

export default function ProjectScreen() {
  const { projectId } = useParams<{ projectId: string }>()
  const [phase, setPhase] = useState<Phase>('researching')
  const [steps, setSteps] = useState<ResearchStep[]>([])
  const [interims, setInterims] = useState<InterimEvent[]>([])
  const [sources, setSources] = useState<SourceEvent[]>([])
  const [brief, setBrief] = useState<BriefResponse | null>(null)

  useEffect(() => {
    if (!projectId) return
    let active = true

    const unsubscribe = subscribeResearch(projectId, {
      onStep: (step) => active && setSteps((prev) => [...prev, step]),
      onInterim: (interim) => active && setInterims((prev) => [...prev, interim]),
      onSource: (source) => active && setSources((prev) => [...prev, source]),
      onDone: async () => {
        try {
          const result = await getBrief(projectId)
          if (active) {
            setBrief(result)
            setPhase('ready')
          }
        } catch {
          if (active) setPhase('error')
        }
      },
      onError: () => active && setPhase('error'),
    })

    return () => {
      active = false
      unsubscribe()
    }
  }, [projectId])

  return (
    <main className="project">
      <nav>
        <Link to="/">← New review</Link>
      </nav>
      {phase === 'researching' && (
        <ResearchConsole steps={steps} interims={interims} sources={sources} done={false} />
      )}
      {phase === 'ready' && brief && projectId && (
        <Brief brief={brief} projectId={projectId} sources={sources} />
      )}
      {phase === 'error' && (
        <p className="error">Research could not be completed. Please try again.</p>
      )}
    </main>
  )
}
