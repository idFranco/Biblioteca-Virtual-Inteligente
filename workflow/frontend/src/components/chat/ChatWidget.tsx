import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { chatService, type ChatMessage, type ChatResponse } from '@/services/chat'
import { bookRequestsService } from '@/services/bookRequests'

export function ChatWidget() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [bookingId, setBookingId] = useState<string | null>(null)
  const [bookingError, setBookingError] = useState<string | null>(null)

  async function handleSend(event: FormEvent) {
    event.preventDefault()
    const content = input.trim()
    if (!content || sending) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
    }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setSending(true)
    setBookingError(null)

    try {
      const response: ChatResponse = await chatService.sendMessage(content)
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.message,
        actionOffer: responsesToOffer(response),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Lo siento, el asistente no está disponible en este momento.',
        },
      ])
    } finally {
      setSending(false)
    }
  }

  function responsesToOffer(response: ChatResponse): ChatMessage['actionOffer'] {
    if (
      response.action_offer &&
      response.action_offer.type === 'book_request' &&
      response.action_offer.metadata?.title &&
      response.action_offer.metadata?.author
    ) {
      return response.action_offer
    }
    return null
  }

  async function handleBookRequest(message: ChatMessage) {
    if (!message.actionOffer || bookingId) return
    setBookingError(null)
    setBookingId('submitting')
    try {
      const created = await bookRequestsService.createRequest({
        title: message.actionOffer.metadata.title,
        author: message.actionOffer.metadata.author,
        isbn: message.actionOffer.metadata.isbn ?? null,
        genre: message.actionOffer.metadata.genre ?? null,
        description: message.actionOffer.metadata.description ?? null,
        openLibraryKey: message.actionOffer.metadata.openLibraryKey ?? null,
      })
      setBookingId(created.id)
    } catch (error) {
      setBookingError(error instanceof Error ? error.message : 'No se pudo registrar la solicitud.')
      setBookingId(null)
    }
  }

  function handleKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      void handleSend(event)
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex w-80 flex-col rounded-lg border bg-white shadow-xl">
      <div className="rounded-t-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">
        Asistente de la Biblioteca
      </div>
      <div className="flex h-96 flex-col gap-2 overflow-y-auto p-3">
        {messages.length === 0 && (
          <p className="text-sm text-gray-500">
            Pregunta por un libro y te ayudaré. Si no está en el catálogo, podrás solicitar una copia.
          </p>
        )}
        {messages.map((message) => (
          <div key={message.id} className="space-y-2">
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                message.role === 'user'
                  ? 'ml-auto bg-blue-600 text-white'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {message.content}
            </div>
            {message.role === 'assistant' && message.actionOffer && (
              <div className="rounded-lg border border-blue-200 bg-blue-50 p-3">
                <p className="text-sm font-medium text-blue-900">
                  Este libro no está en el catálogo.
                </p>
                <p className="mt-1 text-xs text-blue-700">
                  Solicita una copia y te avisaremos cuando esté disponible pronto.
                </p>
                <button
                  type="button"
                  disabled={bookingId !== null}
                  onClick={() => void handleBookRequest(message)}
                  className="mt-2 rounded bg-blue-600 px-3 py-1.5 text-xs font-medium text-white disabled:opacity-50"
                >
                  {bookingId === 'submitting'
                    ? 'Enviando...'
                    : bookingId
                      ? 'Solicitud registrada'
                      : 'Solicitar copia (disponible pronto)'}
                </button>
                {bookingError && <p className="mt-2 text-xs text-red-600">{bookingError}</p>}
              </div>
            )}
          </div>
        ))}
        {sending && <p className="text-xs text-gray-500">Escribiendo...</p>}
      </div>
      <form onSubmit={handleSend} className="flex gap-2 border-t p-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje..."
          className="flex-1 rounded border border-gray-300 px-3 py-2 text-sm"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded bg-blue-600 px-3 py-2 text-sm text-white disabled:opacity-50"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}
