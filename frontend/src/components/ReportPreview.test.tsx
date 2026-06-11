import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import ReportPreview from './ReportPreview'

test('offers PDF and Markdown downloads pointing at the report endpoints', () => {
  render(<ReportPreview projectId="abc123" />)

  const pdf = screen.getByRole('link', { name: /download pdf/i })
  const md = screen.getByRole('link', { name: /download markdown/i })
  expect(pdf).toHaveAttribute('href', '/projects/abc123/report.pdf')
  expect(md).toHaveAttribute('href', '/projects/abc123/report.md')
})
