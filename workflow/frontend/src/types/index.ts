export interface User {
  id: string
  fullName: string
  email: string
  roles: string[]
  permissions: string[]
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

export interface Book {
  id: string
  title: string
  author: string
  isbn: string | null
  genre: string | null
  description: string | null
  totalCopies: number
  availableCopies: number
  isAvailable: boolean
}

export interface PagedBooks {
  page: number
  pageSize: number
  totalItems: number
  totalPages: number
  items: Book[]
}

export interface BookFilters {
  search?: string
  author?: string
  genre?: string
  availableOnly?: boolean
}

export interface CreateBookInput {
  title: string
  author: string
  isbn?: string | null
  genre?: string | null
  description?: string | null
  totalCopies: number
}

export interface UpdateBookInput extends CreateBookInput {
  availableCopies: number
}

export type RentalStatus = 'Active' | 'Returned' | 'Overdue'

export interface Rental {
  id: string
  userId: string
  bookId: string
  bookTitle: string
  userEmail: string
  rentedAt: string
  dueDate: string
  returnedAt: string | null
  status: RentalStatus
  isOverdue: boolean
}

export interface PagedRentals {
  page: number
  pageSize: number
  totalItems: number
  totalPages: number
  items: Rental[]
}

export interface CreateRentalInput {
  bookId: string
  dueDate: string
}