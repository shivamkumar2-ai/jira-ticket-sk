import { useCallback, useEffect, useState } from 'react'
import { ApiError } from '../api/client.js'
import { askRag, fetchRagStatus } from '../api/rag.js'

const CHAT_MODE_KEY = 'velodesk-chat-mode'

function readStoredMode() {
  try {
    return localStorage.getItem(CHAT_MODE_KEY) === 'ai' ? 'ai' : 'team'
  } catch {
    return 'team'
  }
}

function storeMode(mode) {
  try {
    localStorage.setItem(CHAT_MODE_KEY, mode)
  } catch {
    // ignore storage errors
  }
}

function createAiMessage(role, content, extras = {}) {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    content,
    ...extras,
  }
}

export function useRag({ enabled = true, open = false } = {}) {
  const [mode, setMode] = useState(readStoredMode)
  const [aiMessages, setAiMessages] = useState([])
  const [configured, setConfigured] = useState(false)
  const [indexedCount, setIndexedCount] = useState(0)
  const [loadingStatus, setLoadingStatus] = useState(false)
  const [asking, setAsking] = useState(false)
  const [error, setError] = useState(null)

  const loadStatus = useCallback(async (options = {}) => {
    if (!enabled) {
      return
    }

    setLoadingStatus(true)
    try {
      const status = await fetchRagStatus(options)
      setConfigured(status.configured)
      setIndexedCount(status.indexedCount)
      setError(null)
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      const message =
        err instanceof ApiError ? err.message : 'Unable to load AI assistant status.'
      setError(message)
    } finally {
      setLoadingStatus(false)
    }
  }, [enabled])

  useEffect(() => {
    if (!enabled || !open || mode !== 'ai') {
      return undefined
    }

    const controller = new AbortController()
    loadStatus({ signal: controller.signal })
    return () => controller.abort()
  }, [enabled, open, mode, loadStatus])

  const switchMode = useCallback((nextMode) => {
    setMode(nextMode)
    storeMode(nextMode)
    setError(null)
  }, [])

  const askQuestion = useCallback(
    async (question) => {
      const trimmed = question.trim()
      if (!trimmed || asking) {
        return false
      }

      const userMessage = createAiMessage('user', trimmed)
      setAiMessages((prev) => [...prev, userMessage])
      setAsking(true)
      setError(null)

      try {
        const response = await askRag(trimmed)
        const assistantMessage = createAiMessage('assistant', response.answer, {
          sources: response.sources,
        })
        setAiMessages((prev) => [...prev, assistantMessage])
        setConfigured(response.configured)
        setIndexedCount(response.indexedCount)
        return true
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : 'Unable to get an AI answer.'
        setError(message)
        setAiMessages((prev) => [
          ...prev,
          createAiMessage('assistant', `Sorry, I could not answer that. ${message}`),
        ])
        return false
      } finally {
        setAsking(false)
      }
    },
    [asking],
  )

  return {
    mode,
    aiMessages,
    configured,
    indexedCount,
    loadingStatus,
    asking,
    error,
    switchMode,
    askQuestion,
    reloadStatus: loadStatus,
  }
}
