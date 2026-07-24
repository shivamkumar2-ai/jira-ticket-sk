import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { ChatSidebar } from './ChatSidebar.jsx'

const user = { id: 'user-1', name: 'Alice', email: 'alice@example.com' }

const messages = [
  {
    id: 'msg-1',
    userId: 'user-2',
    userName: 'Bob',
    content: 'Hey team',
    createdAt: '2026-07-17T10:00:00.000Z',
  },
]

const aiMessages = [
  { id: 'ai-1', role: 'user', content: 'What is in progress?' },
  { id: 'ai-2', role: 'assistant', content: 'VD-24 is in progress.', sources: [] },
]

describe('ChatSidebar', () => {
  it('renders team messages when in team mode', () => {
    render(
      <ChatSidebar
        open
        user={user}
        mode="team"
        onModeChange={() => {}}
        messages={messages}
        aiMessages={[]}
        configured
        indexedCount={3}
        loading={false}
        sending={false}
        asking={false}
        error={null}
        onClose={() => {}}
        onSend={async () => true}
        onAsk={async () => true}
      />,
    )

    expect(screen.getByText('Hey team')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument()
  })

  it('renders AI messages and switches mode', async () => {
    const userEvents = userEvent.setup()
    const onModeChange = vi.fn()

    render(
      <ChatSidebar
        open
        user={user}
        mode="ai"
        onModeChange={onModeChange}
        messages={messages}
        aiMessages={aiMessages}
        configured
        indexedCount={5}
        loading={false}
        sending={false}
        asking={false}
        error={null}
        onClose={() => {}}
        onSend={async () => true}
        onAsk={async () => true}
      />,
    )

    expect(screen.getByText('VD-24 is in progress.')).toBeInTheDocument()
    await userEvents.click(screen.getByRole('tab', { name: /team/i }))
    expect(onModeChange).toHaveBeenCalledWith('team')
  })

  it('asks AI from the composer', async () => {
    const userEvents = userEvent.setup()
    const onAsk = vi.fn(async () => true)

    render(
      <ChatSidebar
        open
        user={user}
        mode="ai"
        onModeChange={() => {}}
        messages={[]}
        aiMessages={[]}
        configured
        indexedCount={2}
        loading={false}
        sending={false}
        asking={false}
        error={null}
        onClose={() => {}}
        onSend={async () => true}
        onAsk={onAsk}
      />,
    )

    await userEvents.type(screen.getByPlaceholderText(/ask about your workspace/i), 'Summarize blockers')
    await userEvents.click(screen.getByRole('button', { name: /ask ai/i }))
    expect(onAsk).toHaveBeenCalledWith('Summarize blockers')
  })
})
