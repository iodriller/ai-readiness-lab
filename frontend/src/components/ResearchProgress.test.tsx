import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import type { ResearchStep } from '../api/client'
import ResearchProgress from './ResearchProgress'

test('renders received steps with a running count', () => {
  const steps: ResearchStep[] = [
    { type: 'step', index: 1, total: 8, label: 'Identifying company profile' },
    { type: 'step', index: 2, total: 8, label: 'Classifying company type and business segments' },
  ]
  render(<ResearchProgress steps={steps} />)

  expect(screen.getByText(/identifying company profile/i)).toBeInTheDocument()
  expect(screen.getByText(/classifying company type/i)).toBeInTheDocument()
  expect(screen.getByText('2 of 8')).toBeInTheDocument()
})
