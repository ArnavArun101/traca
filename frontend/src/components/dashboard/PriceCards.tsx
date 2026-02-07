import { useEffect, useRef } from 'react'
import { Card, CardContent } from '@/components/ui/card'
import { useMarketStore } from '@/stores/marketStore'
import { cn } from '@/lib/utils'
import type { OutgoingMessage } from '@/types'

interface PriceCardsProps {
  sendMessage: (msg: OutgoingMessage) => void
}

export function PriceCards({ sendMessage }: PriceCardsProps) {
  const prices = useMarketStore((s) => s.prices)
  const prevPrices = useMarketStore((s) => s.prevPrices)
  const selectedSymbol = useMarketStore((s) => s.selectedSymbol)
  const setSelectedSymbol = useMarketStore((s) => s.setSelectedSymbol)

  const flashRef = useRef<Record<string, 'up' | 'down' | null>>({})

  useEffect(() => {
    for (const [symbol, price] of Object.entries(prices)) {
      const prev = prevPrices[symbol]
      if (prev !== undefined && prev !== price) {
        flashRef.current[symbol] = price > prev ? 'up' : 'down'
        setTimeout(() => {
          flashRef.current[symbol] = null
        }, 600)
      }
    }
  }, [prices, prevPrices])

  const symbols = Object.keys(prices)

  if (symbols.length === 0) {
    return (
      <div className="flex items-center justify-center py-8 text-muted-foreground text-sm">
        Select an asset group to see live prices
      </div>
    )
  }

  const handleClick = (symbol: string) => {
    setSelectedSymbol(symbol)
    sendMessage({ type: 'candles_history', symbol, limit: 100 })
    sendMessage({ type: 'indicators', symbol, limit: 100 })
  }

  return (
    <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
      {symbols.map((symbol) => {
        const price = prices[symbol]
        const prev = prevPrices[symbol] ?? price
        const isUp = price > prev
        const isSelected = selectedSymbol === symbol

        return (
          <Card
            key={symbol}
            className={cn(
              'cursor-pointer transition-colors hover:bg-accent/50',
              isSelected && 'ring-1 ring-primary',
              flashRef.current[symbol] === 'up' && 'flash-green',
              flashRef.current[symbol] === 'down' && 'flash-red'
            )}
            onClick={() => handleClick(symbol)}
          >
            <CardContent className="p-3">
              <div className="text-xs text-muted-foreground font-medium">{symbol}</div>
              <div className={cn(
                'text-lg font-mono font-bold tabular-nums',
                isUp ? 'text-green-500' : price < prev ? 'text-red-500' : 'text-foreground'
              )}>
                {price?.toFixed(symbol.startsWith('cry') ? 2 : 4)}
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
