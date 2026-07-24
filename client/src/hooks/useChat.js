import { useCallback, useEffect, useRef, useState } from 'react'
import { ApiError } from '../api/client.js'
import { fetchChatMessages, sendChatMessage } from '../api/chat.js'

const CHAT_OPEN_KEY = 'velodesk-chat-open'
const POLL_INTERVAL_MS = 5000

function readStoredOpenState() {
  try {
    return localStorage.getItem(CHAT_OPEN_KEY) === 'true'
  } catch {
    return false
  }
}

function storeOpenState(open) {
  try {
    localStorage.setItem(CHAT_OPEN_KEY, String(open))
  } catch {
    // ignore storage errors
  }
}

export function useChat(currentUser, { enabled = true } = {}) {
  const [open, setOpen] = useState(readStoredOpenState)
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [error, setError] = useState(null)
  const hasLoadedRef = useRef(false)

  const loadMessages = useCallback(async (options = {}) => {
    if (!enabled) {
      return
    }

    const { silent = false } = options
    if (!silent) {
      setLoading(true)
    }

    try {
      const items = await fetchChatMessages(options)
      if (items.length !== messages.length) {
        setMessages(items)
      }
      setError(null)
      hasLoadedRef.current = true
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      const message =
        err instanceof ApiError ? err.message : 'Unable to load chat messages.'
      setError(message)
    } finally {
      if (!silent) {
        setLoading(false)
      }
    }
  }, [enabled])

  useEffect(() => {
    if (!enabled || !open) {
      return undefined
    }

    const controller = new AbortController()
    loadMessages({ signal: controller.signal })

    const timer = setInterval(() => {
      loadMessages({ signal: controller.signal, silent: true })
    }, POLL_INTERVAL_MS)

    return () => {
      controller.abort()
      clearInterval(timer)
    }
  }, [enabled, open, loadMessages])

  const toggleChat = useCallback(() => {
    setOpen((prev) => {
      const next = !prev
      storeOpenState(next)
      return next
    })
  }, [])

  const closeChat = useCallback(() => {
    setOpen(false)
    storeOpenState(false)
  }, [])

  const sendMessage = useCallback(
    async (content) => {
      const trimmed = content.trim()
      if (!trimmed || sending) {
        return false
      }

      setSending(true)
      try {
        const message = await sendChatMessage(trimmed)
        setMessages((prev) => [...prev, message])
        setError(null)
        return true
      } catch (err) {
        const message =
          err instanceof ApiError ? err.message : 'Unable to send message.'
        setError(message)
        return false
      } finally {
        setSending(false)
      }
    },
    [sending],
  )

  return {
    open,
    messages,
    loading,
    sending,
    error,
    currentUserId: currentUser?.id,
    toggleChat,
    closeChat,
    sendMessage,
    reloadMessages: loadMessages,
  }
}
