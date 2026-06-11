import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { expect, test, vi } from 'vitest'
import * as client from '../api/client'
import RecentReviews from './RecentReviews'

function renderWithRouter() {
  return render(
    <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <RecentReviews />
    </MemoryRouter>,
  )
}

test('lists recent reviews as links to each project', async () => {
  vi.spyOn(client, 'listProjects').mockResolvedValue([
    {
      project_id: 'p1',
      company_name: 'Occidental',
      user_role: 'CTO',
      mode: 'discover_opportunities',
      status: 'ready',
      created_at: new Date().toISOString(),
    },
  ])

  renderWithRouter()

  await waitFor(() => screen.getByText('Occidental'))
  expect(screen.getByRole('link', { name: /occidental/i })).toHaveAttribute('href', '/projects/p1')
})

test('renders nothing when there are no projects', async () => {
  vi.spyOn(client, 'listProjects').mockResolvedValue([])
  const { container } = renderWithRouter()
  await waitFor(() => expect(container).toBeEmptyDOMElement())
})
