import { apiRequest } from './client.js'

function buildQuery(filters = {}) {
  const params = new URLSearchParams()

  if (filters.search?.trim()) {
    params.set('search', filters.search.trim())
  }
  if (filters.status) {
    params.set('status', filters.status)
  }
  if (filters.category) {
    params.set('category', filters.category)
  }
  if (filters.priority) {
    params.set('priority', filters.priority)
  }
  if (filters.sort) {
    params.set('sort', filters.sort)
  }
  if (filters.users?.length) {
    for (const userId of filters.users) {
      params.append('users', userId)
    }
  }

  const query = params.toString()
  return query ? `?${query}` : ''
}

export function toProjectPayload(values) {
  return {
    title: values.title,
    description: values.description,
    category: values.category,
    status: values.status,
    priority: values.priority,
    progress: Number(values.progress),
    tags: values.tags,
    resourceUrl: values.resourceUrl ?? '',
    notes: values.notes ?? '',
  }
}

export async function fetchProjects(filters, options = {}) {
  const data = await apiRequest(`/projects${buildQuery(filters)}`, options)
  return data.items ?? []
}

export async function fetchProjectStats(filters = {}, options = {}) {
  return apiRequest(`/projects/stats${buildQuery(filters)}`, options)
}

export async function createProject(values, options = {}) {
  return apiRequest('/projects', {
    method: 'POST',
    body: JSON.stringify(toProjectPayload(values)),
    ...options,
  })
}

export async function updateProject(id, values, options = {}) {
  return apiRequest(`/projects/${id}`, {
    method: 'PUT',
    body: JSON.stringify(toProjectPayload(values)),
    ...options,
  })
}

export async function deleteProject(id, options = {}) {
  return apiRequest(`/projects/${id}`, {
    method: 'DELETE',
    ...options,
  })
}
