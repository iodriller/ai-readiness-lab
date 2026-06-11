import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import type { InterimEvent, ResearchStep, SourceEvent } from '../api/client'
import ResearchConsole from './ResearchConsole'

const steps: ResearchStep[] = [
  { type: 'step', index: 1, total: 8, label: 'Identifying company profile' },
  { type: 'step', index: 2, total: 8, label: 'Classifying company type' },
]

const interims: InterimEvent[] = [
  { type: 'interim', label: 'Searching public web sources', detail: '9 research angles' },
]

const sources: SourceEvent[] = [
  { type: 'source', url: 'https://sec.gov/a', title: 'Filing A', source_type: 'filing', confidence: 0.95 },
  { type: 'source', url: 'https://reuters.com/b', title: 'News B', source_type: 'news', confidence: 0.7 },
]

test('renders steps, running count, interim feed, and the source list', () => {
  render(<ResearchConsole steps={steps} interims={interims} sources={sources} done={false} />)

  expect(screen.getByText(/identifying company profile/i)).toBeInTheDocument()
  expect(screen.getByText('2 of 8')).toBeInTheDocument()
  // Interim findings show under the active (latest) step.
  expect(screen.getByText(/searching public web sources/i)).toBeInTheDocument()
  // Source list + live count badge.
  expect(screen.getByText('Filing A')).toBeInTheDocument()
  expect(screen.getByText('2')).toBeInTheDocument()
})

test('shows a searching placeholder when no sources yet', () => {
  render(<ResearchConsole steps={steps} interims={[]} sources={[]} done={false} />)
  expect(screen.getByText('Searching…')).toBeInTheDocument()
})
