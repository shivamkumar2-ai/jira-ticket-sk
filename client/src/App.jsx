import { ErrorBoundary } from './components/ErrorBoundary.jsx'
import { AuthPage } from './components/AuthPage.jsx'
import { Layout } from './components/Layout.jsx'
import { ChatSidebar } from './components/ChatSidebar.jsx'
import { DashboardStats } from './components/DashboardStats.jsx'
import { SearchFilters } from './components/SearchFilters.jsx'
import { ProjectList } from './components/ProjectList.jsx'
import { ProjectForm } from './components/ProjectForm.jsx'
import { ConfirmDialog } from './components/ConfirmDialog.jsx'
import { Toast } from './components/Toast.jsx'
import { useAuth } from './context/AuthContext.jsx'
import { useProjects } from './hooks/useProjects.js'
import { useChat } from './hooks/useChat.js'
import { useRag } from './hooks/useRag.js'

function LoadingState({ message = 'Loading your VeloDesk workspace...' }) {
  return <p className="loading-state">{message}</p>
}

function ErrorState({ message, onRetry }) {
  return (
    <section className="error-state" role="alert">
      <h2>Could not load workspace</h2>
      <p>{message}</p>
      <button type="button" className="btn btn--primary" onClick={onRetry}>
        Retry
      </button>
    </section>
  )
}

function AppContent() {
  const { user, logout } = useAuth()
  const {
    stats,
    filteredProjects,
    workspaceUsers,
    filters,
    loading,
    listLoading,
    error,
    toast,
    showForm,
    editingProject,
    deleteTarget,
    updateFilter,
    toggleUserFilter,
    clearFilters,
    openCreateForm,
    openEditForm,
    closeForm,
    saveProject,
    confirmDelete,
    cancelDelete,
    deleteProject,
    dismissToast,
    retryLoad,
  } = useProjects(user)

  const {
    open: chatOpen,
    messages: chatMessages,
    loading: chatLoading,
    sending: chatSending,
    error: chatError,
    toggleChat,
    closeChat,
    sendMessage,
  } = useChat(user)

  const {
    mode: chatMode,
    aiMessages,
    configured: ragConfigured,
    indexedCount: ragIndexedCount,
    loadingStatus: ragLoading,
    asking: ragAsking,
    error: ragError,
    switchMode,
    askQuestion,
  } = useRag({ open: chatOpen })

  if (loading) return <LoadingState />
  if (error) return <ErrorState message={error} onRetry={retryLoad} />

  return (
    <Layout
      user={user}
      onLogout={logout}
      onAdd={openCreateForm}
      chatOpen={chatOpen}
      onToggleChat={toggleChat}
      chatSidebar={
        <ChatSidebar
          open={chatOpen}
          user={user}
          mode={chatMode}
          onModeChange={switchMode}
          messages={chatMessages}
          aiMessages={aiMessages}
          configured={ragConfigured}
          indexedCount={ragIndexedCount}
          loading={chatMode === 'ai' ? ragLoading : chatLoading}
          sending={chatSending}
          asking={ragAsking}
          error={chatMode === 'ai' ? ragError : chatError}
          onClose={closeChat}
          onSend={sendMessage}
          onAsk={askQuestion}
        />
      }
    >
      <DashboardStats stats={stats} />
      <SearchFilters
        filters={filters}
        users={workspaceUsers}
        onChange={updateFilter}
        onToggleUser={toggleUserFilter}
        onClear={clearFilters}
        resultCount={filteredProjects.length}
        loading={listLoading}
      />
      <ProjectList
        projects={filteredProjects}
        currentUserId={user.id}
        onEdit={openEditForm}
        onDelete={confirmDelete}
      />

      {showForm ? (
        <ProjectForm project={editingProject} onSave={saveProject} onCancel={closeForm} />
      ) : null}

      {deleteTarget ? (
        <ConfirmDialog
          title="Delete work item?"
          message={`"${deleteTarget.title}" will be removed from your workspace.`}
          confirmLabel="Delete"
          onConfirm={deleteProject}
          onCancel={cancelDelete}
        />
      ) : null}

      <Toast toast={toast} onDismiss={dismissToast} />
    </Layout>
  )
}

export default function App() {
  const { isAuthenticated, initializing } = useAuth()

  if (initializing) {
    return <LoadingState message="Checking your session..." />
  }

  if (!isAuthenticated) {
    return (
      <ErrorBoundary>
        <AuthPage />
      </ErrorBoundary>
    )
  }

  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  )
}
