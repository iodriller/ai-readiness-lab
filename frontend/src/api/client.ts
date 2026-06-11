// Typed backend client. Domain types are generated from the backend Pydantic
// schemas — run `npm run generate:types` after changing them. Do not hand-edit
// src/api/types.ts.

import type {
  BriefResponse,
  CreateProjectRequest,
  PilotPlan,
  PilotQuestionsResponse,
  Project,
  ProjectSummary,
  SettingsStatus,
  StructuredAnswer,
} from './types'

export type {
  BriefResponse,
  CreateProjectRequest,
  OpportunityCard,
  PilotPlan,
  PilotQuestion,
  PilotQuestionsResponse,
  Project,
  ProjectSummary,
  ReadinessScorecard,
  SettingsStatus,
  StructuredAnswer,
} from './types'

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

export function listProjects(): Promise<ProjectSummary[]> {
  return getJson<ProjectSummary[]>('/projects')
}

/** Download URLs for the exportable report (served with Content-Disposition). */
export function reportUrl(projectId: string, format: 'md' | 'pdf'): string {
  return `/projects/${projectId}/report.${format}`
}

export function getPilotQuestions(
  projectId: string,
  opportunity: string,
): Promise<PilotQuestionsResponse> {
  return getJson<PilotQuestionsResponse>(
    `/projects/${projectId}/pilot/questions?opportunity=${encodeURIComponent(opportunity)}`,
  )
}

export async function submitPilot(
  projectId: string,
  opportunityName: string,
  answers: Record<string, string>,
): Promise<PilotPlan> {
  const response = await fetch(`/projects/${projectId}/pilot`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ opportunity_name: opportunityName, answers }),
  })
  if (!response.ok) {
    throw new Error(`pilot submit failed: ${response.status}`)
  }
  return response.json() as Promise<PilotPlan>
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

export function getSettings(): Promise<SettingsStatus> {
  return getJson<SettingsStatus>('/settings')
}

export async function saveApiKey(apiKey: string): Promise<SettingsStatus> {
  const response = await fetch('/settings/api-key', {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ api_key: apiKey }),
  })
  if (!response.ok) {
    const detail = await response
      .json()
      .then((b) => b.detail)
      .catch(() => null)
    throw new Error(detail || `save key failed: ${response.status}`)
  }
  return response.json() as Promise<SettingsStatus>
}

export async function clearApiKey(): Promise<SettingsStatus> {
  const response = await fetch('/settings/api-key', { method: 'DELETE' })
  if (!response.ok) {
    throw new Error(`clear key failed: ${response.status}`)
  }
  return response.json() as Promise<SettingsStatus>
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
