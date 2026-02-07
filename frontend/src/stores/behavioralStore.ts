import { create } from 'zustand'
import type { BehavioralReport, Nudge } from '@/types'

interface BehavioralState {
  report: BehavioralReport | null
  nudges: Nudge[]
  setReport: (report: BehavioralReport) => void
  addNudge: (nudge: Nudge) => void
  dismissNudge: (id: string) => void
}

export const useBehavioralStore = create<BehavioralState>((set) => ({
  report: null,
  nudges: [],

  setReport: (report) => set({ report }),

  addNudge: (nudge) =>
    set((state) => ({
      nudges: state.nudges.some((n) => n.id === nudge.id)
        ? state.nudges
        : [...state.nudges, nudge],
    })),

  dismissNudge: (id) =>
    set((state) => ({
      nudges: state.nudges.filter((n) => n.id !== id),
    })),
}))
