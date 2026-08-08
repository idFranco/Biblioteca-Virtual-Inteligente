import { apiGet, apiPost } from './api'
import type { CreateRentalInput, PagedRentals, Rental, RentalStatus } from '@/types'

export const rentalsService = {
  async getMyRentals(page: number, pageSize: number, status?: RentalStatus): Promise<PagedRentals> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (status) params.set('status', status)
    return apiGet<PagedRentals>(`/api/rentals/mine?${params.toString()}`)
  },

  async getAllRentals(page: number, pageSize: number, status?: RentalStatus): Promise<PagedRentals> {
    const params = new URLSearchParams({ page: String(page), pageSize: String(pageSize) })
    if (status) params.set('status', status)
    return apiGet<PagedRentals>(`/api/rentals?${params.toString()}`)
  },

  async createRental(input: CreateRentalInput): Promise<Rental> {
    return apiPost<Rental>('/api/rentals', input)
  },

  async returnRental(rentalId: string): Promise<Rental> {
    return apiPost<Rental>(`/api/rentals/${rentalId}/return`, {})
  },
}