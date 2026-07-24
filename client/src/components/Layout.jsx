export function Layout({
  children,
  user,
  onLogout,
  onAdd,
  chatOpen,
  onToggleChat,
  chatSidebar,
}) {
  return (
    <div className={`app-shell${chatOpen ? ' app-shell--chat-open' : ''}`}>
      <header className="app-header">
        <div className="app-header__brand">
          <div className="app-header__logo" aria-hidden="true">
            V
          </div>
          <div>
            <p className="eyebrow">Work coordination</p>
            <h1>VeloDesk</h1>
            <p className="subtitle">
              Organize work items, monitor progress, and keep delivery moving across your team.
            </p>
          </div>
        </div>
        <div className="app-header__actions">
          <div className="app-header__user">
            {user ? (
              <div className="user-chip" aria-label={`Signed in as ${user.name}`}>
                <span className="user-chip__name">{user.name}</span>
                <span className="user-chip__email">{user.email}</span>
              </div>
            ) : null}
            <button type="button" className="btn btn--ghost" onClick={onLogout}>
              Sign out
            </button>
          </div>
          <button
            type="button"
            className={`btn btn--ghost chat-toggle${chatOpen ? ' chat-toggle--active' : ''}`}
            onClick={onToggleChat}
            aria-expanded={chatOpen}
            aria-controls="team-chat-sidebar"
          >
            {chatOpen ? 'Hide chat' : 'Chat'}
          </button>
          <button type="button" className="btn btn--primary" onClick={onAdd}>
            + New work item
          </button>
        </div>
      </header>
      <div className="app-workspace">
        <main className="app-main">{children}</main>
        <div id="team-chat-sidebar">{chatSidebar}</div>
      </div>
      <footer className="app-footer">
        <p>VeloDesk workspace — collaborate with your team in real time.</p>
      </footer>
    </div>
  )
}
