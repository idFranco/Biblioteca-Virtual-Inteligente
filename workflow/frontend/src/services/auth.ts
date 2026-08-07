import { useAuthStore } from '@/stores/authStore'

export interface AuthUser {
  id: string
  fullName: string
  email: string
  roles: string[]
  permissions: string[]
}

export interface AuthResponse {
  accessToken: string
  accessTokenExpiresAt: string
  refreshToken: string
  user: AuthUser
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5002'

async function post<T>(path: string, body: unknown): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  return response.json()
}

function toUser(user: AuthUser) {
  return {
    id: user.id,
    fullName: user.fullName,
    email: user.email,
    roles: user.roles,
    permissions: user.permissions ?? [],
  }
}

function persistAuth(result: AuthResponse) {
  useAuthStore.getState().setAuth(toUser(result.user), {
    accessToken: result.accessToken,
    refreshToken: result.refreshToken,
  })
}

export const authService = {
  async register(fullName: string, email: string, password: string) {
    const result = await post<AuthResponse>('/api/auth/register', {
      fullName,
      email,
      password,
    })
    persistAuth(result)
  },

  async login(email: string, password: string) {
    const result = await post<AuthResponse>('/api/auth/login', {
      email,
      password,
    })
    persistAuth(result)
  },

  async tryRefresh(): Promise<boolean> {
    const { tokens, setAuth } = useAuthStore.getState()
    if (!tokens?.refreshToken) return false
    try {
      const result = await post<AuthResponse>('/api/auth/refresh', {
        refreshToken: tokens.refreshToken,
      })
      setAuth(toUser(result.user), {
        accessToken: result.accessToken,
        refreshToken: result.refreshToken,
      })
      return true
    } catch {
      useAuthStore.getState().logout()
      return false
    }
  },

  async logout() {
    const { tokens } = useAuthStore.getState()
    if (tokens?.refreshToken) {
      try {
        await post<{ revoked: boolean }>('/api/auth/revoke', {
          refreshToken: tokens.refreshToken,
        })
      } catch {
        // Ignored: local logout must succeed regardless of network state.
      }
    }
    useAuthStore.getState().logout()
  },
}