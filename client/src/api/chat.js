import { apiRequest } from './client.js'

export async function fetchChatMessages(options = {}) {
  const data = await apiRequest('/chat/messages', options)
  return data.items
}

export async function sendChatMessage(content, options = {}) {
  return apiRequest('/chat/messages', {
    method: 'POST',
    body: JSON.stringify({ content }),
    ...options,
  })
}
