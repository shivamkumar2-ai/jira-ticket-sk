import {
  clearAuthSession,
  getAuthToken,
  notifyAuthLogout,
} from '../utils/authStorage.js'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '/api'

export class ApiError extends Error {
  constructor(message, { status, errors = {} } = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.errors = errors
  }
}

function toFormField(field) {
  if (field === 'resource_url') return 'resourceUrl'
  return field
}

function parseErrorBody(body) {
  const detail = body?.detail
  if (!detail) {
    return { message: 'Request failed.', errors: {} }
  }

  if (typeof detail === 'string') {
    return { message: detail, errors: {} }
  }

  const errors = Object.fromEntries(
    Object.entries(detail).map(([field, messages]) => {
      const value = Array.isArray(messages) ? messages[0] : String(messages)
      return [toFormField(field), value]
    }),
  )

  const firstError = Object.values(errors)[0]
  return {
    message: firstError ?? 'Validation failed.',
    errors,
  }
}

export async function apiRequest(path, options = {}) {
  const { signal, skipAuth = false, ...fetchOptions } = options
  const headers = {
    Accept: 'application/json',
    ...(fetchOptions.body ? { 'Content-Type': 'application/json' } : {}),
    ...fetchOptions.headers,
  }

  if (!skipAuth) {
    const token = getAuthToken()
    if (token) {
      headers.Authorization = `Bearer ${token}`
    }
  }

  let response
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...fetchOptions,
      headers,
      signal,
    })
  } catch (error) {
    if (error.name === 'AbortError') {
      throw error
    }
    throw new ApiError('Unable to reach the API. Is the backend running on port 8000?', {
      status: 0,
    })
  }

  if (response.status === 204) {
    return null
  }

  let body = null
  const contentType = response.headers.get('content-type') ?? ''
  if (contentType.includes('application/json')) {
    body = await response.json()
  }

  if (response.status === 401 && !skipAuth) {
    clearAuthSession()
    notifyAuthLogout()
  }

  if (!response.ok) {
    const { message, errors } = parseErrorBody(body)
    throw new ApiError(message, { status: response.status, errors })
  }

  return body
}
