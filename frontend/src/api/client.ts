// Typed backend client. Domain types are generated from the backend Pydantic
// schemas — run `npm run generate:types` after changing them. Do not hand-edit
// src/api/types.ts.

import type { BriefResponse, CreateProjectRequest, Project } from './types'

export type { BriefResponse, CreateProjectRequest, OpportunityCard, Project } from './types'

export interface Health {
  status: string
}

export interface ResearchStep {
  type: 'step'
  index: number
  total: number
  label: string
}

export interface InterimEvent {
  type: 'interim'
  label: string
  detail: string
}

export interface SourceEvent {
  type: 'source'
  url: string
  title: string
  source_type: string
  confidence: number
}

export interface StructuredAnswer {
  question: string
  question_type: string
  direct_answer: string
  why_it_matters: string
  peer_signals: string[]
  pilot_options: string[]
  recommended_first_pilot: string
  data_needed: string[]
  risks_to_control: string[]
  technical_questions: string[]
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

export async function askQuestion(projectId: string, question: string): Promise<StructuredAnswer> {
  const response = await fetch(`/projects/${projectId}/qa`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question }),
  })
  if (!response.ok) {
    throw new Error(`qa failed: ${response.status}`)
  }
  return response.json() as Promise<StructuredAnswer>
}

interface ResearchHandlers {
  onStep: (step: ResearchStep) => void
  onInterim?: (interim: InterimEvent) => void
  onSource?: (source: SourceEvent) => void
  onDone: () => void
  onError?: () => void
}

/** Subscribe to the research-progress SSE stream. Returns an unsubscribe fn. */
export function subscribeResearch(projectId: string, handlers: ResearchHandlers): () => void {
  const source = new EventSource(`/projects/${projectId}/research/stream`)

  source.onmessage = (event) => {
    const data = JSON.parse(event.data) as { type: string }
    switch (data.type) {
      case 'done':
        source.close()
        handlers.onDone()
        break
      case 'interim':
        handlers.onInterim?.(data as InterimEvent)
        break
      case 'source':
        handlers.onSource?.(data as SourceEvent)
        break
      default:
        handlers.onStep(data as ResearchStep)
    }
  }

  source.onerror = () => {
    source.close()
    handlers.onError?.()
  }

  return () => source.close()
}
