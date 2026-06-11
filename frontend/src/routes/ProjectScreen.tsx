import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getBrief, subscribeResearch } from '../api/client'
import type { BriefResponse, ResearchStep } from '../api/client'
import Brief from '../components/Brief'
import ResearchProgress from '../components/ResearchProgress'

type Phase = 'researching' | 'ready' | 'error'

export default function ProjectScreen() {
  const { projectId } = useParams<{ projectId: string }>()
  const [phase, setPhase] = useState<Phase>('researching')
  const [steps, setSteps] = useState<ResearchStep[]>([])
  const [brief, setBrief] = useState<BriefResponse | null>(null)

  useEffect(() => {
    if (!projectId) return
    let active = true

    const unsubscribe = subscribeResearch(projectId, {
      onStep: (step) => active && setSteps((prev) => [...prev, step]),
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
      {phase === 'researching' && <ResearchProgress steps={steps} />}
      {phase === 'ready' && brief && <Brief brief={brief} />}
      {phase === 'error' && (
        <p className="error">Research could not be completed. Please try again.</p>
      )}
    </main>
  )
}
