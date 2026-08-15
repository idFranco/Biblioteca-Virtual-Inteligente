import { useCallback, useEffect, useState, type ChangeEvent } from 'react'
import { booksService } from '@/services/books'
import type { Book, BookFilters } from '@/types'
import { BookCard } from '@/components/books/BookCard'
import { PageHeader } from '@/components/layout/PageHeader'
import { Pagination } from '@/components/ui/Pagination'

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
      <PageHeader
        title="Catálogo de libros"
        subtitle="Explora la colección de la biblioteca, filtra por autor, género y disponibilidad."
      />

      <div className="texture-grain mb-6 grid gap-4 rounded-lg border border-tan/80 bg-card p-4 shadow-sm md:grid-cols-4 dark:border-wood">
        <div>
          <label htmlFor="search" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Buscar</label>
          <input
            id="search"
            type="text"
            placeholder="Título o autor"
            value={filters.search ?? ''}
            onChange={handleSearch}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso placeholder:text-sepia/60 focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>
        <div>
          <label htmlFor="author" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Autor</label>
          <input
            id="author"
            type="text"
            value={filters.author ?? ''}
            onChange={handleAuthor}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso placeholder:text-sepia/60 focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>
        <div>
          <label htmlFor="genre" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Género</label>
          <input
            id="genre"
            type="text"
            value={filters.genre ?? ''}
            onChange={handleGenre}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso placeholder:text-sepia/60 focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>
        <div className="flex items-end pb-2">
          <label className="flex cursor-pointer items-center gap-2 text-sm font-medium text-espresso dark:text-parchment">
            <input
              type="checkbox"
              checked={filters.availableOnly === true}
              onChange={handleAvailable}
              className="size-4 accent-olive"
            />
            Solo disponibles
          </label>
        </div>
      </div>

      {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

      {loading ? (
        <p className="text-sm text-sepia">Cargando catálogo...</p>
      ) : books.length === 0 ? (
        <p className="text-sm text-sepia dark:text-tan">No se encontraron libros con los filtros aplicados.</p>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {books.map((book) => (
            <BookCard key={book.id} book={book} />
          ))}
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </div>
  )
}