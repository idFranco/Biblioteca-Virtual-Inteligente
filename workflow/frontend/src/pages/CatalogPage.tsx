import { useCallback, useEffect, useState, type ChangeEvent } from 'react'
import { booksService } from '@/services/books'
import type { Book, BookFilters } from '@/types'

export function CatalogPage() {
  const [books, setBooks] = useState<Book[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [filters, setFilters] = useState<BookFilters>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pageSize = 20

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await booksService.getBooks(filters, page, pageSize)
      setBooks(result.items)
      setTotalPages(result.totalPages)
    } catch {
      setError('No se pudo cargar el catálogo. Inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }, [filters, page])

  useEffect(() => {
    void load()
  }, [load])

  function handleSearch(event: ChangeEvent<HTMLInputElement>) {
    setFilters((f) => ({ ...f, search: event.target.value || undefined }))
    setPage(1)
  }

  function handleAuthor(event: ChangeEvent<HTMLInputElement>) {
    setFilters((f) => ({ ...f, author: event.target.value || undefined }))
    setPage(1)
  }

  function handleGenre(event: ChangeEvent<HTMLInputElement>) {
    setFilters((f) => ({ ...f, genre: event.target.value || undefined }))
    setPage(1)
  }

  function handleAvailable(event: ChangeEvent<HTMLInputElement>) {
    setFilters((f) => ({ ...f, availableOnly: event.target.checked ? true : undefined }))
    setPage(1)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold">Catálogo de libros</h1>

      <div className="mb-6 grid gap-4 rounded-lg border p-4 md:grid-cols-4">
        <div>
          <label htmlFor="search" className="mb-1 block text-sm font-medium">Buscar</label>
          <input
            id="search"
            type="text"
            placeholder="Título o autor"
            value={filters.search ?? ''}
            onChange={handleSearch}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div>
          <label htmlFor="author" className="mb-1 block text-sm font-medium">Autor</label>
          <input
            id="author"
            type="text"
            value={filters.author ?? ''}
            onChange={handleAuthor}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div>
          <label htmlFor="genre" className="mb-1 block text-sm font-medium">Género</label>
          <input
            id="genre"
            type="text"
            value={filters.genre ?? ''}
            onChange={handleGenre}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div className="flex items-end">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={filters.availableOnly === true} onChange={handleAvailable} />
            Solo disponibles
          </label>
        </div>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {loading ? (
        <p>Cargando catálogo...</p>
      ) : books.length === 0 ? (
        <p className="text-gray-600">No se encontraron libros con los filtros aplicados.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {books.map((book) => (
            <div key={book.id} className="flex flex-col justify-between rounded-lg border p-4">
              <div>
                <h3 className="text-lg font-semibold">{book.title}</h3>
                <p className="text-sm text-gray-600">{book.author}</p>
                {book.genre && <p className="mt-1 text-sm text-gray-500">{book.genre}</p>}
              </div>
              <div className="mt-3">
                <span
                  className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                    book.isAvailable ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}
                >
                  {book.isAvailable ? 'Disponible' : 'No disponible'}
                </span>
                <p className="mt-2 text-xs text-gray-500">
                  {book.availableCopies} / {book.totalCopies} copias disponibles
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {!loading && totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-4">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
            className="rounded border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
          >
            Anterior
          </button>
          <span className="text-sm">Página {page} de {totalPages}</span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
            className="rounded border border-gray-300 px-3 py-1 text-sm disabled:opacity-50"
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  )
}