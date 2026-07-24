import {
  CATEGORY_LABELS,
  CATEGORIES,
  PRIORITY_LABELS,
  PRIORITIES,
  STATUS_LABELS,
  STATUSES,
} from '../constants/index.js'
import { SORT_OPTIONS } from '../utils/filters.js'

const sortLabels = {
  [SORT_OPTIONS.UPDATED_DESC]: 'Recently updated',
  [SORT_OPTIONS.UPDATED_ASC]: 'Oldest updated',
  [SORT_OPTIONS.TITLE_ASC]: 'Title A–Z',
  [SORT_OPTIONS.PROGRESS_DESC]: 'Progress high–low',
  [SORT_OPTIONS.PRIORITY_DESC]: 'Priority high–low',
}

export function SearchFilters({
  filters,
  users,
  onChange,
  onToggleUser,
  onClear,
  resultCount,
  loading = false,
}) {
  return (
    <section className="filters" aria-label="Search and filter work items">
      <div className="filters__row">
        <label className="field field--grow">
          <span>Search</span>
          <input
            type="search"
            placeholder="Search summary, description, labels, comments..."
            value={filters.search}
            onChange={(e) => onChange('search', e.target.value)}
          />
        </label>

        <label className="field">
          <span>Status</span>
          <select
            value={filters.status}
            onChange={(e) => onChange('status', e.target.value)}
          >
            <option value="">All statuses</option>
            {Object.values(STATUSES).map((status) => (
              <option key={status} value={status}>
                {STATUS_LABELS[status]}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Issue type</span>
          <select
            value={filters.category}
            onChange={(e) => onChange('category', e.target.value)}
          >
            <option value="">All issue types</option>
            {Object.values(CATEGORIES).map((category) => (
              <option key={category} value={category}>
                {CATEGORY_LABELS[category]}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Priority</span>
          <select
            value={filters.priority}
            onChange={(e) => onChange('priority', e.target.value)}
          >
            <option value="">All priorities</option>
            {Object.values(PRIORITIES).map((priority) => (
              <option key={priority} value={priority}>
                {PRIORITY_LABELS[priority]}
              </option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Sort</span>
          <select
            value={filters.sort}
            onChange={(e) => onChange('sort', e.target.value)}
          >
            {Object.entries(sortLabels).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="user-filter" aria-label="Filter by user">
        <p className="user-filter__label">Users</p>
        <div className="user-filter__list">
          {users.map((user) => (
            <label key={user.id} className="user-filter__option">
              <input
                type="checkbox"
                checked={filters.users.includes(user.id)}
                onChange={(e) => onToggleUser(user.id, e.target.checked)}
              />
              <span>{user.name}</span>
              <span className="user-filter__email">{user.email}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="filters__meta">
        <p>
          Showing <strong>{resultCount}</strong> work item{resultCount === 1 ? '' : 's'}
          {loading ? ' · Updating…' : ''}
        </p>
        <button type="button" className="btn btn--ghost btn--small" onClick={onClear}>
          Clear filters
        </button>
      </div>
    </section>
  )
}
