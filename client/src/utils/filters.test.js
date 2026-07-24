import { describe, expect, it } from 'vitest'
import { computeStats, filterProjects, SORT_OPTIONS } from './filters.js'
import { CATEGORIES, PRIORITIES, STATUSES } from '../constants/index.js'

const projects = [
  {
    id: '1',
    title: 'VD-24 Login bug',
    description: 'Fix redirect',
    notes: '',
    tags: ['bug'],
    category: CATEGORIES.BUG,
    status: STATUSES.IN_PROGRESS,
    priority: PRIORITIES.HIGH,
    progress: 40,
    updatedAt: '2026-07-10T00:00:00.000Z',
  },
  {
    id: '2',
    title: 'VD-31 Filter presets story',
    description: 'Add saved filters',
    notes: 'ux',
    tags: ['filters'],
    category: CATEGORIES.STORY,
    status: STATUSES.COMPLETED,
    priority: PRIORITIES.MEDIUM,
    progress: 100,
    updatedAt: '2026-07-12T00:00:00.000Z',
  },
  {
    id: '3',
    title: 'VD-38 API task',
    description: 'Validation messages',
    notes: '',
    tags: ['api'],
    category: CATEGORIES.TASK,
    status: STATUSES.NOT_STARTED,
    priority: PRIORITIES.LOW,
    progress: 0,
    updatedAt: '2026-07-08T00:00:00.000Z',
  },
]

describe('filterProjects', () => {
  it('filters by search text across fields', () => {
    const result = filterProjects(projects, {
      search: 'ux',
      status: '',
      category: '',
      priority: '',
      sort: SORT_OPTIONS.UPDATED_DESC,
    })
    expect(result).toHaveLength(1)
    expect(result[0].title).toBe('VD-31 Filter presets story')
  })

  it('filters by status and issue type', () => {
    const result = filterProjects(projects, {
      search: '',
      status: STATUSES.IN_PROGRESS,
      category: CATEGORIES.BUG,
      priority: '',
      sort: SORT_OPTIONS.UPDATED_DESC,
    })
    expect(result).toHaveLength(1)
    expect(result[0].id).toBe('1')
  })

  it('sorts by progress descending', () => {
    const result = filterProjects(projects, {
      search: '',
      status: '',
      category: '',
      priority: '',
      sort: SORT_OPTIONS.PROGRESS_DESC,
    })
    expect(result[0].progress).toBe(100)
    expect(result.at(-1).progress).toBe(0)
  })
})

describe('computeStats', () => {
  it('returns aggregate counts', () => {
    const stats = computeStats(projects)
    expect(stats.total).toBe(3)
    expect(stats.completed).toBe(1)
    expect(stats.inProgress).toBe(1)
    expect(stats.notStarted).toBe(1)
    expect(stats.avgProgress).toBe(47)
  })
})
