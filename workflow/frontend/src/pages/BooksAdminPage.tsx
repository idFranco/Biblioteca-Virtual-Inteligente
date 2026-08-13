import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { booksService } from '@/services/books'
import type { Book } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { StatusBadge } from '@/components/ui/StatusBadge'

interface BookForm {
  title: string
  author: string
  isbn: string
  genre: string
  description: string
  totalCopies: number
  availableCopies: number
}

const emptyForm: BookForm = {
  title: '',
  author: '',
  isbn: '',
  genre: '',
  description: '',
  totalCopies: 1,
  availableCopies: 1,
}

export function BooksAdminPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [form, setForm] = useState<BookForm>(emptyForm)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await booksService.getBooks({}, 1, 100)
      setBooks(result.items)
    } catch {
      setError('No se pudo cargar la lista de libros.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  function startEdit(book: Book) {
    setEditingId(book.id)
    setForm({
      title: book.title,
      author: book.author,
      isbn: book.isbn ?? '',
      genre: book.genre ?? '',
      description: book.description ?? '',
      totalCopies: book.totalCopies,
      availableCopies: book.availableCopies,
    })
  }

  function resetForm() {
    setEditingId(null)
    setForm(emptyForm)
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    try {
      if (editingId) {
        await booksService.updateBook(editingId, {
          title: form.title,
          author: form.author,
          isbn: form.isbn || null,
          genre: form.genre || null,
          description: form.description || null,
          totalCopies: form.totalCopies,
          availableCopies: form.availableCopies,
        })
      } else {
        await booksService.createBook({
          title: form.title,
          author: form.author,
          isbn: form.isbn || null,
          genre: form.genre || null,
          description: form.description || null,
          totalCopies: form.totalCopies,
        })
      }
      resetForm()
      await reload()
    } catch {
      setError('No se pudo guardar el libro. Verifica los datos.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(book: Book) {
    if (!window.confirm(`¿Eliminar el libro "${book.title}"?`)) return
    try {
      await booksService.deleteBook(book.id)
      await reload()
    } catch {
      setError('No se pudo eliminar el libro.')
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Gestión de libros"
        subtitle="Administra el catálogo: crea, edita y elimina libros de la biblioteca."
      />

      {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

      <form onSubmit={handleSubmit} className="texture-grain mb-8 rounded-lg border border-tan/80 bg-card p-4 shadow-sm dark:border-wood">
        <h2 className="mb-4 font-heading text-lg font-semibold text-espresso dark:text-parchment">
          {editingId ? 'Editar libro' : 'Nuevo libro'}
        </h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="title" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Título</label>
            <input
              id="title"
              required
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div>
            <label htmlFor="author" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Autor</label>
            <input
              id="author"
              required
              value={form.author}
              onChange={(e) => setForm((f) => ({ ...f, author: e.target.value }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div>
            <label htmlFor="isbn" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">ISBN</label>
            <input
              id="isbn"
              value={form.isbn}
              onChange={(e) => setForm((f) => ({ ...f, isbn: e.target.value }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div>
            <label htmlFor="genre" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Género</label>
            <input
              id="genre"
              value={form.genre}
              onChange={(e) => setForm((f) => ({ ...f, genre: e.target.value }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="description" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Descripción</label>
            <textarea
              id="description"
              rows={3}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div>
            <label htmlFor="totalCopies" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Total de copias</label>
            <input
              id="totalCopies"
              type="number"
              min={0}
              value={form.totalCopies}
              onChange={(e) => setForm((f) => ({ ...f, totalCopies: Number(e.target.value) }))}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          {editingId && (
            <div>
              <label htmlFor="availableCopies" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Copias disponibles</label>
              <input
                id="availableCopies"
                type="number"
                min={0}
                max={form.totalCopies}
                value={form.availableCopies}
                onChange={(e) => setForm((f) => ({ ...f, availableCopies: Number(e.target.value) }))}
                className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
              />
            </div>
          )}
        </div>
        <div className="mt-4 flex gap-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded-md bg-wine px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
          >
            {saving ? 'Guardando...' : (editingId ? 'Actualizar' : 'Crear')}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={resetForm}
              className="rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p className="text-sm text-sepia">Cargando libros...</p>
      ) : books.length === 0 ? (
        <p className="text-sm text-sepia dark:text-tan">Aún no hay libros registrados.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-tan/80 bg-card dark:border-wood">
          <table className="min-w-full text-sm">
            <thead className="bg-parchment/60 dark:bg-wood-dark/60">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-sepia">Título</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Autor</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Género</th>
                <th className="px-4 py-2 text-right font-medium text-sepia">Copias</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Disponible</th>
                <th className="px-4 py-2 text-right font-medium text-sepia">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => (
                <tr key={book.id} className="border-t border-tan/70 text-espresso dark:border-wood dark:text-parchment">
                  <td className="px-4 py-2">{book.title}</td>
                  <td className="px-4 py-2">{book.author}</td>
                  <td className="px-4 py-2">{book.genre ?? '—'}</td>
                  <td className="px-4 py-2 text-right">{book.availableCopies} / {book.totalCopies}</td>
                  <td className="px-4 py-2 text-center">
                    <StatusBadge variant={book.isAvailable ? 'available' : 'unavailable'}>
                      {book.isAvailable ? 'Sí' : 'No'}
                    </StatusBadge>
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => startEdit(book)}
                      className="mr-2 rounded-md border border-brass/50 bg-paper px-2 py-1 text-xs font-medium text-espresso transition-colors hover:border-brass hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleDelete(book)}
                      className="rounded-md bg-oxide px-2 py-1 text-xs font-medium text-paper transition-colors hover:brightness-110"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}