import { useEffect, useRef, useState } from 'react'

function formatTime(value) {
  const date = new Date(value)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export function ChatSidebar({
  open,
  user,
  mode,
  onModeChange,
  messages,
  aiMessages,
  configured,
  indexedCount,
  loading,
  sending,
  asking,
  error,
  onClose,
  onSend,
  onAsk,
}) {
  const [draft, setDraft] = useState('')
  const listRef = useRef(null)
  const isAiMode = mode === 'ai'
  const busy = isAiMode ? asking : sending

  useEffect(() => {
    if (!open || !listRef.current) {
      return
    }
    listRef.current.scrollTop = listRef.current.scrollHeight
  }, [open, messages, aiMessages, loading, mode])

  async function handleSubmit(event) {
    event.preventDefault()
    const sent = isAiMode ? await onAsk(draft) : await onSend(draft)
    if (sent) {
      setDraft('')
    }
  }

  return (
    <>
      <aside
        className={`chat-sidebar${open ? ' chat-sidebar--open' : ''}`}
        aria-label={isAiMode ? 'VeloDesk AI assistant' : 'Team chat'}
        aria-hidden={!open}
      >
        <header className="chat-sidebar__header">
          <div>
            <p className="eyebrow">Workspace</p>
            <h2>{isAiMode ? 'VeloDesk AI' : 'Team chat'}</h2>
          </div>
          <button
            type="button"
            className="chat-sidebar__close"
            onClick={onClose}
            aria-label="Close chat"
          >
            ×
          </button>
        </header>

        <div className="chat-mode-toggle" role="tablist" aria-label="Chat mode">
          <button
            type="button"
            role="tab"
            className={`chat-mode-toggle__btn${mode === 'team' ? ' chat-mode-toggle__btn--active' : ''}`}
            aria-selected={mode === 'team'}
            onClick={() => onModeChange('team')}
          >
            Team
          </button>
          <button
            type="button"
            role="tab"
            className={`chat-mode-toggle__btn${mode === 'ai' ? ' chat-mode-toggle__btn--active' : ''}`}
            aria-selected={mode === 'ai'}
            onClick={() => onModeChange('ai')}
          >
            AI
          </button>
        </div>

        {isAiMode ? (
          <p className="chat-sidebar__status chat-sidebar__status--inline">
            {configured
              ? `Indexed records: ${indexedCount}`
              : 'Set GOOGLE_API_KEY on the server to enable AI answers.'}
          </p>
        ) : null}

        <div className="chat-sidebar__messages" ref={listRef}>
          {isAiMode ? (
            <>
              {loading && !aiMessages.length ? (
                <p className="chat-sidebar__status">Loading assistant…</p>
              ) : null}

              {!loading && !aiMessages.length ? (
                <p className="chat-sidebar__status">
                  Ask about work items, status, owners, or team chat history. Answers use embedded
                  workspace data.
                </p>
              ) : null}

              {aiMessages.map((message) => {
                const isOwn = message.role === 'user'
                return (
                  <article
                    key={message.id}
                    className={`chat-message${isOwn ? ' chat-message--own' : ' chat-message--ai'}`}
                  >
                    <div className="chat-message__meta">
                      <strong>{isOwn ? 'You' : 'VeloDesk AI'}</strong>
                    </div>
                    <p className="chat-message__body">{message.content}</p>
                    {message.sources?.length ? (
                      <ul className="chat-message__sources">
                        {message.sources.slice(0, 3).map((source) => (
                          <li key={`${source.sourceType}-${source.sourceId}`}>
                            {source.sourceType}:{source.sourceId}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </article>
                )
              })}
            </>
          ) : (
            <>
              {loading && !messages.length ? (
                <p className="chat-sidebar__status">Loading messages…</p>
              ) : null}

              {!loading && !messages.length ? (
                <p className="chat-sidebar__status">No messages yet. Say hello to the team.</p>
              ) : null}

              {messages.map((message) => {
                const isOwn = message.userId === user?.id
                return (
                  <article
                    key={message.id}
                    className={`chat-message${isOwn ? ' chat-message--own' : ''}`}
                  >
                    <div className="chat-message__meta">
                      <strong>{isOwn ? 'You' : message.userName}</strong>
                      <time dateTime={message.createdAt}>{formatTime(message.createdAt)}</time>
                    </div>
                    <p className="chat-message__body">{message.content}</p>
                  </article>
                )
              })}
            </>
          )}
        </div>

        {error ? (
          <p className="chat-sidebar__error" role="alert">
            {error}
          </p>
        ) : null}

        <form className="chat-sidebar__composer" onSubmit={handleSubmit}>
          <label className="field">
            <span className="sr-only">{isAiMode ? 'Question' : 'Message'}</span>
            <textarea
              rows={3}
              value={draft}
              placeholder={isAiMode ? 'Ask about your workspace…' : 'Write a message…'}
              onChange={(event) => setDraft(event.target.value)}
              disabled={busy || (isAiMode && !configured)}
            />
          </label>
          <button
            type="submit"
            className="btn btn--primary btn--small"
            disabled={busy || !draft.trim() || (isAiMode && !configured)}
          >
            {busy ? (isAiMode ? 'Thinking…' : 'Sending…') : isAiMode ? 'Ask AI' : 'Send'}
          </button>
        </form>
      </aside>

      {open ? (
        <button
          type="button"
          className="chat-sidebar__backdrop"
          onClick={onClose}
          aria-label="Dismiss chat overlay"
        />
      ) : null}
    </>
  )
}
