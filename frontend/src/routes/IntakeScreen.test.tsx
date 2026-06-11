import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, expect, test, vi } from 'vitest'
import IntakeScreen from './IntakeScreen'

const navigate = vi.fn()
vi.mock('react-router-dom', async (importOriginal) => ({
  ...(await importOriginal<typeof import('react-router-dom')>()),
  useNavigate: () => navigate,
}))

const createProject = vi.fn()
vi.mock('../api/client', () => ({
  createProject: (...args: unknown[]) => createProject(...args),
}))

afterEach(() => {
  vi.clearAllMocks()
})

function renderIntake() {
  return render(
    <MemoryRouter>
      <IntakeScreen />
    </MemoryRouter>,
  )
}

test('renders intake fields without technical settings', () => {
  renderIntake()
  expect(screen.getByRole('heading', { name: /ai readiness lab/i })).toBeInTheDocument()
  expect(screen.getByText(/company name/i)).toBeInTheDocument()
  expect(screen.getByText(/find ai opportunities/i)).toBeInTheDocument()
  // Executive surface stays clean — no model/infra knobs.
  expect(screen.queryByText(/model/i)).not.toBeInTheDocument()
  expect(screen.queryByText(/vector/i)).not.toBeInTheDocument()
})

test('submitting creates a project and navigates to it', async () => {
  createProject.mockResolvedValue({ project_id: 'abc123' })
  const user = userEvent.setup()
  renderIntake()

  await user.type(screen.getByPlaceholderText(/occidental/i), 'Acme Corp')
  await user.click(screen.getByRole('button', { name: /start review/i }))

  await waitFor(() =>
    expect(createProject).toHaveBeenCalledWith({
      company_name: 'Acme Corp',
      user_role: 'CTO',
      mode: 'discover_opportunities',
    }),
  )
  expect(navigate).toHaveBeenCalledWith('/projects/abc123')
})

test('start button is disabled until a company name is entered', () => {
  renderIntake()
  expect(screen.getByRole('button', { name: /start review/i })).toBeDisabled()
})
