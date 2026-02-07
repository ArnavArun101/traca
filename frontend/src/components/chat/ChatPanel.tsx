import { useEffect, useRef } from 'react'
import { MessageSquare } from 'lucide-react'
import { useChatStore } from '@/stores/chatStore'
import { useMarketStore } from '@/stores/marketStore'
import { MessageBubble, TypingIndicator } from './MessageBubble'
import { ChatInput } from './ChatInput'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import type { OutgoingMessage } from '@/types'

interface ChatPanelProps {
  sendMessage: (msg: OutgoingMessage) => void
}

export function ChatPanel({ sendMessage }: ChatPanelProps) {
  const messages = useChatStore((s) => s.messages)
  const isLoading = useChatStore((s) => s.isLoading)
  const addMessage = useChatStore((s) => s.addMessage)
  const setLoading = useChatStore((s) => s.setLoading)
  const selectedSymbol = useMarketStore((s) => s.selectedSymbol)

  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const handleSend = (text: string) => {
    const id = crypto.randomUUID?.() ?? Math.random().toString(36).slice(2)
    addMessage({
      id,
      role: 'user',
      content: text,
      timestamp: Date.now(),
    })
    setLoading(true)
    sendMessage({ type: 'chat', message: text })
  }

  const handleQuickAction = (action: string) => {
    if (action === 'explain' && selectedSymbol) {
      const id = crypto.randomUUID?.() ?? Math.random().toString(36).slice(2)
      addMessage({
        id,
        role: 'user',
        content: `Explain ${selectedSymbol}`,
        timestamp: Date.now(),
      })
      setLoading(true)
      sendMessage({ type: 'explain', symbol: selectedSymbol })
    } else if (action === 'summary') {
      const id = crypto.randomUUID?.() ?? Math.random().toString(36).slice(2)
      addMessage({
        id,
        role: 'user',
        content: 'Give me a market summary',
        timestamp: Date.now(),
      })
      setLoading(true)
      sendMessage({ type: 'chat', message: 'Give me a brief market summary and trading outlook for today.' })
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center gap-2 border-b px-4 py-3">
        <MessageSquare className="h-4 w-4 text-primary" />
        <span className="text-sm font-semibold">Chat</span>
      </div>

      <ScrollArea className="flex-1 p-4">
        <div className="space-y-3">
          {messages.length === 0 && (
            <div className="text-center text-muted-foreground text-sm py-12 space-y-3">
              <MessageSquare className="h-10 w-10 mx-auto opacity-30" />
              <p>Ask anything about markets or trading</p>
              <div className="flex justify-center gap-2 flex-wrap">
                {selectedSymbol && (
                  <Button variant="outline" size="sm" onClick={() => handleQuickAction('explain')}>
                    Explain {selectedSymbol}
                  </Button>
                )}
                <Button variant="outline" size="sm" onClick={() => handleQuickAction('summary')}>
                  Market Summary
                </Button>
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))}

          {isLoading && <TypingIndicator />}

          <div ref={bottomRef} />
        </div>
      </ScrollArea>

      <ChatInput onSend={handleSend} disabled={isLoading} />
    </div>
  )
}
