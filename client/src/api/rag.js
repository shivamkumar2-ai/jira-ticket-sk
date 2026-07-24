import { apiRequest } from './client.js'

export async function fetchRagStatus(options = {}) {
  return apiRequest('/rag/status', options)
}

export async function indexWorkspace(options = {}) {
  return apiRequest('/rag/index', {
    method: 'POST',
    ...options,
  })
}

export async function askRag(question, options = {}) {
  return apiRequest('/rag/ask', {
    method: 'POST',
    body: JSON.stringify({ question }),
    ...options,
  })
}
