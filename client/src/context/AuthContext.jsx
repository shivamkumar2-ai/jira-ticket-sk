import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { fetchCurrentUser, loginUser, registerUser } from '../api/auth.js'
import { ApiError } from '../api/client.js'
import {
  AUTH_LOGOUT_EVENT,
  clearAuthSession,
  getAuthToken,
  getStoredUser,
  saveAuthSession,
} from '../utils/authStorage.js'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getStoredUser())
  const [initializing, setInitializing] = useState(true)

  const logout = useCallback(() => {
    clearAuthSession()
    setUser(null)
  }, [])

  const establishSession = useCallback((payload) => {
    saveAuthSession(payload)
    setUser(payload.user)
  }, [])

  const login = useCallback(
    async ({ email, password }) => {
      const payload = await loginUser({ email, password })
      establishSession(payload)
      return payload.user
    },
    [establishSession],
  )

  const register = useCallback(
    async ({ email, password, name }) => {
      const payload = await registerUser({ email, password, name })
      establishSession(payload)
      return payload.user
    },
    [establishSession],
  )

  useEffect(() => {
    const token = getAuthToken()
    if (!token) {
      setInitializing(false)
      return undefined
    }

    let active = true
    fetchCurrentUser()
      .then((currentUser) => {
        if (active) {
          setUser(currentUser)
        }
      })
      .catch(() => {
        if (active) {
          logout()
        }
      })
      .finally(() => {
        if (active) {
          setInitializing(false)
        }
      })

    return () => {
      active = false
    }
  }, [logout])

  useEffect(() => {
    const handleLogout = () => logout()
    window.addEventListener(AUTH_LOGOUT_EVENT, handleLogout)
    return () => window.removeEventListener(AUTH_LOGOUT_EVENT, handleLogout)
  }, [logout])

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      initializing,
      login,
      register,
      logout,
    }),
    [user, initializing, login, register, logout],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export function getAuthErrorMessage(error, fallback = 'Something went wrong.') {
  if (error instanceof ApiError) {
    return error.message
  }
  return fallback
}
