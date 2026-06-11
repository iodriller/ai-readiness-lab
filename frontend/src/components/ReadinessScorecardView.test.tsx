import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import type { ReadinessScorecard } from '../api/client'
import ReadinessScorecardView from './ReadinessScorecardView'

const scorecard: ReadinessScorecard = {
  overall_score: 72,
  recommendation: 'limited_pilot',
  dimensions: {
    business_value: 90,
    workflow_clarity: 70,
    data_readiness: 40,
    risk_controls: 75,
    evaluation_readiness: 65,
    integration_feasibility: 70,
    operational_ownership: 60,
    user_adoption: 80,
  },
  blockers: ['Low data readiness (40/100)'],
  strengths: ['Strong business value (90/100)'],
  next_actions: ['Inventory the source systems and confirm access before building.'],
}

test('renders the overall score, recommendation, and dimension bars', () => {
  render(<ReadinessScorecardView scorecard={scorecard} />)
  expect(screen.getByText('72/100')).toBeInTheDocument()
  expect(screen.getByText(/limited pilot/i)).toBeInTheDocument()
  expect(screen.getByTestId('bar-data_readiness')).toHaveStyle({ width: '40%' })
  expect(screen.getByText(/strong business value/i)).toBeInTheDocument()
  expect(screen.getByText(/low data readiness/i)).toBeInTheDocument()
})
