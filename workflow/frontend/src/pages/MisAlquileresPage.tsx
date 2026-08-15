import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { rentalsService } from '@/services/rentals'
import type { Rental, RentalStatus } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { Pagination } from '@/components/ui/Pagination'
import { StatusBadge } from '@/components/ui/StatusBadge'

function formatDate(value: string | null): string {
  if (!value) return '—'
  return new Date(value).toLocaleDateString()
}

const statusLabels: Record<RentalStatus, string> = {
  Active: 'Activo',
  Returned: 'Devuelto',
  Overdue: 'Vencido',
}

const statusVariants: Record<RentalStatus, 'active' | 'returned' | 'overdue'> = {
  Active: 'active',
  Returned: 'returned',
  Overdue: 'overdue',
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
      <PageHeader
        title="Mis alquileres"
        subtitle="Consulta el estado de las obras que tienes prestadas y sus fechas de devolución."
      />

      <div className="mb-6">
        <label htmlFor="statusFilter" className="mr-2 text-sm font-medium text-espresso dark:text-parchment">Estado:</label>
        <select
          id="statusFilter"
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value as RentalStatus | '')
            setPage(1)
          }}
          className="rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
        >
          <option value="">Todos</option>
          <option value="Active">Activos</option>
          <option value="Returned">Devueltos</option>
          <option value="Overdue">Vencidos</option>
        </select>
      </div>

      {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

      {loading ? (
        <p className="text-sm text-sepia">Cargando alquileres...</p>
      ) : rentals.length === 0 ? (
        <p className="text-sm text-sepia dark:text-tan">No tienes alquileres registrados.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-tan/80 bg-card dark:border-wood">
          <table className="min-w-full text-sm">
            <thead className="bg-parchment/60 dark:bg-wood-dark/60">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-sepia">Libro</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha de alquiler</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha límite</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha de devolución</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Estado</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Sala de lectura</th>
              </tr>
            </thead>
            <tbody>
              {rentals.map((rental) => {
                const isOverdue = rental.status === 'Active' && rental.isOverdue
                return (
                  <tr key={rental.id} className="border-t border-tan/70 text-espresso dark:border-wood dark:text-parchment">
                    <td className="px-4 py-2 font-medium">{rental.bookTitle}</td>
                    <td className="px-4 py-2">{formatDate(rental.rentedAt)}</td>
                    <td className="px-4 py-2">{formatDate(rental.dueDate)}</td>
                    <td className="px-4 py-2">{formatDate(rental.returnedAt)}</td>
                    <td className="px-4 py-2 text-center">
                      <StatusBadge variant={isOverdue ? 'overdue' : statusVariants[rental.status]}>
                        {isOverdue ? 'Vencido' : statusLabels[rental.status]}
                      </StatusBadge>
                    </td>
                    <td className="px-4 py-2 text-center">
                      {rental.status === 'Active' || rental.status === 'Overdue' ? (
                        <Link
                          to={`/sala-lectura/${rental.bookId}`}
                          className="inline-block rounded-md border border-brass/50 bg-paper px-3 py-1.5 text-xs font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
                        >
                          Leer
                        </Link>
                      ) : (
                        <span className="text-xs text-sepia/60 dark:text-tan/50">—</span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </div>
  )
}