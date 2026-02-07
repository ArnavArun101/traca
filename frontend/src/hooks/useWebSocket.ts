import { useEffect, useRef, useCallback, useState } from 'react'
import type { OutgoingMessage, IncomingMessage } from '@/types'
import { useMarketStore } from '@/stores/marketStore'
import { useChatStore } from '@/stores/chatStore'
import { useBehavioralStore } from '@/stores/behavioralStore'
import { useAlertStore } from '@/stores/alertStore'

function generateId(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID()
  }
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null)
  const sessionIdRef = useRef(generateId())
  const reconnectAttempt = useRef(0)
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const [connected, setConnected] = useState(false)

  const dispatch = useCallback((msg: IncomingMessage) => {
    switch (msg.type) {
      case 'asset_list':
        useMarketStore.getState().setAssets(msg.data)
        break
      case 'latest_prices':
        for (const [symbol, price] of Object.entries(msg.data)) {
          useMarketStore.getState().updatePrice(symbol, price)
        }
        break
      case 'price_update':
        useMarketStore.getState().updatePrice(msg.symbol, msg.price)
        break
      case 'candles_history':
      case 'history_data':
      case 'stored_history': {
        const candles = msg.type === 'candles_history' ? msg.data : msg.candles
        useMarketStore.getState().setCandles(msg.symbol, candles)
        break
      }
      case 'indicator_result':
        useMarketStore.getState().setIndicators(msg.symbol, msg.data)
        break
      case 'chat_response':
        useChatStore.getState().addMessage({
          id: generateId(),
          role: 'assistant',
          content: msg.text,
          timestamp: Date.now(),
        })
        useChatStore.getState().setLoading(false)
        break
      case 'market_explanation':
      case 'market_answer':
        useChatStore.getState().addMessage({
          id: generateId(),
          role: 'assistant',
          content: msg.text,
          timestamp: Date.now(),
        })
        useChatStore.getState().setLoading(false)
        break
      case 'news_summary':
        useChatStore.getState().addMessage({
          id: generateId(),
          role: 'assistant',
          content: msg.text,
          timestamp: Date.now(),
        })
        useChatStore.getState().setLoading(false)
        break
      case 'behavioral_report':
        useBehavioralStore.getState().setReport(msg.data)
        break
      case 'nudges':
        for (const nudge of msg.data) {
          useBehavioralStore.getState().addNudge(nudge)
        }
        break
      case 'social_draft':
        useChatStore.getState().addMessage({
          id: generateId(),
          role: 'assistant',
          content: msg.text,
          timestamp: Date.now(),
        })
        useChatStore.getState().setLoading(false)
        break
      case 'alert_created': {
        const store = useAlertStore.getState()
        store.addAlert({
          alert_id: msg.data.alert_id,
          symbol: msg.data.symbol,
          target_price: msg.data.target_price,
          direction: msg.data.direction as 'above' | 'below',
          is_active: true,
          created_at: Date.now() / 1000,
          triggered_at: null,
        })
        break
      }
      case 'alert_list':
        useAlertStore.getState().setAlerts(msg.data)
        break
      case 'alert_cancelled':
        useAlertStore.getState().removeAlert(msg.data.alert_id)
        break
      case 'price_alert_triggered':
        useAlertStore.getState().setTriggeredAlert(msg)
        break
      case 'info':
      case 'error':
        break
    }
  }, [])

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const envUrl = (import.meta.env.VITE_WS_URL as string | undefined)?.trim()
    let url: string
    const token = localStorage.getItem('traca_token')
    if (!token) {
      setConnected(false)
      reconnectTimer.current = setTimeout(connect, 1000)
      return
    }
    const tokenQuery = token ? `?token=${encodeURIComponent(token)}` : ''

    if (envUrl) {
      let base = envUrl.replace(/\/$/, '')
      if (base.startsWith('http://')) base = base.replace('http://', 'ws://')
      if (base.startsWith('https://')) base = base.replace('https://', 'wss://')
      url = `${base}/ws/${sessionIdRef.current}${tokenQuery}`
    } else {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const host = window.location.host
      url = `${protocol}//${host}/ws/${sessionIdRef.current}${tokenQuery}`
    }

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      reconnectAttempt.current = 0
    }

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data) as IncomingMessage
        dispatch(msg)
      } catch {
        // ignore malformed messages
      }
    }

    ws.onclose = () => {
      setConnected(false)
      const delay = Math.min(1000 * 2 ** reconnectAttempt.current, 30000)
      reconnectAttempt.current += 1
      reconnectTimer.current = setTimeout(connect, delay)
    }

    ws.onerror = () => {
      ws.close()
    }
  }, [dispatch])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimer.current)
      wsRef.current?.close()
    }
  }, [connect])

  const sendMessage = useCallback((msg: OutgoingMessage) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(msg))
    }
  }, [])

  return { connected, sendMessage, sessionId: sessionIdRef.current }
}
