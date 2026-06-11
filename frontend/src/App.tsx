import { useEffect, useState } from 'react'
import { getHealth } from './api/client'

type ApiState = 'checking' | 'online' | 'offline'

export default function App() {
  const [api, setApi] = useState<ApiState>('checking')

  useEffect(() => {
    let active = true
    getHealth()
      .then((health) => active && setApi(health.status === 'ok' ? 'online' : 'offline'))
      .catch(() => active && setApi('offline'))
    return () => {
      active = false
    }
  }, [])

  return (
    <main>
      <h1>AI Readiness Lab</h1>
      <p>Know where your company stands on AI — and which pilot to launch next.</p>
      <p data-testid="api-status">Backend: {api}</p>
    </main>
  )
}
