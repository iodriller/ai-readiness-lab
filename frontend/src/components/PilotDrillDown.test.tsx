import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import * as client from '../api/client'
import type { OpportunityCard, PilotPlan } from '../api/client'
import PilotDrillDown from './PilotDrillDown'

const card = {
  name: 'Enterprise Knowledge Assistant',
  category: 'Knowledge',
  executive_summary: 's',
  why_now: 'w',
  competitive_pressure: 'p',
  business_value: 'high',
  pilot_feasibility: 'high',
  risk_level: 'low',
  time_to_pilot: '60_days',
  recommended_first_step: 'scope',
  technical_depth_required: 'medium',
} as OpportunityCard

const PLAN: PilotPlan = {
  profile: { opportunity_name: card.name, answers: {} },
  scorecard: {
    overall_score: 81,
    recommendation: 'proceed',
    dimensions: {
      business_value: 90,
      workflow_clarity: 85,
      data_readiness: 80,
      risk_controls: 85,
      evaluation_readiness: 80,
      integration_feasibility: 85,
      operational_ownership: 75,
      user_adoption: 85,
    },
    blockers: [],
    strengths: ['Strong business value (90/100)'],
    next_actions: [],
  },
  technical_checklist: [
    { category: 'Data and systems', items: ['Where are the relevant documents stored?'] },
  ],
}

test('loads questions, submits answers, and shows the scorecard + checklist', async () => {
  vi.spyOn(client, 'getPilotQuestions').mockResolvedValue({
    opportunity_name: card.name,
    questions: [{ id: 'users', prompt: 'Who would use this?' }],
  })
  vi.spyOn(client, 'submitPilot').mockResolvedValue(PLAN)
  const user = userEvent.setup()

  render(<PilotDrillDown projectId="p1" card={card} onClose={() => {}} />)

  await waitFor(() => screen.getByLabelText(/who would use this/i))
  await user.type(screen.getByLabelText(/who would use this/i), 'Field engineers')
  await user.click(screen.getByRole('button', { name: /build pilot plan/i }))

  await waitFor(() => screen.getByText('81/100'))
  expect(screen.getByText(/proceed/i)).toBeInTheDocument()
  expect(screen.getByText(/questions for technical leaders/i)).toBeInTheDocument()
  expect(client.submitPilot).toHaveBeenCalledWith('p1', card.name, { users: 'Field engineers' })
})
