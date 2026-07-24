import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ProjectForm } from './ProjectForm.jsx'

describe('ProjectForm', () => {
  it('shows validation errors for empty submit', async () => {
    const user = userEvent.setup()
    const onSave = vi.fn(() => ({ ok: false, errors: { title: 'Summary is required.' } }))

    render(<ProjectForm onSave={onSave} onCancel={() => {}} />)

    await user.click(screen.getByRole('button', { name: /create work item/i }))

    expect(onSave).toHaveBeenCalled()
    expect(screen.getByText('Summary is required.')).toBeInTheDocument()
  })

  it('renders edit mode title', () => {
    render(
      <ProjectForm
        project={{
          title: 'Existing',
          description: 'Desc',
          category: 'task',
          status: 'in_progress',
          priority: 'medium',
          progress: 10,
          tags: ['ai'],
          resourceUrl: '',
          notes: '',
        }}
        onSave={() => ({ ok: true })}
        onCancel={() => {}}
      />,
    )

    expect(screen.getByRole('heading', { name: /edit work item/i })).toBeInTheDocument()
    expect(screen.getByDisplayValue('Existing')).toBeInTheDocument()
  })
})
