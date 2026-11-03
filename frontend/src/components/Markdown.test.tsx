/**
 * Tests für die Markdown-Anzeige.
 */
import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { Markdown } from './Markdown'

describe('Markdown', () => {
  it('formatiert Überschriften, Code und Links', () => {
    render(
      <Markdown text={'## Arrays\n\nEin `array` speichert Werte. [PHP](https://www.php.net/)'} />,
    )

    expect(screen.getByRole('heading', { name: 'Arrays' })).toBeInTheDocument()
    expect(screen.getByText('array').tagName).toBe('CODE')
    const link = screen.getByRole('link', { name: 'PHP' })
    expect(link).toHaveAttribute('target', '_blank')
    expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  it('führt kein HTML aus dem Text aus', () => {
    const { container } = render(
      <Markdown text={'Hallo <img src=x onerror="alert(1)"> <script>alert(1)</script>'} />,
    )

    expect(container.querySelector('img')).toBeNull()
    expect(container.querySelector('script')).toBeNull()
  })
})
