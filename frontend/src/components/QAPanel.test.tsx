import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import * as client from '../api/client'
import QAPanel from './QAPanel'

const MOCK_ANSWER: client.StructuredAnswer = {
  question: 'What pilots should we run?',
  question_type: 'opportunity_seeking',
  direct_answer: 'Start with an Enterprise Knowledge Assistant.',
  why_it_matters: 'Quick wins build momentum.',
  peer_signals: ['Competitor A: AI drilling platform [drilling]'],
  pilot_options: ['Enterprise Knowledge Assistant: A grounded assistant.'],
  recommended_first_pilot: 'Enterprise Knowledge Assistant',
  data_needed: ['Internal documents', 'SharePoint access'],
  risks_to_control: ['Change management', 'Data privacy'],
  technical_questions: ['What cloud platform is approved?'],
}

test('submits a question and renders the structured answer', async () => {
  vi.spyOn(client, 'askQuestion').mockResolvedValue(MOCK_ANSWER)
  const user = userEvent.setup()

  render(<QAPanel projectId="proj-123" />)

  const input = screen.getByRole('textbox', { name: /strategy question/i })
  await user.type(input, 'What pilots should we run?')
  await user.click(screen.getByRole('button', { name: /ask/i }))

  await waitFor(() => screen.getByTestId('answer-card'))

  expect(screen.getByText(/start with an enterprise knowledge assistant/i)).toBeInTheDocument()
  // The name appears in both pilot options and recommended first pilot — both present.
  expect(screen.getAllByText(/enterprise knowledge assistant/i).length).toBeGreaterThanOrEqual(1)
  expect(screen.getByText(/opportunity seeking/i)).toBeInTheDocument()
})

test('Ask button is disabled when input is empty', () => {
  render(<QAPanel projectId="proj-123" />)
  expect(screen.getByRole('button', { name: /ask/i })).toBeDisabled()
})

test('shows error message when request fails', async () => {
  vi.spyOn(client, 'askQuestion').mockRejectedValue(new Error('network error'))
  const user = userEvent.setup()

  render(<QAPanel projectId="proj-123" />)
  await user.type(screen.getByRole('textbox', { name: /strategy question/i }), 'A question')
  await user.click(screen.getByRole('button', { name: /ask/i }))

  await waitFor(() => screen.getByText(/could not get an answer/i))
})
