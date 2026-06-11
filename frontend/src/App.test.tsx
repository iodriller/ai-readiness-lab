import { render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, test, vi } from 'vitest'
import App from './App'

afterEach(() => {
  vi.restoreAllMocks()
})

test('renders the product heading', () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify({ status: 'ok' }), { status: 200 }),
  )
  render(<App />)
  expect(screen.getByRole('heading', { name: /ai readiness lab/i })).toBeInTheDocument()
})

test('shows backend online when health check succeeds', async () => {
  vi.spyOn(globalThis, 'fetch').mockResolvedValue(
    new Response(JSON.stringify({ status: 'ok' }), { status: 200 }),
  )
  render(<App />)
  await waitFor(() => expect(screen.getByTestId('api-status')).toHaveTextContent('online'))
})

test('shows backend offline when health check fails', async () => {
  vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('network down'))
  render(<App />)
  await waitFor(() => expect(screen.getByTestId('api-status')).toHaveTextContent('offline'))
})
