import { apiRequest } from './client.js'

export async function fetchUsers(options = {}) {
  const data = await apiRequest('/users', options)
  return data.items ?? []
}
