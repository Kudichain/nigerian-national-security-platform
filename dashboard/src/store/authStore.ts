import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  username: string
  role: 'admin' | 'analyst' | 'auditor'
  permissions: string[]
}

type AuthState = {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,

      login: async (username: string, password: string) => {
        // In production, call your auth API
        // For demo, simulate authentication
        if (username && password) {
          const mockUser: User = {
            id: '1',
            username,
            role: 'admin',
            permissions: ['view_alerts', 'manage_models', 'admin_settings'],
          }

          set({
            user: mockUser,
            token: 'mock-jwt-token',
            isAuthenticated: true,
          })
        } else {
          throw new Error('Invalid credentials')
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
        })
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)
