import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { SearchFilters } from './SearchFilters.jsx'
import { SORT_OPTIONS } from '../utils/filters.js'

const baseFilters = {
  search: '',
  status: '',
  category: '',
  priority: '',
  sort: SORT_OPTIONS.UPDATED_DESC,
  users: ['user-1'],
}

const users = [
  { id: 'user-1', name: 'Alice', email: 'alice@example.com' },
  { id: 'user-2', name: 'Bob', email: 'bob@example.com' },
]

describe('SearchFilters', () => {
  it('updates search input', async () => {
    const user = userEvent.setup()
    const onChange = vi.fn()

    render(
      <SearchFilters
        filters={baseFilters}
        users={users}
        onChange={onChange}
        onToggleUser={() => {}}
        onClear={() => {}}
        resultCount={3}
      />,
    )

    await user.type(screen.getByRole('searchbox'), 'bug')

    expect(onChange).toHaveBeenCalled()
    expect(screen.getByText(/showing/i)).toHaveTextContent('3')
  })

  it('toggles user filter checkboxes', async () => {
    const user = userEvent.setup()
    const onToggleUser = vi.fn()

    render(
      <SearchFilters
        filters={baseFilters}
        users={users}
        onChange={() => {}}
        onToggleUser={onToggleUser}
        onClear={() => {}}
        resultCount={1}
      />,
    )

    await user.click(screen.getByLabelText(/bob/i))
    expect(onToggleUser).toHaveBeenCalledWith('user-2', true)
  })

  it('calls clear filters', async () => {
    const user = userEvent.setup()
    const onClear = vi.fn()

    render(
      <SearchFilters
        filters={{ ...baseFilters, search: 'bug' }}
        users={users}
        onChange={() => {}}
        onToggleUser={() => {}}
        onClear={onClear}
        resultCount={1}
      />,
    )

    await user.click(screen.getByRole('button', { name: /clear filters/i }))
    expect(onClear).toHaveBeenCalledTimes(1)
  })
})
