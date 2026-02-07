import { create } from 'zustand'
import type { PriceAlert, PriceAlertTriggeredResponse } from '@/types'

interface AlertState {
  alerts: PriceAlert[]
  triggeredAlert: PriceAlertTriggeredResponse | null
  setAlerts: (alerts: PriceAlert[]) => void
  addAlert: (alert: PriceAlert) => void
  removeAlert: (alertId: number) => void
  setTriggeredAlert: (alert: PriceAlertTriggeredResponse | null) => void
}

export const useAlertStore = create<AlertState>((set) => ({
  alerts: [],
  triggeredAlert: null,

  setAlerts: (alerts) => set({ alerts }),

  addAlert: (alert) =>
    set((state) => ({
      alerts: [...state.alerts, alert],
    })),

  removeAlert: (alertId) =>
    set((state) => ({
      alerts: state.alerts.filter((a) => a.alert_id !== alertId),
    })),

  setTriggeredAlert: (alert) => set({ triggeredAlert: alert }),
}))
