import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import * as client from '../api/client'
import SettingsPanel from './SettingsPanel'

const SAMPLE: client.SettingsStatus = {
  has_api_key: false,
  key_hint: '',
  mode: 'sample',
  source: 'none',
}

const LIVE: client.SettingsStatus = {
  has_api_key: true,
  key_hint: '…5678',
  mode: 'live',
  source: 'keychain',
}

test('shows sample-mode banner and opens the key modal', async () => {
  vi.spyOn(client, 'getSettings').mockResolvedValue(SAMPLE)
  const user = userEvent.setup()

  render(<SettingsPanel />)

  await waitFor(() => screen.getByText(/sample mode/i))
  await user.click(screen.getByRole('button', { name: /research mode settings/i }))

  expect(screen.getByRole('dialog')).toBeInTheDocument()
  expect(screen.getByLabelText(/anthropic api key/i)).toBeInTheDocument()
  // One-click path to obtain a key.
  expect(screen.getByRole('link', { name: /anthropic console/i })).toHaveAttribute(
    'href',
    expect.stringContaining('console.anthropic.com'),
  )
})

test('saving a key enables live mode', async () => {
  vi.spyOn(client, 'getSettings').mockResolvedValue(SAMPLE)
  vi.spyOn(client, 'saveApiKey').mockResolvedValue(LIVE)
  const user = userEvent.setup()

  render(<SettingsPanel />)
  await waitFor(() => screen.getByText(/sample mode/i))
  await user.click(screen.getByRole('button', { name: /research mode settings/i }))

  await user.type(screen.getByLabelText(/anthropic api key/i), 'sk-ant-abcd-5678')
  await user.click(screen.getByRole('button', { name: /save & enable/i }))

  await waitFor(() => screen.getByText(/live research enabled/i))
  expect(client.saveApiKey).toHaveBeenCalledWith('sk-ant-abcd-5678')
})

test('surfaces a validation error from the server', async () => {
  vi.spyOn(client, 'getSettings').mockResolvedValue(SAMPLE)
  vi.spyOn(client, 'saveApiKey').mockRejectedValue(new Error("That doesn't look like an Anthropic API key"))
  const user = userEvent.setup()

  render(<SettingsPanel />)
  await waitFor(() => screen.getByText(/sample mode/i))
  await user.click(screen.getByRole('button', { name: /research mode settings/i }))
  await user.type(screen.getByLabelText(/anthropic api key/i), 'wrong')
  await user.click(screen.getByRole('button', { name: /save & enable/i }))

  await waitFor(() => screen.getByText(/doesn't look like an anthropic api key/i))
})
