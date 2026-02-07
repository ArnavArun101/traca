import ReactMarkdown from 'react-markdown'
import { cn } from '@/lib/utils'
import type { ChatMessage } from '@/types'

interface MessageBubbleProps {
  message: ChatMessage
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user'

  return (
    <div className={cn('flex', isUser ? 'justify-end' : 'justify-start')}>
      <div
        className={cn(
          'max-w-[85%] rounded-xl px-3.5 py-2 text-sm',
          isUser
            ? 'bg-primary text-primary-foreground'
            : 'bg-secondary text-secondary-foreground'
        )}
      >
        {isUser ? (
          <p className="whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="prose prose-sm prose-invert max-w-none [&>*:first-child]:mt-0 [&>*:last-child]:mb-0">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-secondary rounded-xl px-4 py-3 flex items-center gap-1">
        <div className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
        <div className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
        <div className="typing-dot h-1.5 w-1.5 rounded-full bg-muted-foreground" />
      </div>
    </div>
  )
}
