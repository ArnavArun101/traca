import { useEffect, useRef } from 'react'
import { createChart, CandlestickSeries, type IChartApi, type ISeriesApi, type CandlestickData, type Time } from 'lightweight-charts'
import { useMarketStore } from '@/stores/marketStore'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

export function CandlestickChart() {
  const selectedSymbol = useMarketStore((s) => s.selectedSymbol)
  const candles = useMarketStore((s) => (selectedSymbol ? s.candles[selectedSymbol] : undefined))
  const currentPrice = useMarketStore((s) => (selectedSymbol ? s.prices[selectedSymbol] : undefined))

  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: 'transparent' },
        textColor: '#999',
      },
      grid: {
        vertLines: { color: 'rgba(255,255,255,0.04)' },
        horzLines: { color: 'rgba(255,255,255,0.04)' },
      },
      width: chartContainerRef.current.clientWidth,
      height: 350,
      crosshair: {
        mode: 0,
      },
      timeScale: {
        timeVisible: true,
        borderColor: 'rgba(255,255,255,0.1)',
      },
      rightPriceScale: {
        borderColor: 'rgba(255,255,255,0.1)',
      },
    })

    const series = chart.addSeries(CandlestickSeries, {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderDownColor: '#ef4444',
      borderUpColor: '#22c55e',
      wickDownColor: '#ef4444',
      wickUpColor: '#22c55e',
    })

    chartRef.current = chart
    seriesRef.current = series

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth })
      }
    }

    const ro = new ResizeObserver(handleResize)
    ro.observe(chartContainerRef.current)

    return () => {
      ro.disconnect()
      chart.remove()
      chartRef.current = null
      seriesRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!seriesRef.current || !candles?.length) return

    const data: CandlestickData<Time>[] = candles.map((c) => ({
      time: c.epoch as Time,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
    }))

    seriesRef.current.setData(data)
    chartRef.current?.timeScale().fitContent()
  }, [candles])

  useEffect(() => {
    if (!seriesRef.current || !currentPrice || !candles?.length) return

    const last = candles[candles.length - 1]
    if (!last) return

    seriesRef.current.update({
      time: last.epoch as Time,
      open: last.open,
      high: Math.max(last.high, currentPrice),
      low: Math.min(last.low, currentPrice),
      close: currentPrice,
    })
  }, [currentPrice, candles])

  if (!selectedSymbol) {
    return (
      <Card>
        <CardContent className="flex items-center justify-center py-16 text-muted-foreground text-sm">
          Click a price card to view chart
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">{selectedSymbol} Chart</CardTitle>
      </CardHeader>
      <CardContent className="p-2">
        <div ref={chartContainerRef} />
      </CardContent>
    </Card>
  )
}
