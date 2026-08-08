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
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    >
      <form onSubmit={handleSubmit} className="w-full max-w-md rounded-lg border bg-white p-6 shadow-lg">
        <h2 className="text-lg font-semibold">Alquilar "{book.title}"</h2>
        <p className="mb-4 text-sm text-gray-600">{book.author}</p>

        {error && <p className="mb-4 text-sm text-red-600">{error}</p>}

        <div className="mb-4">
          <label htmlFor="dueDate" className="mb-1 block text-sm font-medium">
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
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="rounded border border-gray-300 px-4 py-2 text-sm"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={submitting}
            className="rounded bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
          >
            {submitting ? 'Alquilando...' : 'Confirmar alquiler'}
          </button>
        </div>
      </form>
    </div>
  )
}