import { useCallback, useEffect, useState } from 'react'
import { rentalsService } from '@/services/rentals'
import { useAuthStore } from '@/stores/authStore'
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

export function AlquileresAdminPage() {
  const user = useAuthStore((state) => state.user)
  const canReturn = user != null && user.permissions.includes('rentals.return')

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
      const result = await rentalsService.getAllRentals(page, pageSize, statusFilter || undefined)
      setRentals(result.items)
      setTotalPages(result.totalPages)
    } catch {
      setError('No se pudieron cargar los alquileres.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter])

  useEffect(() => {
    void load()
  }, [load])

  async function handleReturn(rental: Rental) {
    if (!window.confirm(`¿Registrar la devolución de "${rental.bookTitle}" (${rental.userEmail})?`)) {
      return
    }
    setError(null)
    try {
      await rentalsService.returnRental(rental.id)
      await load()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'No se pudo registrar la devolución.')
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Gestión de alquileres"
        subtitle="Supervisa los préstamos activos y registra las devoluciones de la biblioteca."
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
        <p className="text-sm text-sepia dark:text-tan">No hay alquileres registrados.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-tan/80 bg-card dark:border-wood">
          <table className="min-w-full text-sm">
            <thead className="bg-parchment/60 dark:bg-wood-dark/60">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-sepia">Libro</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Usuario</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha de alquiler</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha límite</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha de devolución</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Estado</th>
                {canReturn && <th className="px-4 py-2 text-right font-medium text-sepia">Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {rentals.map((rental) => {
                const isOverdue = rental.status === 'Active' && rental.isOverdue
                return (
                  <tr key={rental.id} className="border-t border-tan/70 text-espresso dark:border-wood dark:text-parchment">
                    <td className="px-4 py-2 font-medium">{rental.bookTitle}</td>
                    <td className="px-4 py-2">{rental.userEmail}</td>
                    <td className="px-4 py-2">{formatDate(rental.rentedAt)}</td>
                    <td className="px-4 py-2">{formatDate(rental.dueDate)}</td>
                    <td className="px-4 py-2">{formatDate(rental.returnedAt)}</td>
                    <td className="px-4 py-2 text-center">
                      <StatusBadge variant={isOverdue ? 'overdue' : statusVariants[rental.status]}>
                        {isOverdue ? 'Vencido' : statusLabels[rental.status]}
                      </StatusBadge>
                    </td>
                    {canReturn && (
                      <td className="px-4 py-2 text-right">
                        {rental.status !== 'Returned' && (
                          <button
                            type="button"
                            onClick={() => void handleReturn(rental)}
                            className="rounded-md bg-olive px-2 py-1 text-xs font-medium text-paper transition-colors hover:brightness-110"
                          >
                            Registrar devolución
                          </button>
                        )}
                      </td>
                    )}
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