import { useRef, useState, type FormEvent, type KeyboardEvent, type PointerEvent } from 'react'
import { Maximize2, MessageCircle, Minimize2, ThumbsDown, ThumbsUp, X } from 'lucide-react'
import { chatService, type BookRecommendation, type ChatMessage, type ChatResponse } from '@/services/chat'
import { bookRequestsService } from '@/services/bookRequests'
import { BookCover } from '@/components/books/BookCover'
import {
  useChatWidgetStore,
  CHAT_WIDGET_DEFAULTS,
} from '@/stores/chatWidgetStore'

const MIN_WIDTH = 280
const MIN_HEIGHT = 320

function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

export function ChatWidget() {
  const isOpen = useChatWidgetStore((state) => state.isOpen)
  const size = useChatWidgetStore((state) => state.size)
  const widthPx = useChatWidgetStore((state) => state.widthPx)
  const heightPx = useChatWidgetStore((state) => state.heightPx)
  const toggleSize = useChatWidgetStore((state) => state.toggleSize)
  const open = useChatWidgetStore((state) => state.open)
  const close = useChatWidgetStore((state) => state.close)
  const setWidth = useChatWidgetStore((state) => state.setWidth)
  const setHeight = useChatWidgetStore((state) => state.setHeight)

  const [conversation, setConversation] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [bookingId, setBookingId] = useState<string | null>(null)
  const [bookingError, setBookingError] = useState<string | null>(null)

  const widgetRef = useRef<HTMLDivElement | null>(null)
  const resizing = useRef<'width' | 'height' | null>(null)

  const defaults = CHAT_WIDGET_DEFAULTS[size]
  const widgetWidth = clamp(widthPx ?? defaults.width, MIN_WIDTH, Math.max(MIN_WIDTH, window.innerWidth - 16))
  const widgetHeight = clamp(heightPx ?? defaults.height, MIN_HEIGHT, Math.max(MIN_HEIGHT, window.innerHeight - 16))

  function startResize(axis: 'width' | 'height', event: PointerEvent<HTMLDivElement>) {
    event.preventDefault()
    resizing.current = axis
    const startPos = axis === 'width' ? event.clientX : event.clientY
    const startSize = axis === 'width' ? widgetRef.current?.getBoundingClientRect().width ?? defaults.width : widgetRef.current?.getBoundingClientRect().height ?? defaults.height

    const handleMove = (moveEvent: globalThis.PointerEvent) => {
      const current = axis === 'width' ? moveEvent.clientX : moveEvent.clientY
      const delta = startPos - current
      const next = Math.round(startSize + delta)
      if (axis === 'width') {
        setWidth(clamp(next, MIN_WIDTH, Math.max(MIN_WIDTH, window.innerWidth - 16)))
      } else {
        setHeight(clamp(next, MIN_HEIGHT, Math.max(MIN_HEIGHT, window.innerHeight - 16)))
      }
    }

    const handleUp = () => {
      resizing.current = null
      window.removeEventListener('pointermove', handleMove)
      window.removeEventListener('pointerup', handleUp)
    }

    window.addEventListener('pointermove', handleMove)
    window.addEventListener('pointerup', handleUp)
  }

  function handleResizeKey(axis: 'width' | 'height', event: KeyboardEvent<HTMLDivElement>) {
    const step = event.shiftKey ? 32 : 8
    if (axis === 'width') {
      if (event.key === 'ArrowLeft') setWidth(clamp(widgetWidth + step, MIN_WIDTH, window.innerWidth - 16))
      if (event.key === 'ArrowRight') setWidth(clamp(widgetWidth - step, MIN_WIDTH, window.innerWidth - 16))
    } else {
      if (event.key === 'ArrowUp') setHeight(clamp(widgetHeight + step, MIN_HEIGHT, window.innerHeight - 16))
      if (event.key === 'ArrowDown') setHeight(clamp(widgetHeight - step, MIN_HEIGHT, window.innerHeight - 16))
    }
  }

  async function handleSend(event: FormEvent) {
    event.preventDefault()
    const content = input.trim()
    if (!content || sending) return

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
    }
    setConversation((prev) => [...prev, userMessage])
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
        recommendations: response.recommendations ?? null,
      }
      setConversation((prev) => [...prev, assistantMessage])
    } catch {
      setConversation((prev) => [
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

  async function handleFeedback(recommendation: BookRecommendation, liked: boolean) {
    if (sending) return
    const title = recommendation.title
    const text = liked ? `Me gustó el libro «${title}»` : `No me gustó el libro «${title}»`
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: text }
    setConversation((prev) => [...prev, userMessage])
    setSending(true)
    try {
      const response: ChatResponse = await chatService.sendMessage(text)
      setConversation((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: response.message,
          actionOffer: responsesToOffer(response),
          recommendations: response.recommendations ?? null,
        },
      ])
    } catch {
      setConversation((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: 'Lo siento, no pude guardar tu valoración en este momento.',
        },
      ])
    } finally {
      setSending(false)
    }
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

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={open}
        aria-label="Abrir el asistente de la biblioteca"
        className="wood-panel fixed bottom-4 right-4 z-50 flex items-center gap-2 rounded-full border border-brass/40 px-4 py-3 text-sm font-medium text-parchment shadow-[0_10px_34px_-12px_rgba(51,36,26,0.5)] transition-colors hover:bg-brass/20 hover:text-brass"
      >
        <MessageCircle className="size-5" aria-hidden="true" />
        <span>Asistente de la Biblioteca</span>
      </button>
    )
  }

  return (
    <div
      ref={widgetRef}
      style={{ width: widgetWidth, height: widgetHeight }}
      className="fixed bottom-4 right-4 z-50 flex max-w-[calc(100vw-1rem)] max-h-[calc(100vh-1rem)] flex-col overflow-hidden rounded-lg border border-tan/80 bg-card shadow-[0_10px_34px_-12px_rgba(51,36,26,0.5)] dark:border-wood"
    >
      {/* Asa izquierda: redimensiona el ancho */}
      <div
        role="separator"
        aria-orientation="vertical"
        aria-label="Redimensionar el ancho del asistente"
        tabIndex={0}
        onPointerDown={(event) => startResize('width', event)}
        onKeyDown={(event) => handleResizeKey('width', event)}
        className="absolute inset-y-0 left-0 w-1.5 cursor-ew-resize touch-none bg-transparent transition-colors hover:bg-brass/50 focus:bg-brass/70 focus:outline-none"
      />

      <div className="wood-panel flex items-center gap-2 px-4 py-2.5 text-sm font-medium text-parchment">
        <span aria-hidden="true" className="block size-1.5 rotate-45 bg-brass" />
        <span className="min-w-0 flex-1 truncate">Asistente de la Biblioteca</span>
        <button
          type="button"
          onClick={toggleSize}
          aria-label={size === 'large' ? 'Reducir la ventana del asistente' : 'Ampliar la ventana del asistente'}
          className="rounded p-1 text-parchment/80 transition-colors hover:bg-brass/20 hover:text-brass"
        >
          {size === 'large' ? <Minimize2 className="size-4" aria-hidden="true" /> : <Maximize2 className="size-4" aria-hidden="true" />}
        </button>
        <button
          type="button"
          onClick={close}
          aria-label="Minimizar el asistente de la biblioteca"
          className="rounded p-1 text-parchment/80 transition-colors hover:bg-brass/20 hover:text-brass"
        >
          <X className="size-4" aria-hidden="true" />
        </button>
      </div>

      <div className="flex min-h-0 flex-1 flex-col gap-2 overflow-y-auto p-3">
        {conversation.length === 0 && (
          <p className="text-sm text-sepia dark:text-tan">
            Pregunta por un libro y te ayudaré. Si no está en el catálogo, podrás solicitar una copia.
          </p>
        )}
        {conversation.map((message) => (
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
            {message.role === 'assistant' && message.recommendations && message.recommendations.length > 0 && (
              <div className="space-y-2">
                {message.recommendations.map((recommendation) => (
                  <div
                    key={`${recommendation.id ?? recommendation.title}-${recommendation.title}`}
                    className="flex gap-3 rounded-lg border border-brass/40 bg-parchment/60 p-3 dark:border-wood dark:bg-wood-dark"
                  >
                    <div className="h-24 w-16 shrink-0">
                      <BookCover
                        title={recommendation.title}
                        author={recommendation.author}
                        isbn={recommendation.isbn}
                        openLibraryKey={recommendation.openLibraryKey}
                      />
                    </div>
                    <div className="flex min-w-0 flex-1 flex-col">
                      <p className="text-sm font-medium text-espresso dark:text-parchment">
                        {recommendation.title}
                      </p>
                      {recommendation.author && (
                        <p className="mt-0.5 text-xs text-sepia dark:text-tan">{recommendation.author}</p>
                      )}
                      {recommendation.reason && (
                        <p className="mt-1 text-xs italic text-sepia dark:text-tan">{recommendation.reason}</p>
                      )}
                      <div className="mt-auto flex items-center justify-between gap-2 pt-2">
                        <span
                          className={`rounded-full px-2 py-0.5 text-[10px] font-medium ${
                            recommendation.available
                              ? 'bg-olive/15 text-olive dark:bg-olive/25 dark:text-parchment'
                              : 'bg-oxide/15 text-oxide dark:bg-oxide/25 dark:text-parchment'
                          }`}
                        >
                          {recommendation.available ? 'Disponible' : 'Sin copias'}
                        </span>
                        <div className="flex gap-1">
                          <button
                            type="button"
                            aria-label={`Me gustó ${recommendation.title}`}
                            title="Me gustó"
                            disabled={sending}
                            onClick={() => void handleFeedback(recommendation, true)}
                            className="rounded p-1 text-espresso/70 transition-colors hover:bg-olive/15 hover:text-olive disabled:opacity-40 dark:text-parchment/70 dark:hover:text-parchment"
                          >
                            <ThumbsUp className="size-3.5" aria-hidden="true" />
                          </button>
                          <button
                            type="button"
                            aria-label={`No me gustó ${recommendation.title}`}
                            title="No me gustó"
                            disabled={sending}
                            onClick={() => void handleFeedback(recommendation, false)}
                            className="rounded p-1 text-espresso/70 transition-colors hover:bg-oxide/15 hover:text-oxide disabled:opacity-40 dark:text-parchment/70 dark:hover:text-parchment"
                          >
                            <ThumbsDown className="size-3.5" aria-hidden="true" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
          aria-label="Mensaje para el asistente"
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

      {/* Asa inferior: redimensiona la altura */}
      <div
        role="separator"
        aria-orientation="horizontal"
        aria-label="Redimensionar la altura del asistente"
        tabIndex={0}
        onPointerDown={(event) => startResize('height', event)}
        onKeyDown={(event) => handleResizeKey('height', event)}
        className="absolute inset-x-0 bottom-0 h-1.5 cursor-ns-resize touch-none bg-transparent transition-colors hover:bg-brass/50 focus:bg-brass/70 focus:outline-none"
      />
    </div>
  )
}
