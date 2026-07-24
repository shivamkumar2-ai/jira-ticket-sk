import { describe, expect, it } from 'vitest'
import { validateProject } from './validation.js'
import { CATEGORIES, PRIORITIES, STATUSES } from '../constants/index.js'

const validInput = {
  title: 'VD-52 Workspace filter reset',
  description: 'Filters clear unexpectedly when returning from a work item detail view.',
  category: CATEGORIES.BUG,
  status: STATUSES.IN_PROGRESS,
  priority: PRIORITIES.HIGH,
  progress: 50,
  tags: 'bug, filters',
  resourceUrl: 'https://example.com/work/VD-52',
  notes: 'Regression from last release.',
}

describe('validateProject', () => {
  it('accepts valid input', () => {
    const result = validateProject(validInput)
    expect(result.isValid).toBe(true)
    expect(result.errors).toEqual({})
    expect(result.values.title).toBe('VD-52 Workspace filter reset')
    expect(result.values.tags).toEqual(['bug', 'filters'])
  })

  it('requires summary and description', () => {
    const result = validateProject({ ...validInput, title: '  ', description: '' })
    expect(result.isValid).toBe(false)
    expect(result.errors.title).toBeTruthy()
    expect(result.errors.description).toBeTruthy()
  })

  it('rejects invalid progress and URL', () => {
    const result = validateProject({
      ...validInput,
      progress: 150,
      resourceUrl: 'not-a-url',
    })
    expect(result.isValid).toBe(false)
    expect(result.errors.progress).toBeTruthy()
    expect(result.errors.resourceUrl).toBeTruthy()
  })

  it('limits label count', () => {
    const result = validateProject({
      ...validInput,
      tags: 'a, b, c, d, e, f, g, h, i',
    })
    expect(result.isValid).toBe(false)
    expect(result.errors.tags).toBeTruthy()
  })
})
