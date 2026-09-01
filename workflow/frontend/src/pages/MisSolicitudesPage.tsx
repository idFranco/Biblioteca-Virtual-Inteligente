import { useCallback, useEffect, useState, type ChangeEvent } from 'react'
import { bookRequestsService } from '@/services/bookRequests'
import { RequestStatusBadge } from '@/components/requests/RequestStatusBadge'
import type { BookRequest, BookRequestStatus } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { Pagination } from '@/components/ui/Pagination'

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString()
}

export function MisSolicitudesPage() {
  const [requests, setRequests] = useState<BookRequest[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [statusFilter, setStatusFilter] = useState<BookRequestStatus | ''>('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const pageSize = 20

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await bookRequestsService.getMyRequests(
        page,
        pageSize,
        statusFilter || undefined,
      )
      setRequests(result.items)
      setTotalPages(result.totalPages)
    } catch {
      setError('No se pudieron cargar tus solicitudes.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter])

  useEffect(() => {
    void load()
  }, [load])

  function handleStatusChange(event: ChangeEvent<HTMLSelectElement>) {
    setStatusFilter(event.target.value as BookRequestStatus | '')
    setPage(1)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Mis solicitudes"
        subtitle="Consulta el estado de los títulos que has pedido añadir al catálogo."
      />

      <div className="mb-6">
        <label htmlFor="statusFilter" className="mr-2 text-sm font-medium text-espresso dark:text-parchment">Estado:</label>
        <select
          id="statusFilter"
          value={statusFilter}
          onChange={handleStatusChange}
          className="rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
        >
          <option value="">Todas</option>
          <option value="Pending">Pendiente</option>
          <option value="Approved">Aprobada</option>
          <option value="Rejected">Rechazada</option>
        </select>
      </div>

      {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

      {loading ? (
        <p className="text-sm text-sepia">Cargando solicitudes...</p>
      ) : requests.length === 0 ? (
        <p className="text-sm text-sepia dark:text-tan">No has realizado solicitudes de títulos.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-tan/80 bg-card dark:border-wood">
          <table className="min-w-full text-sm">
            <thead className="bg-parchment/60 dark:bg-wood-dark/60">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-sepia">Título</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Autor</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">ISBN</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Estado</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => (
                <tr key={request.id} className="border-t border-tan/70 text-espresso dark:border-wood dark:text-parchment">
                  <td className="px-4 py-2 font-medium">{request.title}</td>
                  <td className="px-4 py-2">{request.author}</td>
                  <td className="px-4 py-2">{request.isbn ?? '—'}</td>
                  <td className="px-4 py-2">{formatDate(request.requestedAt)}</td>
                  <td className="px-4 py-2 text-center">
                    <RequestStatusBadge status={request.status} />
                    {request.status === 'Rejected' && request.adminNotes && (
                      <p className="mt-1 text-xs text-sepia dark:text-tan">Motivo: {request.adminNotes}</p>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />
    </div>
  )
}
