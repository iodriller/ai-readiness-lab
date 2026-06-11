import { Route, Routes } from 'react-router-dom'
import IntakeScreen from './routes/IntakeScreen'
import ProjectScreen from './routes/ProjectScreen'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<IntakeScreen />} />
      <Route path="/projects/:projectId" element={<ProjectScreen />} />
    </Routes>
  )
}
