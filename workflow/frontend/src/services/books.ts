import { apiGet, apiPost, apiPut, apiDelete } from './api'
import type { Book, PagedBooks, BookFilters, CreateBookInput, UpdateBookInput } from '@/types'

export const booksService = {
  async getBooks(filters: BookFilters, page: number, pageSize: number): Promise<PagedBooks> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (filters.search) params.set('search', filters.search)
    if (filters.author) params.set('author', filters.author)
    if (filters.genre) params.set('genre', filters.genre)
    if (filters.availableOnly !== undefined) params.set('availableOnly', String(filters.availableOnly))
    return apiGet<PagedBooks>(`/api/books?${params.toString()}`)
  },

  async getBook(bookId: string): Promise<Book> {
    return apiGet<Book>(`/api/books/${bookId}`)
  },

  async createBook(input: CreateBookInput): Promise<Book> {
    return apiPost<Book>('/api/books', input)
  },

  async updateBook(bookId: string, input: UpdateBookInput): Promise<Book> {
    return apiPut<Book>(`/api/books/${bookId}`, input)
  },

  async deleteBook(bookId: string): Promise<void> {
    await apiDelete<void>(`/api/books/${bookId}`)
  },
}