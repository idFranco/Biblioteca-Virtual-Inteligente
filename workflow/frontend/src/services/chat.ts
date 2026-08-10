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

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  actionOffer?: ChatActionOffer | null
}

export interface ChatResponse {
  message: string
  action_offer?: ChatActionOffer | null
}

function createCorrelationId(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `chat-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`
}

async function sendMessage(message: string): Promise<ChatResponse> {
  const { user } = useAuthStore.getState()
  const response = await fetch(`${CHATBOT_API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': createCorrelationId(),
    },
    body: JSON.stringify({ message, userId: user?.id ?? null }),
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

  return response.json() as Promise<ChatResponse>
}

export const chatService = { sendMessage, createCorrelationId }
