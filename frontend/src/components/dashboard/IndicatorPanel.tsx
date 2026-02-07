import { useMarketStore } from '@/stores/marketStore'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ReferenceLine,
  BarChart,
  Bar,
  CartesianGrid,
} from 'recharts'

export function IndicatorPanel() {
  const selectedSymbol = useMarketStore((s) => s.selectedSymbol)
  const indicatorData = useMarketStore((s) => (selectedSymbol ? s.indicators[selectedSymbol] : undefined))

  if (!selectedSymbol || !indicatorData) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-12 text-muted-foreground text-sm">
          Select a symbol to view indicators
        </CardContent>
      </Card>
    )
  }

  const { indicators, latest, signals } = indicatorData

  const rsiData = indicators.rsi.map((val, i) => ({ index: i, rsi: val }))

  const macdData = indicators.macd.macd_line.map((val, i) => ({
    index: i,
    macd: val,
    signal: indicators.macd.signal_line[i] ?? 0,
    histogram: indicators.macd.histogram[i] ?? 0,
  }))

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{selectedSymbol} Indicators</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {signals.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {signals.map((s, i) => (
              <Badge
                key={i}
                variant={s.toLowerCase().includes('bullish') || s.toLowerCase().includes('uptrend') || s.toLowerCase().includes('golden') ? 'default' : 'secondary'}
                className="text-xs"
              >
                {s.length > 50 ? s.slice(0, 50) + '...' : s}
              </Badge>
            ))}
          </div>
        )}

        <Tabs defaultValue="rsi">
          <TabsList className="w-full">
            <TabsTrigger value="rsi" className="flex-1">RSI</TabsTrigger>
            <TabsTrigger value="macd" className="flex-1">MACD</TabsTrigger>
            <TabsTrigger value="ma" className="flex-1">MA</TabsTrigger>
          </TabsList>

          <TabsContent value="rsi">
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={rsiData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="index" hide />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: '#888' }} width={35} />
                <Tooltip
                  contentStyle={{ background: '#1a1d2e', border: '1px solid #333', borderRadius: 8 }}
                  labelStyle={{ display: 'none' }}
                />
                <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 4" label={{ value: '70', fill: '#ef4444', fontSize: 10 }} />
                <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 4" label={{ value: '30', fill: '#22c55e', fontSize: 10 }} />
                <Line type="monotone" dataKey="rsi" stroke="#8b5cf6" dot={false} strokeWidth={1.5} />
              </LineChart>
            </ResponsiveContainer>
            <div className="text-xs text-muted-foreground text-center mt-1">
              Current RSI: <span className="text-foreground font-medium">{latest.rsi?.toFixed(1)}</span>
            </div>
          </TabsContent>

          <TabsContent value="macd">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={macdData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="index" hide />
                <YAxis tick={{ fontSize: 11, fill: '#888' }} width={45} />
                <Tooltip
                  contentStyle={{ background: '#1a1d2e', border: '1px solid #333', borderRadius: 8 }}
                  labelStyle={{ display: 'none' }}
                />
                <ReferenceLine y={0} stroke="#555" />
                <Bar dataKey="histogram" fill="#22c55e" radius={[1, 1, 0, 0]} />
                <Line type="monotone" dataKey="macd" stroke="#3b82f6" dot={false} strokeWidth={1.5} />
                <Line type="monotone" dataKey="signal" stroke="#f97316" dot={false} strokeWidth={1.5} />
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>

          <TabsContent value="ma">
            <div className="grid grid-cols-2 gap-3 py-4">
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">SMA 20</div>
                <div className="font-mono text-sm">{latest.sma_20?.toFixed(4)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">SMA 50</div>
                <div className="font-mono text-sm">{latest.sma_50?.toFixed(4)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">EMA 12</div>
                <div className="font-mono text-sm">{latest.ema_12?.toFixed(4)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">EMA 26</div>
                <div className="font-mono text-sm">{latest.ema_26?.toFixed(4)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">Price</div>
                <div className="font-mono text-sm font-bold">{latest.price?.toFixed(4)}</div>
              </div>
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">MACD Histogram</div>
                <div className="font-mono text-sm">{latest.macd_histogram?.toFixed(4)}</div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
