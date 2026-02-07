import { useState } from 'react'
import { Share2, Copy, Check } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useChatStore } from '@/stores/chatStore'
import type { OutgoingMessage } from '@/types'

interface SocialPanelProps {
  sendMessage: (msg: OutgoingMessage) => void
}

export function SocialPanel({ sendMessage }: SocialPanelProps) {
  const [platform, setPlatform] = useState<'linkedin' | 'x'>('linkedin')
  const [topic, setTopic] = useState('')
  const [copied, setCopied] = useState(false)

  const isLoading = useChatStore((s) => s.isLoading)
  const messages = useChatStore((s) => s.messages)
  const addMessage = useChatStore((s) => s.addMessage)
  const setLoading = useChatStore((s) => s.setLoading)

  const lastDraft = [...messages].reverse().find(
    (m) => m.role === 'assistant'
  )

  const handleGenerate = () => {
    if (!topic.trim()) return
    const id = crypto.randomUUID?.() ?? Math.random().toString(36).slice(2)
    addMessage({
      id,
      role: 'user',
      content: `Generate ${platform} post about: ${topic}`,
      timestamp: Date.now(),
    })
    setLoading(true)
    sendMessage({
      type: 'generate_social',
      topic: topic.trim(),
      platform,
    })
  }

  const handleCopy = async () => {
    if (!lastDraft) return
    await navigator.clipboard.writeText(lastDraft.content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Share2 className="h-4 w-4" />
          Social Content
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex gap-2">
          <Select value={platform} onValueChange={(v) => setPlatform(v as 'linkedin' | 'x')}>
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="linkedin">LinkedIn</SelectItem>
              <SelectItem value="x">X (Twitter)</SelectItem>
            </SelectContent>
          </Select>
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="Topic (e.g., market update)"
            className="flex-1"
            onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
          />
        </div>

        <Button
          className="w-full"
          size="sm"
          onClick={handleGenerate}
          disabled={!topic.trim() || isLoading}
        >
          {isLoading ? 'Generating...' : 'Generate Draft'}
        </Button>

        {lastDraft && (
          <div className="relative rounded-md border bg-secondary/30 p-3">
            <p className="text-sm whitespace-pre-wrap pr-8">{lastDraft.content}</p>
            <Button
              variant="ghost"
              size="icon"
              className="absolute right-1.5 top-1.5 h-7 w-7"
              onClick={handleCopy}
            >
              {copied ? <Check className="h-3.5 w-3.5 text-green-500" /> : <Copy className="h-3.5 w-3.5" />}
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
