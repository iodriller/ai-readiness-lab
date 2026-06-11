// Typed backend client. Domain types are generated from the backend Pydantic
// schemas — run `npm run generate:types` after changing them. Do not hand-edit
// src/api/types.ts.

import type { BriefResponse, CreateProjectRequest, Project } from './types'

export type { BriefResponse, CreateProjectRequest, OpportunityCard, Project } from './types'

export interface Health {
  status: string
}

export interface ResearchStep {
  type: 'step' | 'done'
  index?: number
  total?: number
  label?: string
}

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path)
  if (!response.ok) {
    throw new Error(`${path} failed: ${response.status}`)
  }
  return response.json() as Promise<T>
}

export function getHealth(): Promise<Health> {
  return getJson<Health>('/health')
}

export async function createProject(request: CreateProjectRequest): Promise<Project> {
  const response = await fetch('/projects', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  })
  if (!response.ok) {
    throw new Error(`create project failed: ${response.status}`)
  }
  return response.json() as Promise<Project>
}

export function getBrief(projectId: string): Promise<BriefResponse> {
  return getJson<BriefResponse>(`/projects/${projectId}/brief`)
}

interface ResearchHandlers {
  onStep: (step: ResearchStep) => void
  onDone: () => void
  onError?: () => void
}

/** Subscribe to the research-progress SSE stream. Returns an unsubscribe fn. */
export function subscribeResearch(projectId: string, handlers: ResearchHandlers): () => void {
  const source = new EventSource(`/projects/${projectId}/research/stream`)

  source.onmessage = (event) => {
    const step = JSON.parse(event.data) as ResearchStep
    if (step.type === 'done') {
      source.close()
      handlers.onDone()
    } else {
      handlers.onStep(step)
    }
  }

  source.onerror = () => {
    source.close()
    handlers.onError?.()
  }

  return () => source.close()
}
