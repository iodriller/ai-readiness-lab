import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'
import type { BriefResponse, ResearchStep } from '../api/client'
import ProjectScreen from './ProjectScreen'

const subscribeResearch = vi.fn()
const getBrief = vi.fn()

vi.mock('../api/client', () => ({
  subscribeResearch: (...args: unknown[]) => subscribeResearch(...args),
  getBrief: (...args: unknown[]) => getBrief(...args),
  // Brief → ReportPreview builds download URLs from this.
  reportUrl: (id: string, fmt: string) => `/projects/${id}/report.${fmt}`,
  // Brief fetches any saved pilot plan on mount.
  getPilot: () => Promise.resolve(null),
}))

afterEach(() => vi.clearAllMocks())

function renderProject() {
  return render(
    <MemoryRouter
      initialEntries={['/projects/test-id']}
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <Routes>
        <Route path="/projects/:projectId" element={<ProjectScreen />} />
      </Routes>
    </MemoryRouter>,
  )
}

test('shows step label while research is in progress', async () => {
  subscribeResearch.mockImplementation(
    (_id: string, { onStep }: { onStep: (s: ResearchStep) => void }) => {
      onStep({ type: 'step', index: 1, total: 8, label: 'Identifying company profile' })
      return () => {}
    },
  )
  renderProject()
  await waitFor(() =>
    expect(screen.getByText(/identifying company profile/i)).toBeInTheDocument(),
  )
})

test('shows brief after research completes', async () => {
  const brief: BriefResponse = {
    company_name: 'Test Co',
    is_sample: false,
    what_matters: 'Key context.',
    competitive_pressure: 'Peers moving fast.',
    the_opening: 'Now is the time.',
    recommended_next_move: 'Start with X.',
    opportunities: [],
  }
  subscribeResearch.mockImplementation(
    (_id: string, { onDone }: { onDone: () => void }) => {
      onDone()
      return () => {}
    },
  )
  getBrief.mockResolvedValue(brief)
  renderProject()
  await waitFor(() =>
    expect(
      screen.getByRole('heading', { name: /ai readiness brief: test co/i }),
    ).toBeInTheDocument(),
  )
})

test('shows error state when research fails', async () => {
  subscribeResearch.mockImplementation(
    (_id: string, { onError }: { onError: () => void }) => {
      onError()
      return () => {}
    },
  )
  renderProject()
  await waitFor(() =>
    expect(screen.getByText(/research could not be completed/i)).toBeInTheDocument(),
  )
})
