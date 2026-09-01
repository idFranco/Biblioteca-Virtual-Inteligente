import { useState, type FormEvent } from 'react'
import { BookOpen } from 'lucide-react'
import { bookRequestsService } from '@/services/bookRequests'

interface BookRequestDialogProps {
  onClose: () => void
  onCreated: () => void
}

/**
 * Diálogo reutilizable "Solicitar título": permite al usuario pedir que se
 * añada al catálogo un título que no existe. Título y autor son obligatorios;
 * el ISBN es opcional. Reutiliza el patrón modal on-brand de la librería.
 */
export function BookRequestDialog({ onClose, onCreated }: BookRequestDialogProps) {
  const [title, setTitle] = useState('')
  const [author, setAuthor] = useState('')
  const [isbn, setIsbn] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await bookRequestsService.createRequest({
        title,
        author,
        isbn: isbn.trim() ? isbn.trim() : null,
      })
      onCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo enviar la solicitud.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Solicitar título"
      className="fixed inset-0 z-50 flex items-center justify-center bg-espresso/50 p-4"
    >
      <form
        onSubmit={handleSubmit}
        className="texture-grain w-full max-w-md rounded-lg border border-tan/80 bg-paper p-6 shadow-xl dark:border-wood dark:bg-wood-dark"
      >
        <div className="flex items-center gap-3">
          <span
            aria-hidden="true"
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-sm border border-brass/50 bg-brass/10 text-brass"
          >
            <BookOpen className="size-5" />
          </span>
          <div>
            <h2 className="font-heading text-lg font-semibold text-espresso dark:text-parchment">
              Solicitar título
            </h2>
            <p className="text-sm text-sepia dark:text-tan">
              Pide que añadamos al catálogo un libro que no encuentras.
            </p>
          </div>
        </div>

        <div className="ornament-rule mt-4">
          <span className="ornament-diamond" />
        </div>

        {error && <p className="mt-4 text-sm text-oxide">{error}</p>}

        <div className="mt-4">
          <label htmlFor="request-title" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">
            Título <span className="text-oxide">*</span>
          </label>
          <input
            id="request-title"
            type="text"
            required
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>

        <div className="mt-4">
          <label htmlFor="request-author" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">
            Autor <span className="text-oxide">*</span>
          </label>
          <input
            id="request-author"
            type="text"
            required
            value={author}
            onChange={(event) => setAuthor(event.target.value)}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>

        <div className="mt-4">
          <label htmlFor="request-isbn" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">
            ISBN <span className="text-sepia/70 dark:text-tan/60">(opcional)</span>
          </label>
          <input
            id="request-isbn"
            type="text"
            value={isbn}
            onChange={(event) => setIsbn(event.target.value)}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>

        <div className="mt-6 flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded-md bg-wine px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
          >
            {submitting ? 'Enviando...' : 'Enviar solicitud'}
          </button>
        </div>
      </form>
    </div>
  )
}
