import { useEffect, useState } from 'react'
import { clearApiKey, getSettings, saveApiKey } from '../api/client'
import type { SettingsStatus } from '../api/client'
import { cn } from '../lib/utils'

const CONSOLE_URL = 'https://console.anthropic.com/settings/keys'

// Seamless key setup: a status banner on the landing screen that tells the exec
// whether live research is on, and a two-click modal to paste an Anthropic key.
// The key is stored server-side in the OS keychain; the UI only ever sees a hint.
export default function SettingsPanel() {
  const [status, setStatus] = useState<SettingsStatus | null>(null)
  const [open, setOpen] = useState(false)

  useEffect(() => {
    getSettings().then(setStatus).catch(() => setStatus(null))
  }, [])

  if (!status) return null
  const live = status.mode === 'live'

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={cn(
          'flex w-full items-center justify-between gap-3 rounded-lg border px-4 py-2.5 text-left text-sm',
          live ? 'border-green-200 bg-green-50' : 'border-amber-200 bg-amber-50',
        )}
        aria-label="Research mode settings"
      >
        <span className="flex items-center gap-2">
          <span className={cn('h-2 w-2 rounded-full', live ? 'bg-green-500' : 'bg-amber-500')} />
          <span className={cn('font-medium', live ? 'text-green-800' : 'text-amber-800')}>
            {live
              ? `Live research enabled${status.key_hint ? ` · key ${status.key_hint}` : ''}`
              : 'Sample mode — add your Anthropic key for live research'}
          </span>
        </span>
        <span className={cn('text-xs underline', live ? 'text-green-700' : 'text-amber-700')}>
          {live ? 'Manage' : 'Enable live research'}
        </span>
      </button>

      {open && (
        <SettingsModal
          status={status}
          onClose={() => setOpen(false)}
          onChange={(next) => setStatus(next)}
        />
      )}
    </>
  )
}

function SettingsModal({
  status,
  onClose,
  onChange,
}: {
  status: SettingsStatus
  onClose: () => void
  onChange: (next: SettingsStatus) => void
}) {
  const [key, setKey] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSave() {
    if (!key.trim()) return
    setBusy(true)
    setError(null)
    try {
      const next = await saveApiKey(key.trim())
      onChange(next)
      onClose()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save the key.')
    } finally {
      setBusy(false)
    }
  }

  async function handleRemove() {
    setBusy(true)
    setError(null)
    try {
      onChange(await clearApiKey())
      onClose()
    } catch {
      setError('Could not remove the key.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4"
      role="dialog"
      aria-modal="true"
      aria-label="Research settings"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-2xl bg-white p-6 shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 className="text-lg font-semibold text-slate-900">Enable live research</h2>
        <p className="mt-2 text-sm text-slate-600">
          Paste your Anthropic API key to research real companies. It is stored securely on this
          computer (the system keychain) and never leaves it except to call Claude. You can explore
          with sample data without a key.
        </p>

        <a
          href={CONSOLE_URL}
          target="_blank"
          rel="noopener noreferrer"
          className="mt-3 inline-block text-sm font-medium text-blue-600 underline"
        >
          Get a key from the Anthropic Console →
        </a>

        <input
          type="password"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          placeholder="sk-ant-…"
          className="mt-4 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          aria-label="Anthropic API key"
          autoFocus
        />
        {error && <p className="mt-2 text-sm text-red-600">{error}</p>}

        <div className="mt-5 flex items-center justify-between gap-2">
          {status.source === 'keychain' ? (
            <button
              type="button"
              onClick={handleRemove}
              disabled={busy}
              className="text-sm text-slate-500 underline disabled:opacity-50"
            >
              Remove saved key
            </button>
          ) : (
            <button type="button" onClick={onClose} className="text-sm text-slate-500 underline">
              Continue with sample data
            </button>
          )}
          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg px-4 py-2 text-sm text-slate-600 hover:bg-slate-100"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              disabled={busy || !key.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {busy ? 'Saving…' : 'Save & enable'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
