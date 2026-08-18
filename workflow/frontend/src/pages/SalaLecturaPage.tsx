import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { booksService } from '@/services/books'
import type { BookForReading } from '@/types'
import { BookCover } from '@/components/books/BookCover'
import { PageHeader } from '@/components/layout/PageHeader'

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

export function SalaLecturaPage() {
  const { bookId } = useParams<{ bookId: string }>()
  const [book, setBook] = useState<BookForReading | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!bookId) return
    let cancelled = false
    setLoading(true)
    setError(null)
    booksService
      .getBookForReading(bookId)
      .then((data) => {
        if (!cancelled) setBook(data)
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'No se pudo abrir la sala de lectura.')
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [bookId])

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <p className="text-sm text-sepia dark:text-tan">Abriendo la sala de lectura...</p>
      </div>
    )
  }

  if (error || !book) {
    return (
      <div className="container mx-auto max-w-2xl px-4 py-8">
        <PageHeader title="Sala de lectura" />
        <div className="texture-grain rounded-lg border border-tan/80 bg-card p-6 dark:border-wood">
          <p className="text-sm text-oxide">
            {error ?? 'No se encontró el libro en tu sala de lectura.'}
          </p>
          <p className="mt-2 text-sm text-sepia dark:text-tan">
            Solo puedes leer los libros que tienes alquilados y aún no has devuelto.
          </p>
          <Link
            to="/mis-alquileres"
            className="mt-4 inline-block rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
          >
            Volver a mis alquileres
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Sala de lectura"
        subtitle={`Estás leyendo "${book.title}" mientras el préstamo esté activo.`}
      />

      <div className="texture-grain overflow-hidden rounded-lg border border-tan/80 bg-card shadow-sm dark:border-wood">
        <div className="grid gap-6 border-b border-tan/70 p-6 dark:border-wood md:grid-cols-[10rem_1fr]">
          <div className="mx-auto h-56 w-40">
            <BookCover
              title={book.title}
              author={book.author}
              isbn={book.isbn}
              openLibraryKey={book.openLibraryKey}
              size="L"
            />
          </div>
          <div className="min-w-0">
            <h2 className="font-heading text-2xl font-semibold leading-snug text-espresso dark:text-parchment">
              {book.title}
            </h2>
            <p className="mt-1 text-sm text-sepia dark:text-tan">{book.author}</p>
            {book.genre && (
              <p className="mt-1.5 text-xs italic text-wood dark:text-brass">{book.genre}</p>
            )}
            <dl className="mt-4 flex flex-wrap gap-x-8 gap-y-2 text-sm">
              <div>
                <dt className="text-xs uppercase tracking-wide text-sepia dark:text-tan">Alquilado el</dt>
                <dd className="mt-0.5 font-medium text-espresso dark:text-parchment">
                  {formatDate(book.rentedAt)}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-sepia dark:text-tan">Fecha límite</dt>
                <dd className="mt-0.5 font-medium text-espresso dark:text-parchment">
                  {formatDate(book.dueDate)}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        <div className="p-6">
          <h3 className="font-heading text-lg font-semibold text-espresso dark:text-parchment">
            Contenido
          </h3>
          <div className="ornament-rule mt-3 max-w-md">
            <span className="ornament-diamond" />
          </div>
          <p className="mt-5 max-w-prose font-serif text-base leading-8 text-espresso dark:text-parchment">
            {book.description ?? 'Este ejemplar no incluye contenido textual disponible.'}
          </p>

          <div className="mt-8">
            <Link
              to="/mis-alquileres"
              className="inline-block rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
            >
              Volver a mis alquileres
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}