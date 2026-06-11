import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import './index.css'

// HashRouter keeps all routing client-side (#/projects/:id), so the bundled
// FastAPI server only ever serves "/" and assets — no deep-link route config,
// no collision with the API's /projects endpoints.
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
