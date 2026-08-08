import { useAuthStore } from '@/stores/authStore'
import { authService } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:5002'
const UNAUTHORIZED = 401

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const { tokens } = useAuthStore.getState()

  const headers = new Headers(init.headers)
  headers.set('Content-Type', 'application/json')
  if (tokens?.accessToken) {
    headers.set('Authorization', `Bearer ${tokens.accessToken}`)
  }

  let response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })

  if (response.status === UNAUTHORIZED) {
    const refreshed = await authService.tryRefresh()
    if (refreshed) {
      const { accessToken } = useAuthStore.getState().tokens!
      headers.set('Authorization', `Bearer ${accessToken}`)
      response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers })
    }
  }

  if (!response.ok) {
    let message = `API error: ${response.status}`
    try {
      const problem = (await response.json()) as { detail?: string; title?: string }
      if (problem.detail) message = problem.detail
      else if (problem.title) message = `${problem.title} (${response.status})`
    } catch {
      // keep the default message if the body is not JSON
    }
    throw new Error(message)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return response.json()
}

export async function apiGet<T>(path: string): Promise<T> {
  return request<T>(path)
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  })
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  })
}

export async function apiDelete<T>(path: string): Promise<T> {
  return request<T>(path, {
    method: 'DELETE',
  })
}