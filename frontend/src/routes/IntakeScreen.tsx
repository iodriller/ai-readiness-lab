import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createProject } from '../api/client'
import type { CreateProjectRequest } from '../api/client'
import SettingsPanel from '../components/SettingsPanel'

const ROLES = ['CTO', 'CIO', 'CEO', 'COO', 'VP', 'Director', 'Transformation Lead', 'Consultant']

const MODES: { value: CreateProjectRequest['mode']; label: string }[] = [
  { value: 'discover_opportunities', label: 'Find AI opportunities' },
  { value: 'evaluate_idea', label: 'Evaluate a specific AI idea' },
  { value: 'strategy_question', label: 'Ask a strategy question' },
  { value: 'compare_competitors', label: 'Compare against competitors' },
]

export default function IntakeScreen() {
  const navigate = useNavigate()
  const [companyName, setCompanyName] = useState('')
  const [userRole, setUserRole] = useState(ROLES[0])
  const [mode, setMode] = useState<CreateProjectRequest['mode']>(MODES[0].value)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!companyName.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const project = await createProject({ company_name: companyName.trim(), user_role: userRole, mode })
      navigate(`/projects/${project.project_id}`)
    } catch {
      setError('Could not start the review. Is the backend running?')
      setSubmitting(false)
    }
  }

  return (
    <main className="intake">
      <h1>AI Readiness Lab</h1>
      <p className="tagline">
        See where your company stands on AI, where competitors are moving, and which pilot is worth
        launching next.
      </p>

      <div className="mb-4">
        <SettingsPanel />
      </div>

      <form onSubmit={handleSubmit}>
        <label>
          Company name
          <input
            type="text"
            value={companyName}
            onChange={(event) => setCompanyName(event.target.value)}
            placeholder="e.g. Occidental Petroleum"
            autoFocus
          />
        </label>

        <label>
          Your role
          <select value={userRole} onChange={(event) => setUserRole(event.target.value)}>
            {ROLES.map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </select>
        </label>

        <fieldset>
          <legend>What do you want to do?</legend>
          {MODES.map((option) => (
            <label key={option.value} className="mode-option">
              <input
                type="radio"
                name="mode"
                value={option.value}
                checked={mode === option.value}
                onChange={() => setMode(option.value)}
              />
              {option.label}
            </label>
          ))}
        </fieldset>

        <button type="submit" disabled={!companyName.trim() || submitting}>
          {submitting ? 'Starting…' : 'Start Review'}
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </main>
  )
}
