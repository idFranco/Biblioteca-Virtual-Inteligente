import { useState, type FormEvent } from 'react'
import { rentalsService } from '@/services/rentals'
import type { Book } from '@/types'

interface CreateRentalDialogProps {
  book: Book
  onClose: () => void
  onCreated: () => void
}

function toDateInputValue(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

export function CreateRentalDialog({ book, onClose, onCreated }: CreateRentalDialogProps) {
  const today = new Date()
  const defaultDue = new Date(today)
  defaultDue.setDate(defaultDue.getDate() + 14)
  const maxDue = new Date(today)
  maxDue.setDate(maxDue.getDate() + 30)

  const [dueDate, setDueDate] = useState(toDateInputValue(defaultDue))
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await rentalsService.createRental({ bookId: book.id, dueDate })
      onCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo crear el alquiler.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div
      role="dialog"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-espresso/50 p-4"
    >
      <form onSubmit={handleSubmit} className="texture-grain w-full max-w-md rounded-lg border border-tan/80 bg-paper p-6 shadow-xl dark:border-wood dark:bg-wood-dark">
        <h2 className="font-heading text-lg font-semibold text-espresso dark:text-parchment">Alquilar "{book.title}"</h2>
        <p className="mb-4 text-sm text-sepia dark:text-tan">{book.author}</p>

        {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

        <div className="mb-4">
          <label htmlFor="dueDate" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">
            Fecha límite de devolución
          </label>
          <input
            id="dueDate"
            type="date"
            required
            min={toDateInputValue(today)}
            max={toDateInputValue(maxDue)}
            value={dueDate}
            onChange={(event) => setDueDate(event.target.value)}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>

        <div className="flex justify-end gap-2">
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
            {submitting ? 'Alquilando...' : 'Confirmar alquiler'}
          </button>
        </div>
      </form>
    </div>
  )
}