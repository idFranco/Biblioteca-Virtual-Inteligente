import { useCallback, useEffect, useState } from 'react'
import { rentalsService } from '@/services/rentals'
import type { Rental, RentalStatus } from '@/types'

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
}

const statusLabels: Record<RentalStatus, string> = {
  Active: 'Activo',
  Returned: 'Devuelto',
  Overdue: 'Vencido',
}

const statusStyles: Record<RentalStatus, string> = {
  Active: 'bg-blue-100 text-blue-800',
  Returned: 'bg-green-100 text-green-800',
  Overdue: 'bg-red-100 text-red-800',
}

export function MisAlquileresPage() {
  const [rentals, setRentals] = useState<Rental[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [statusFilter, setStatusFilter] = useState<RentalStatus | ''>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pageSize = 20

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await rentalsService.getMyRentals(page, pageSize, statusFilter || undefined)
      setRentals(result.items)
      setTotalPages(result.totalPages)
    } catch {
      setError('No se pudieron cargar tus alquileres.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter])

  useEffect(() => {
    void load()
  }, [load])

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="mb-6 text-3xl font-bold">Mis alquileres</h1>

      <div className="mb-6">
        <label htmlFor="statusFilter" className="mr-2 text-sm font-medium">Estado:</label>
        <select
          id="statusFilter"
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value as RentalStatus | '')
            setPage(1)
          }}
          className="rounded border border-gray-300 px-3 py-2 text-sm"
        >
          <option value="">Todos</option>
          <option value="Active">Activos</option>
          <option value="Returned">Devueltos</option>
          <option value="Overdue">Vencidos</option>
        </select>
      </div>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      {loading ? (
        <p>Cargando alquileres...</p>
      ) : rentals.length === 0 ? (
        <p className="text-gray-600">No tienes alquileres registrados.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Libro</th>
                <th className="px-4 py-2 text-left">Fecha de alquiler</th>
                <th className="px-4 py-2 text-left">Fecha límite</th>
                <th className="px-4 py-2 text-left">Fecha de devolución</th>
                <th className="px-4 py-2 text-center">Estado</th>
              </tr>
            </thead>
            <tbody>
              {rentals.map((rental) => {
                const isOverdue = rental.status === 'Active' && rental.isOverdue
                return (
                  <tr key={rental.id} className="border-t">
                    <td className="px-4 py-2 font-medium">{rental.bookTitle}</td>
                    <td className="px-4 py-2">{formatDate(rental.rentedAt)}</td>
                    <td className="px-4 py-2">{formatDate(rental.dueDate)}</td>
                    <td className="px-4 py-2">{formatDate(rental.returnedAt)}</td>
                    <td className="px-4 py-2 text-center">
                      <span
                        className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${
                          isOverdue ? 'bg-red-100 text-red-800' : statusStyles[rental.status]
                        }`}
                      >
                        {isOverdue ? 'Vencido' : statusLabels[rental.status]}
                      </span>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
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