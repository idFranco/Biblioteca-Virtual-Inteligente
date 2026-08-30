import { CHATBOT_API_BASE_URL } from '@/config/env'
import { useAuthStore } from '@/stores/authStore'

export interface BookRequestOfferMetadata {
  title: string
  author: string
  isbn?: string | null
  genre?: string | null
  description?: string | null
  openLibraryKey?: string | null
}

export interface ChatActionOffer {
  type: 'book_request'
  metadata: BookRequestOfferMetadata
}

export interface BookRecommendation {
  id?: string | null
  title: string
  author?: string | null
  genre?: string | null
  isbn?: string | null
  openLibraryKey?: string | null
  coverUrl?: string | null
  availableCopies: number
  available: boolean
  reason?: string | null
  source?: 'catalog' | 'open_library' | null
  openLibraryVerified?: boolean | null
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  actionOffer?: ChatActionOffer | null
  recommendations?: BookRecommendation[] | null
}

export interface ChatResponse {
  message: string
  action_offer?: ChatActionOffer | null
  recommendations?: BookRecommendation[] | null
  conversation_id?: string | null
}

function createCorrelationId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `chat-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

const CONVERSATION_KEY = 'biblioteca.conversationId'

export function getOrCreateConversationId(): string {
  const existing = window.sessionStorage.getItem(CONVERSATION_KEY)
  if (existing) return existing
  const created = createCorrelationId()
  window.sessionStorage.setItem(CONVERSATION_KEY, created)
  return created
}

function persistConversationId(id: string | null | undefined): void {
  if (id && id !== window.sessionStorage.getItem(CONVERSATION_KEY)) {
    window.sessionStorage.setItem(CONVERSATION_KEY, id)
  }
}

/**
 * Devuelve el `userId` para enviar a `/chat`, tomado VERBATIM del claim
 * JWT `sub` (sin transformación de case). El backend/Biblioteca-MCP compara
 * de forma case-insensitive, por lo que el valor se preserva tal cual.
 *
 * Contrato: el frontend no debe normalizar el case ni el formato de este id;
 * la normalización es responsabilidad exclusiva del seam de Biblioteca-MCP.
 * Retorna null cuando no hay sesión activa.
 */
export function getChatUserId(): string | null {
  return useAuthStore.getState().user?.id ?? null
}

async function sendMessage(message: string): Promise<ChatResponse> {
  const conversationId = getOrCreateConversationId()
  const userId = getChatUserId()
  const response = await fetch(`${CHATBOT_API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': createCorrelationId(),
    },
    body: JSON.stringify({ message, userId, conversationId }),
  })

  if (!response.ok) {
    let detail = `Chatbot error: ${response.status}`
    try {
      const body = (await response.json()) as { detail?: string }
      if (body.detail) detail = body.detail
    } catch {
      // keep the default message
    }
    throw new Error(detail)
  }

  const data = (await response.json()) as ChatResponse
  persistConversationId(data.conversation_id)
  return data
}

export const chatService = { sendMessage, createCorrelationId }
