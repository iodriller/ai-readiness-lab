import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import ReadinessGauge from './ReadinessGauge'

test('shows the score out of 100 and fills the ring proportionally', () => {
  const { container } = render(<ReadinessGauge score={72} />)
  expect(screen.getByText('72/100')).toBeInTheDocument()
  // The progress ring is the second circle; its dash offset is < full circumference.
  const rings = container.querySelectorAll('circle')
  expect(rings.length).toBe(2)
  const offset = Number(rings[1].getAttribute('stroke-dashoffset'))
  const dash = Number(rings[1].getAttribute('stroke-dasharray'))
  expect(offset).toBeGreaterThan(0)
  expect(offset).toBeLessThan(dash)
})

test('clamps out-of-range scores', () => {
  render(<ReadinessGauge score={140} />)
  expect(screen.getByText('100/100')).toBeInTheDocument()
})
