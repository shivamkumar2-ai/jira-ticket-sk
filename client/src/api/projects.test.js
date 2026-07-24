import { describe, expect, it } from 'vitest'
import { toProjectPayload } from './projects.js'

describe('toProjectPayload', () => {
  it('maps form values to API payload', () => {
    expect(
      toProjectPayload({
        title: 'VD-52',
        description: 'Desc',
        category: 'bug',
        status: 'in_progress',
        priority: 'high',
        progress: 40,
        tags: ['bug', 'filters'],
        resourceUrl: 'https://example.com',
        notes: 'note',
      }),
    ).toEqual({
      title: 'VD-52',
      description: 'Desc',
      category: 'bug',
      status: 'in_progress',
      priority: 'high',
      progress: 40,
      tags: ['bug', 'filters'],
      resourceUrl: 'https://example.com',
      notes: 'note',
    })
  })
})
