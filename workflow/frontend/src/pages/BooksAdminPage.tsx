import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { booksService } from '@/services/books'
import type { Book } from '@/types'

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
      <h1 className="mb-6 text-3xl font-bold">Gestión de libros</h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <form onSubmit={handleSubmit} className="mb-8 rounded-lg border p-4">
        <h2 className="mb-4 text-lg font-semibold">{editingId ? 'Editar libro' : 'Nuevo libro'}</h2>
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label htmlFor="title" className="mb-1 block text-sm font-medium">Título</label>
            <input
              id="title"
              required
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label htmlFor="author" className="mb-1 block text-sm font-medium">Autor</label>
            <input
              id="author"
              required
              value={form.author}
              onChange={(e) => setForm((f) => ({ ...f, author: e.target.value }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label htmlFor="isbn" className="mb-1 block text-sm font-medium">ISBN</label>
            <input
              id="isbn"
              value={form.isbn}
              onChange={(e) => setForm((f) => ({ ...f, isbn: e.target.value }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label htmlFor="genre" className="mb-1 block text-sm font-medium">Género</label>
            <input
              id="genre"
              value={form.genre}
              onChange={(e) => setForm((f) => ({ ...f, genre: e.target.value }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div className="md:col-span-2">
            <label htmlFor="description" className="mb-1 block text-sm font-medium">Descripción</label>
            <textarea
              id="description"
              rows={3}
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          <div>
            <label htmlFor="totalCopies" className="mb-1 block text-sm font-medium">Total de copias</label>
            <input
              id="totalCopies"
              type="number"
              min={0}
              value={form.totalCopies}
              onChange={(e) => setForm((f) => ({ ...f, totalCopies: Number(e.target.value) }))}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
          </div>
          {editingId && (
            <div>
              <label htmlFor="availableCopies" className="mb-1 block text-sm font-medium">Copias disponibles</label>
              <input
                id="availableCopies"
                type="number"
                min={0}
                max={form.totalCopies}
                value={form.availableCopies}
                onChange={(e) => setForm((f) => ({ ...f, availableCopies: Number(e.target.value) }))}
                className="w-full rounded border border-gray-300 px-3 py-2"
              />
            </div>
          )}
        </div>
        <div className="mt-4 flex gap-2">
          <button
            type="submit"
            disabled={saving}
            className="rounded bg-blue-600 px-4 py-2 text-white disabled:opacity-50"
          >
            {saving ? 'Guardando...' : (editingId ? 'Actualizar' : 'Crear')}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={resetForm}
              className="rounded border border-gray-300 px-4 py-2"
            >
              Cancelar
            </button>
          )}
        </div>
      </form>

      {loading ? (
        <p>Cargando libros...</p>
      ) : books.length === 0 ? (
        <p className="text-gray-600">Aún no hay libros registrados.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Título</th>
                <th className="px-4 py-2 text-left">Autor</th>
                <th className="px-4 py-2 text-left">Género</th>
                <th className="px-4 py-2 text-right">Copias</th>
                <th className="px-4 py-2 text-center">Disponible</th>
                <th className="px-4 py-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {books.map((book) => (
                <tr key={book.id} className="border-t">
                  <td className="px-4 py-2">{book.title}</td>
                  <td className="px-4 py-2">{book.author}</td>
                  <td className="px-4 py-2">{book.genre ?? '—'}</td>
                  <td className="px-4 py-2 text-right">{book.availableCopies} / {book.totalCopies}</td>
                  <td className="px-4 py-2 text-center">
                    {book.isAvailable ? 'Sí' : 'No'}
                  </td>
                  <td className="px-4 py-2 text-right">
                    <button
                      type="button"
                      onClick={() => startEdit(book)}
                      className="mr-2 rounded border border-gray-300 px-2 py-1 text-xs"
                    >
                      Editar
                    </button>
                    <button
                      type="button"
                      onClick={() => void handleDelete(book)}
                      className="rounded bg-red-600 px-2 py-1 text-xs text-white"
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