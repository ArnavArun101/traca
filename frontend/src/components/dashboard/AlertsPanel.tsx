import { useState } from 'react'
import { Bell, X, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useAlertStore } from '@/stores/alertStore'
import { useMarketStore } from '@/stores/marketStore'
import type { OutgoingMessage } from '@/types'

interface AlertsPanelProps {
  sendMessage: (msg: OutgoingMessage) => void
}

export function AlertsPanel({ sendMessage }: AlertsPanelProps) {
  const alerts = useAlertStore((s) => s.alerts)
  const triggeredAlert = useAlertStore((s) => s.triggeredAlert)
  const setTriggeredAlert = useAlertStore((s) => s.setTriggeredAlert)
  const prices = useMarketStore((s) => s.prices)

  const [symbol, setSymbol] = useState('')
  const [targetPrice, setTargetPrice] = useState('')
  const [direction, setDirection] = useState<'above' | 'below'>('above')

  const symbols = Object.keys(prices)

  const handleCreate = () => {
    if (!symbol || !targetPrice) return
    sendMessage({
      type: 'create_alert',
      symbol,
      target_price: parseFloat(targetPrice),
      direction,
    })
    setTargetPrice('')
  }

  const handleCancel = (alertId: number) => {
    sendMessage({ type: 'cancel_alert', alert_id: alertId })
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm flex items-center gap-2">
          <Bell className="h-4 w-4" />
          Price Alerts
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {triggeredAlert && (
          <div className="flex items-center justify-between rounded-md bg-primary/10 border border-primary/30 p-2 text-sm">
            <span>{triggeredAlert.message}</span>
            <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setTriggeredAlert(null)}>
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}

        <div className="flex gap-2">
          <Select value={symbol} onValueChange={setSymbol}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Symbol" />
            </SelectTrigger>
            <SelectContent>
              {symbols.map((s) => (
                <SelectItem key={s} value={s}>{s}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Input
            type="number"
            placeholder="Target price"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
            className="w-[110px]"
          />
          <Select value={direction} onValueChange={(v) => setDirection(v as 'above' | 'below')}>
            <SelectTrigger className="w-[90px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="above">Above</SelectItem>
              <SelectItem value="below">Below</SelectItem>
            </SelectContent>
          </Select>
          <Button size="sm" onClick={handleCreate}>Set</Button>
        </div>

        {alerts.filter((a) => a.is_active).length === 0 ? (
          <div className="text-xs text-muted-foreground text-center py-3">No active alerts</div>
        ) : (
          <div className="space-y-1.5">
            {alerts
              .filter((a) => a.is_active)
              .map((alert) => (
                <div
                  key={alert.alert_id}
                  className="flex items-center justify-between rounded-md bg-secondary/50 px-3 py-2 text-sm"
                >
                  <div className="flex items-center gap-2">
                    {alert.direction === 'above' ? (
                      <TrendingUp className="h-3.5 w-3.5 text-green-500" />
                    ) : (
                      <TrendingDown className="h-3.5 w-3.5 text-red-500" />
                    )}
                    <span className="font-medium">{alert.symbol}</span>
                    <Badge variant="outline" className="text-xs">
                      {alert.direction} {alert.target_price}
                    </Badge>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-6 w-6"
                    onClick={() => handleCancel(alert.alert_id)}
                  >
                    <X className="h-3 w-3" />
                  </Button>
                </div>
              ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
