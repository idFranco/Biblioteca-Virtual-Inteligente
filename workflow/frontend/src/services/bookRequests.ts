import { apiGet, apiPost } from './api'
import type {
  ApproveBookRequestInput,
  BookRequest,
  BookRequestStatus,
  CreateBookRequestInput,
  PagedBookRequests,
  RejectBookRequestInput,
} from '@/types'

export const bookRequestsService = {
  async createRequest(input: CreateBookRequestInput): Promise<BookRequest> {
    return apiPost<BookRequest>('/api/book-requests', input)
  },

  async getMyRequests(
    page: number,
    pageSize: number,
    status?: BookRequestStatus,
  ): Promise<PagedBookRequests> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (status) params.set('status', status)
    return apiGet<PagedBookRequests>(`/api/book-requests/mine?${params.toString()}`)
  },

  async getAllRequests(
    page: number,
    pageSize: number,
    status?: BookRequestStatus,
    search?: string,
  ): Promise<PagedBookRequests> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (status) params.set('status', status)
    if (search) params.set('search', search)
    return apiGet<PagedBookRequests>(`/api/book-requests?${params.toString()}`)
  },

  async getRequestById(requestId: string): Promise<BookRequest> {
    return apiGet<BookRequest>(`/api/book-requests/${requestId}`)
  },

  async approveRequest(requestId: string, input: ApproveBookRequestInput): Promise<BookRequest> {
    return apiPost<BookRequest>(`/api/book-requests/${requestId}/approve`, input)
  },

  async rejectRequest(requestId: string, input: RejectBookRequestInput): Promise<BookRequest> {
    return apiPost<BookRequest>(`/api/book-requests/${requestId}/reject`, input)
  },
}
