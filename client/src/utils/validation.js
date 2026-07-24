import {
  CATEGORIES,
  PRIORITIES,
  STATUSES,
} from '../constants/index.js'

const URL_PATTERN = /^https?:\/\/.+/i

export function validateProject(input, { isEdit = false } = {}) {
  const errors = {}

  const title = input.title?.trim() ?? ''
  if (!title) {
    errors.title = 'Summary is required.'
  } else if (title.length > 120) {
    errors.title = 'Summary must be 120 characters or fewer.'
  }

  const description = input.description?.trim() ?? ''
  if (!description) {
    errors.description = 'Description is required.'
  } else if (description.length > 500) {
    errors.description = 'Description must be 500 characters or fewer.'
  }

  if (!Object.values(CATEGORIES).includes(input.category)) {
    errors.category = 'Select a valid category.'
  }

  if (!Object.values(STATUSES).includes(input.status)) {
    errors.status = 'Select a valid status.'
  }

  if (!Object.values(PRIORITIES).includes(input.priority)) {
    errors.priority = 'Select a valid priority.'
  }

  const progress = Number(input.progress)
  if (Number.isNaN(progress) || progress < 0 || progress > 100) {
    errors.progress = 'Progress must be between 0 and 100.'
  }

  const resourceUrl = input.resourceUrl?.trim() ?? ''
  if (resourceUrl && !URL_PATTERN.test(resourceUrl)) {
    errors.resourceUrl = 'Resource URL must start with http:// or https://.'
  }

  const tagsRaw = input.tags ?? ''
  const tags = typeof tagsRaw === 'string'
    ? tagsRaw.split(',').map((tag) => tag.trim()).filter(Boolean)
    : tagsRaw

  if (tags.length > 8) {
    errors.tags = 'You can add up to 8 labels.'
  }

  const invalidTag = tags.find((tag) => tag.length > 24)
  if (invalidTag) {
    errors.tags = 'Each label must be 24 characters or fewer.'
  }

  const notes = input.notes?.trim() ?? ''
  if (notes.length > 1000) {
    errors.notes = 'Comments must be 1000 characters or fewer.'
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
    values: {
      title,
      description,
      category: input.category,
      status: input.status,
      priority: input.priority,
      progress: Math.round(progress),
      tags,
      resourceUrl,
      notes,
      ...(isEdit ? {} : {}),
    },
  }
}
