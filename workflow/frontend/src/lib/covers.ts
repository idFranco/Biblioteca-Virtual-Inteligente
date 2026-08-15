import type { Book } from '@/types'

export type CoverSize = 'S' | 'M' | 'L'

interface CoverSource {
  isbn: string | null
  openLibraryKey: string | null
}

/**
 * Deriva la URL de la portada desde el ISBN (prioritario) o la clave
 * Open Library (OLID) del libro, contra covers.openlibrary.org.
 * Devuelve null cuando el libro no expone ninguno de los dos identificadores.
 */
export function getCoverUrl(book: CoverSource, size: CoverSize = 'M'): string | null {
  const isbn = book.isbn?.replace(/[\s-]/g, '')
  if (isbn) {
    return `https://covers.openlibrary.org/b/isbn/${isbn}-${size}.jpg`
  }
  const olid = book.openLibraryKey?.trim()
  if (olid) {
    return `https://covers.openlibrary.org/b/olid/${olid}-${size}.jpg`
  }
  return null
}

/** Nombre del archivo derivado (útil para claves de React y tests). */
export function getCoverId(book: Pick<Book, 'isbn' | 'openLibraryKey'>): string {
  return book.isbn?.replace(/[\s-]/g, '') ?? book.openLibraryKey ?? 'cover'
}
