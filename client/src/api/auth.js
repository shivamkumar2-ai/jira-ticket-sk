import { apiRequest } from './client.js'

export async function registerUser({ email, password, name }) {
  return apiRequest('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, name }),
    skipAuth: true,
  })
}

export async function loginUser({ email, password }) {
  return apiRequest('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
    skipAuth: true,
  })
}

export async function fetchCurrentUser() {
  return apiRequest('/auth/me')
}
