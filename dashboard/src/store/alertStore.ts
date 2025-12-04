import { create } from 'zustand'

export interface Alert {
  id: string
  timestamp: string
  domain: 'nids' | 'logs' | 'phishing' | 'auth' | 'malware'
  severity: 'low' | 'medium' | 'high' | 'critical'
  title: string
  description: string
  score: number
  confidence?: number
  action?: string
  affectedAssets?: string[]
  status: 'new' | 'investigating' | 'resolved' | 'false_positive'
  source_ip?: string
}

interface AlertState {
  alerts: Alert[]
  connected: boolean
  loading: boolean
  error: string | null
  addAlert: (alert: Alert) => void
  updateAlert: (id: string, updates: Partial<Alert>) => void
  fetchAlerts: () => Promise<void>
  connectWebSocket: () => void
  disconnectWebSocket: () => void
}

const API_BASE = 'http://localhost:8000'
let alertRefreshInterval: ReturnType<typeof setInterval> | undefined

export const useAlertStore = create<AlertState>((set, get) => ({
  alerts: [],
  connected: false,
  loading: false,
  error: null,

  addAlert: (alert: Alert) => {
    set((state) => ({
      alerts: [alert, ...state.alerts].slice(0, 1000), // Keep last 1000
    }))
  },

  updateAlert: (id: string, updates: Partial<Alert>) => {
    set((state) => ({
      alerts: state.alerts.map((alert: Alert) =>
        alert.id === id ? { ...alert, ...updates } : alert
      ),
    }))
  },

  fetchAlerts: async () => {
    set({ loading: true, error: null })
    try {
      const response = await fetch(`${API_BASE}/api/v1/alerts`)
      if (!response.ok) throw new Error('Failed to fetch alerts')
      const data = await response.json()
      set({ alerts: data.alerts, loading: false, connected: true })
    } catch (error) {
      console.error('Error fetching alerts:', error)
      // Use mock data if API unavailable
      set({
        alerts: generateMockAlerts(),
        loading: false,
        error: 'Using mock data - start API server with: python services/mock_api.py',
        connected: false
      })
    }
  },

  connectWebSocket: () => {
    set({ connected: true })
    // Fetch initial data
    get().fetchAlerts()
    // Poll every 10 seconds
    const interval = setInterval(() => {
      get().fetchAlerts()
    }, 10000)
    // Store interval for cleanup
    alertRefreshInterval = interval
  },

  disconnectWebSocket: () => {
    set({ connected: false })
    if (alertRefreshInterval) {
      clearInterval(alertRefreshInterval)
      alertRefreshInterval = undefined
    }
  },
}))

// Mock data generator for offline development
function generateMockAlerts(): Alert[] {
  const domains: Alert['domain'][] = ['nids', 'phishing', 'logs', 'malware', 'auth']
  const severities: Alert['severity'][] = ['critical', 'high', 'medium', 'low']
  const statuses: Alert['status'][] = ['new', 'investigating', 'resolved']

  return Array.from({ length: 50 }, (_, i) => {
    const domain = domains[Math.floor(Math.random() * domains.length)]
    const severity = severities[Math.floor(Math.random() * severities.length)]
    const status = statuses[Math.floor(Math.random() * statuses.length)]

    return {
      id: `alert-${i + 1000}`,
      domain,
      severity,
      status,
      title: `${domain.toUpperCase()} Alert: ${severity} threat detected`,
      description: `Detected suspicious ${domain} activity requiring investigation`,
      timestamp: new Date(Date.now() - Math.random() * 72 * 60 * 60 * 1000).toISOString(),
      score: Math.random() * 0.4 + 0.6,
      source_ip: `192.168.${Math.floor(Math.random() * 254) + 1}.${Math.floor(Math.random() * 254) + 1}`,
    }
  }).sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
}

