import { create } from 'zustand'
import type { User, AuthTokens } from '@/types'

const STORAGE_KEY = 'biblioteca.auth'

interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  setAuth: (user: User, tokens: AuthTokens) => void
  logout: () => void
}

function loadPersisted(): Pick<AuthState, 'user' | 'tokens' | 'isAuthenticated'> {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return { user: null, tokens: null, isAuthenticated: false }
    const parsed = JSON.parse(raw) as Pick<AuthState, 'user' | 'tokens'>
    return { ...parsed, isAuthenticated: Boolean(parsed.tokens?.accessToken) }
  } catch {
    return { user: null, tokens: null, isAuthenticated: false }
  }
}

const persisted = loadPersisted()

export const useAuthStore = create<AuthState>((set) => ({
  ...persisted,
  setAuth: (user, tokens) => {
    const state = { user, tokens, isAuthenticated: true }
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state))
    set(state)
  },
  logout: () => {
    sessionStorage.removeItem(STORAGE_KEY)
    set({ user: null, tokens: null, isAuthenticated: false })
  },
}))