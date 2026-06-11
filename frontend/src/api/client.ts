// Typed backend client. Domain types are generated from the backend Pydantic
// schemas — run `npm run generate:types` after changing them. Do not hand-edit
// src/api/types.ts.

export type {
  Project,
  CompanyResearchPlan,
  SourceRecord,
  CompanyIntelligenceProfile,
  CompetitiveSignal,
  OpportunityCard,
  ReadinessScorecard,
} from './types'

export interface Health {
  status: string
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
