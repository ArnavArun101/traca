import { create } from 'zustand'
import type { Candle, IndicatorData } from '@/types'

interface MarketState {
  prices: Record<string, number>
  prevPrices: Record<string, number>
  candles: Record<string, Candle[]>
  assets: Record<string, string[]>
  indicators: Record<string, IndicatorData>
  selectedSymbol: string | null
  updatePrice: (symbol: string, price: number) => void
  setCandles: (symbol: string, candles: Candle[]) => void
  setAssets: (assets: Record<string, string[]>) => void
  setIndicators: (symbol: string, data: IndicatorData) => void
  setSelectedSymbol: (symbol: string) => void
}

export const useMarketStore = create<MarketState>((set) => ({
  prices: {},
  prevPrices: {},
  candles: {},
  assets: {},
  indicators: {},
  selectedSymbol: null,

  updatePrice: (symbol, price) =>
    set((state) => ({
      prevPrices: { ...state.prevPrices, [symbol]: state.prices[symbol] ?? price },
      prices: { ...state.prices, [symbol]: price },
    })),

  setCandles: (symbol, candles) =>
    set((state) => ({
      candles: { ...state.candles, [symbol]: candles },
    })),

  setAssets: (assets) => set({ assets }),

  setIndicators: (symbol, data) =>
    set((state) => ({
      indicators: { ...state.indicators, [symbol]: data },
    })),

  setSelectedSymbol: (symbol) => set({ selectedSymbol: symbol }),
}))
