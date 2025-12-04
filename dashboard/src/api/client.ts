import axios, {
  AxiosError,
  AxiosResponse,
  InternalAxiosRequestConfig,
} from 'axios'
import { useAuthStore } from '../store/authStore'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// Add auth token to requests
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
    }
    return Promise.reject(error)
  }
)

type JsonRecord = Record<string, unknown>

export const alertsApi = {
  getAlerts: (params?: { domain?: string; severity?: string; status?: string }) =>
    api.get('/alerts', { params }),
  
  getAlertById: (id: string) =>
    api.get(`/alerts/${id}`),
  
  updateAlertStatus: (id: string, status: string) =>
    api.patch(`/alerts/${id}`, { status }),
}

export const nidsApi = {
  score: (data: JsonRecord) => api.post('/nids/score', data),
  health: () => api.get('/nids/health'),
  metrics: () => api.get('/nids/metrics'),
}

export const phishingApi = {
  score: (data: JsonRecord) => api.post('/phishing/score', data),
  health: () => api.get('/phishing/health'),
}

export const authApi = {
  score: (data: JsonRecord) => api.post('/auth/score', data),
  health: () => api.get('/auth/health'),
}

export const insightsApi = {
  getStats: (domain: string, timeRange: string) =>
    api.get(`/insights/${domain}/stats`, { params: { timeRange } }),
  
  getTrends: (domain: string) =>
    api.get(`/insights/${domain}/trends`),
}

export const modelsApi = {
  list: () => api.get('/models'),
  train: (domain: string, config: JsonRecord) => api.post(`/models/${domain}/train`, config),
  deploy: (domain: string, version: string) => api.post(`/models/${domain}/deploy`, { version }),
}

// New API client for government services
const API_BASE = 'http://localhost:8000'

export const agencyApi = {
  // INEC
  getInecHealth: async () => {
    const response = await fetch(`${API_BASE}/api/v1/inec/health`)
    return response.json()
  },

  // Fire Service
  getFireHealth: async () => {
    const response = await fetch(`${API_BASE}/api/v1/fire/health`)
    return response.json()
  },

  // Police
  getPoliceHealth: async () => {
    const response = await fetch(`${API_BASE}/api/v1/police/health`)
    return response.json()
  },

  // Social Media
  getSocialHealth: async () => {
    const response = await fetch(`${API_BASE}/api/v1/social/health`)
    return response.json()
  },

  // Gateway
  getGatewayMetrics: async () => {
    const response = await fetch(`${API_BASE}/api/v1/gateway/metrics`)
    return response.json()
  },

  // Pilot
  getPilotStatus: async () => {
    const response = await fetch(`${API_BASE}/api/v1/pilot/status`)
    return response.json()
  },
}

export default api

