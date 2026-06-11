import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import type { BriefResponse } from '../api/client'
import Brief from './Brief'

const brief: BriefResponse = {
  company_name: 'Acme Corp',
  is_sample: true,
  what_matters: 'What matters text.',
  competitive_pressure: 'Competitive pressure text.',
  the_opening: 'The opening text.',
  recommended_next_move: 'Next move text.',
  opportunities: [
    {
      name: 'Enterprise Knowledge Assistant',
      category: 'Knowledge & Decision Support',
      executive_summary: 'A grounded assistant.',
      why_now: 'Low-risk start.',
      competitive_pressure: 'Peers start here.',
      business_value: 'high',
      pilot_feasibility: 'high',
      risk_level: 'low',
      time_to_pilot: '60_days',
      recommended_first_step: 'Pick a corpus.',
      technical_depth_required: 'medium',
    },
  ],
}

test('renders the brief title, sample badge, and opportunity cards', () => {
  render(<Brief brief={brief} />)
  expect(screen.getByRole('heading', { name: /ai readiness brief: acme corp/i })).toBeInTheDocument()
  expect(screen.getByText(/sample/i)).toBeInTheDocument()
  expect(screen.getByRole('heading', { name: /enterprise knowledge assistant/i })).toBeInTheDocument()
  expect(screen.getByText(/value: high/i)).toBeInTheDocument()
})
