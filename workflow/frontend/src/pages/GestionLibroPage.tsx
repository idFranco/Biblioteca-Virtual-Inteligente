import { useCallback, useEffect, useState, type ChangeEvent, type FormEvent } from 'react'
import { bookRequestsService } from '@/services/bookRequests'
import { RequestStatusBadge } from '@/components/requests/RequestStatusBadge'
import type { BookRequest, BookRequestStatus } from '@/types'
import { PageHeader } from '@/components/layout/PageHeader'
import { Pagination } from '@/components/ui/Pagination'

interface ApproveForm {
  title: string
  author: string
  isbn: string
  genre: string
  description: string
  totalCopies: number
}

const emptyApproveForm: ApproveForm = {
  title: '',
  author: '',
  isbn: '',
  genre: '',
  description: '',
  totalCopies: 1,
}

export function GestionLibroPage() {
  const [requests, setRequests] = useState<BookRequest[]>([])
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [statusFilter, setStatusFilter] = useState<BookRequestStatus | ''>('')
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [approving, setApproving] = useState<BookRequest | null>(null)
  const [approveForm, setApproveForm] = useState<ApproveForm>(emptyApproveForm)
  const [savingApprove, setSavingApprove] = useState(false)
  const [rejecting, setRejecting] = useState<BookRequest | null>(null)
  const [rejectNotes, setRejectNotes] = useState('')
  const [savingReject, setSavingReject] = useState(false)
  const pageSize = 20

  const reload = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await bookRequestsService.getAllRequests(
        page,
        pageSize,
        statusFilter || undefined,
        search || undefined,
      )
      setRequests(result.items)
      setTotalPages(result.totalPages)
    } catch {
      setError('No se pudo cargar la lista de solicitudes.')
    } finally {
      setLoading(false)
    }
  }, [page, statusFilter, search])

  useEffect(() => {
    void reload()
  }, [reload])

  function handleSearchChange(event: ChangeEvent<HTMLInputElement>) {
    setSearch(event.target.value)
    setPage(1)
  }

  function handleStatusChange(event: ChangeEvent<HTMLSelectElement>) {
    setStatusFilter(event.target.value as BookRequestStatus | '')
    setPage(1)
  }

  function openApprove(request: BookRequest) {
    setApproving(request)
    setApproveForm({
      title: request.title,
      author: request.author,
      isbn: request.isbn ?? '',
      genre: request.genre ?? '',
      description: request.description ?? '',
      totalCopies: 1,
    })
  }

  function closeApprove() {
    setApproving(null)
  }

  function openReject(request: BookRequest) {
    setRejecting(request)
    setRejectNotes('')
  }

  function closeReject() {
    setRejecting(null)
  }

  async function handleApprove(event: FormEvent) {
    event.preventDefault()
    if (!approving) return
    setSavingApprove(true)
    setError(null)
    try {
      await bookRequestsService.approveRequest(approving.id, {
        title: approveForm.title,
        author: approveForm.author,
        isbn: approveForm.isbn || null,
        genre: approveForm.genre || null,
        description: approveForm.description || null,
        totalCopies: approveForm.totalCopies,
      })
      closeApprove()
      await reload()
    } catch {
      setError('No se pudo aprobar la solicitud. Verifica los datos.')
    } finally {
      setSavingApprove(false)
    }
  }

  async function handleReject(event: FormEvent) {
    event.preventDefault()
    if (!rejecting) return
    setSavingReject(true)
    setError(null)
    try {
      await bookRequestsService.rejectRequest(rejecting.id, { adminNotes: rejectNotes })
      closeReject()
      await reload()
    } catch {
      setError('No se pudo rechazar la solicitud.')
    } finally {
      setSavingReject(false)
    }
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <PageHeader
        title="Gestión de libro"
        subtitle="Revisa las solicitudes de copias, dales de alta en el catálogo o recházalas."
      />

      {error && <p className="mb-4 text-sm text-oxide">{error}</p>}

      <div className="texture-grain mb-6 grid gap-4 rounded-lg border border-tan/80 bg-card p-4 shadow-sm md:grid-cols-3 dark:border-wood">
        <div>
          <label htmlFor="search" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Buscar por título, autor o ISBN</label>
          <input
            id="search"
            type="text"
            value={search}
            onChange={handleSearchChange}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          />
        </div>
        <div>
          <label htmlFor="status" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Estado</label>
          <select
            id="status"
            value={statusFilter}
            onChange={handleStatusChange}
            className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
          >
            <option value="">Todos</option>
            <option value="Pending">Pendiente</option>
            <option value="Approved">Aprobada</option>
            <option value="Rejected">Rechazada</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-sm text-sepia">Cargando solicitudes...</p>
      ) : requests.length === 0 ? (
        <p className="text-sm text-sepia dark:text-tan">No hay solicitudes que coincidan con los filtros.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-tan/80 bg-card dark:border-wood">
          <table className="min-w-full text-sm">
            <thead className="bg-parchment/60 dark:bg-wood-dark/60">
              <tr>
                <th className="px-4 py-2 text-left font-medium text-sepia">Título</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Autor</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Solicitante</th>
                <th className="px-4 py-2 text-left font-medium text-sepia">Fecha</th>
                <th className="px-4 py-2 text-center font-medium text-sepia">Estado</th>
                <th className="px-4 py-2 text-right font-medium text-sepia">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => (
                <tr key={request.id} className="border-t border-tan/70 text-espresso dark:border-wood dark:text-parchment">
                  <td className="px-4 py-2">
                    {request.title}
                    {request.openLibraryKey && (
                      <p className="text-xs text-sepia dark:text-tan">Open Library: {request.openLibraryKey}</p>
                    )}
                  </td>
                  <td className="px-4 py-2">{request.author}</td>
                  <td className="px-4 py-2">{request.requestedByEmail}</td>
                  <td className="px-4 py-2">{new Date(request.requestedAt).toLocaleDateString()}</td>
                  <td className="px-4 py-2 text-center">
                    <RequestStatusBadge status={request.status} />
                    {request.status === 'Rejected' && request.adminNotes && (
                      <p className="mt-1 text-xs text-sepia dark:text-tan">Motivo: {request.adminNotes}</p>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {request.status === 'Pending' && (
                      <>
                        <button
                          type="button"
                          onClick={() => openApprove(request)}
                          className="mr-2 rounded-md bg-olive px-2 py-1 text-xs font-medium text-paper transition-colors hover:brightness-110"
                        >
                          Aprobar
                        </button>
                        <button
                          type="button"
                          onClick={() => openReject(request)}
                          className="rounded-md bg-oxide px-2 py-1 text-xs font-medium text-paper transition-colors hover:brightness-110"
                        >
                          Rechazar
                        </button>
                      </>
                    )}
                    {request.status === 'Approved' && request.promotedBookId && (
                      <span className="text-xs text-olive">Libro creado</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <Pagination page={page} totalPages={totalPages} onChange={setPage} />

      {approving && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-espresso/50 p-4">
          <form onSubmit={handleApprove} className="texture-grain w-full max-w-lg rounded-lg border border-tan/80 bg-paper p-6 shadow-xl dark:border-wood dark:bg-wood-dark">
            <h2 className="mb-4 font-heading text-lg font-semibold text-espresso dark:text-parchment">Dar de alta libro solicitado</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label htmlFor="approve-title" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Título</label>
                <input
                  id="approve-title"
                  required
                  value={approveForm.title}
                  onChange={(e) => setApproveForm((f) => ({ ...f, title: e.target.value }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
              <div>
                <label htmlFor="approve-author" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Autor</label>
                <input
                  id="approve-author"
                  required
                  value={approveForm.author}
                  onChange={(e) => setApproveForm((f) => ({ ...f, author: e.target.value }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
              <div>
                <label htmlFor="approve-isbn" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">ISBN</label>
                <input
                  id="approve-isbn"
                  value={approveForm.isbn}
                  onChange={(e) => setApproveForm((f) => ({ ...f, isbn: e.target.value }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
              <div>
                <label htmlFor="approve-genre" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Género</label>
                <input
                  id="approve-genre"
                  value={approveForm.genre}
                  onChange={(e) => setApproveForm((f) => ({ ...f, genre: e.target.value }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
              <div className="md:col-span-2">
                <label htmlFor="approve-description" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Descripción</label>
                <textarea
                  id="approve-description"
                  rows={3}
                  value={approveForm.description}
                  onChange={(e) => setApproveForm((f) => ({ ...f, description: e.target.value }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
              <div>
                <label htmlFor="approve-copies" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Total de copias</label>
                <input
                  id="approve-copies"
                  type="number"
                  min={1}
                  value={approveForm.totalCopies}
                  onChange={(e) => setApproveForm((f) => ({ ...f, totalCopies: Number(e.target.value) }))}
                  className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={closeApprove}
                className="rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={savingApprove}
                className="rounded-md bg-olive px-4 py-2 text-sm font-medium text-paper transition-colors hover:brightness-110 disabled:opacity-50"
              >
                {savingApprove ? 'Guardando...' : 'Dar de alta y aprobar'}
              </button>
            </div>
          </form>
        </div>
      )}

      {rejecting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-espresso/50 p-4">
          <form onSubmit={handleReject} className="texture-grain w-full max-w-md rounded-lg border border-tan/80 bg-paper p-6 shadow-xl dark:border-wood dark:bg-wood-dark">
            <h2 className="mb-4 font-heading text-lg font-semibold text-espresso dark:text-parchment">Rechazar solicitud</h2>
            <p className="mb-4 text-sm text-sepia dark:text-tan">
              Libro: <span className="font-medium text-espresso dark:text-parchment">{rejecting.title}</span> de {rejecting.author}
            </p>
            <label htmlFor="reject-notes" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Motivo (obligatorio)</label>
            <textarea
              id="reject-notes"
              rows={3}
              required
              value={rejectNotes}
              onChange={(e) => setRejectNotes(e.target.value)}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={closeReject}
                className="rounded-md border border-brass/50 bg-paper px-4 py-2 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={savingReject}
                className="rounded-md bg-oxide px-4 py-2 text-sm font-medium text-paper transition-colors hover:brightness-110 disabled:opacity-50"
              >
                {savingReject ? 'Guardando...' : 'Rechazar'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}