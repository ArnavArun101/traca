import { Activity } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { OutgoingMessage } from '@/types'

interface HeaderProps {
  connected: boolean
  sendMessage: (msg: OutgoingMessage) => void
}

export function Header({ connected, sendMessage }: HeaderProps) {
  const handleGroupChange = (group: string) => {
    sendMessage({ type: 'subscribe_group', group: group as 'synthetic' | 'forex' | 'crypto' })
  }

  return (
    <header className="flex h-14 items-center justify-between border-b px-4">
      <div className="flex items-center gap-3">
        <Activity className="h-5 w-5 text-primary" />
        <h1 className="text-lg font-bold tracking-tight">traca</h1>
      </div>

      <div className="flex items-center gap-4">
        <Select onValueChange={handleGroupChange}>
          <SelectTrigger className="w-[140px]">
            <SelectValue placeholder="Asset group" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="synthetic">Synthetic</SelectItem>
            <SelectItem value="forex">Forex</SelectItem>
            <SelectItem value="crypto">Crypto</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <div
            className={cn(
              'h-2 w-2 rounded-full',
              connected ? 'bg-green-500' : 'bg-red-500'
            )}
          />
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>
    </header>
  )
}
