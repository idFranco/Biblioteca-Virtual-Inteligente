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
    <div className="fixed bottom-4 right-4 z-50 flex w-80 flex-col overflow-hidden rounded-lg border border-tan/80 bg-card shadow-[0_10px_34px_-12px_rgba(51,36,26,0.5)] dark:border-wood">
      <div className="wood-panel flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-parchment">
        <span aria-hidden="true" className="block size-1.5 rotate-45 bg-brass" />
        Asistente de la Biblioteca
      </div>
      <div className="flex h-96 flex-col gap-2 overflow-y-auto p-3">
        {messages.length === 0 && (
          <p className="text-sm text-sepia dark:text-tan">
            Pregunta por un libro y te ayudaré. Si no está en el catálogo, podrás solicitar una copia.
          </p>
        )}
        {messages.map((message) => (
          <div key={message.id} className="space-y-2">
            <div
              className={`max-w-[85%] whitespace-pre-wrap rounded-lg px-3 py-2 text-sm ${
                message.role === 'user'
                  ? 'ml-auto bg-wine text-paper dark:bg-primary dark:text-primary-foreground'
                  : 'bg-parchment/70 text-espresso dark:bg-wood dark:text-parchment'
              }`}
            >
              {message.content}
            </div>
            {message.role === 'assistant' && message.actionOffer && (
              <div className="rounded-lg border border-brass/40 bg-parchment/60 p-3 dark:border-wood dark:bg-wood-dark">
                <p className="text-sm font-medium text-espresso dark:text-parchment">
                  Este libro no está en el catálogo.
                </p>
                <p className="mt-1 text-xs text-sepia dark:text-tan">
                  Solicita una copia y te avisaremos cuando esté disponible pronto.
                </p>
                <button
                  type="button"
                  disabled={bookingId !== null}
                  onClick={() => void handleBookRequest(message)}
                  className="mt-2 rounded-md bg-wine px-3 py-1.5 text-xs font-medium text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
                >
                  {bookingId === 'submitting'
                    ? 'Enviando...'
                    : bookingId
                      ? 'Solicitud registrada'
                      : 'Solicitar copia (disponible pronto)'}
                </button>
                {bookingError && <p className="mt-2 text-xs text-oxide">{bookingError}</p>}
              </div>
            )}
          </div>
        ))}
        {sending && <p className="text-xs text-sepia dark:text-tan">Escribiendo...</p>}
      </div>
      <form onSubmit={handleSend} className="flex gap-2 border-t border-tan/70 bg-paper p-2 dark:border-wood dark:bg-wood-dark">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje..."
          className="flex-1 rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded bg-wine px-3 py-2 text-sm text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
        >
          Enviar
        </button>
      </form>
    </div>
  )
}