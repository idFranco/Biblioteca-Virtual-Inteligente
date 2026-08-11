import { useCallback, useEffect, useState, type ChangeEvent, type FormEvent } from 'react'
import { bookRequestsService } from '@/services/bookRequests'
import { RequestStatusBadge } from '@/components/requests/RequestStatusBadge'
import type { BookRequest, BookRequestStatus } from '@/types'

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
      <h1 className="mb-6 text-3xl font-bold">Gestión de libro</h1>

      {error && <p className="mb-4 text-red-600">{error}</p>}

      <div className="mb-6 grid gap-4 rounded-lg border p-4 md:grid-cols-3">
        <div>
          <label htmlFor="search" className="mb-1 block text-sm font-medium">Buscar por título, autor o ISBN</label>
          <input
            id="search"
            type="text"
            value={search}
            onChange={handleSearchChange}
            className="w-full rounded border border-gray-300 px-3 py-2"
          />
        </div>
        <div>
          <label htmlFor="status" className="mb-1 block text-sm font-medium">Estado</label>
          <select
            id="status"
            value={statusFilter}
            onChange={handleStatusChange}
            className="w-full rounded border border-gray-300 px-3 py-2"
          >
            <option value="">Todos</option>
            <option value="Pending">Pendiente</option>
            <option value="Approved">Aprobada</option>
            <option value="Rejected">Rechazada</option>
          </select>
        </div>
      </div>

      {loading ? (
        <p>Cargando solicitudes...</p>
      ) : requests.length === 0 ? (
        <p className="text-gray-600">No hay solicitudes que coincidan con los filtros.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="min-w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 text-left">Título</th>
                <th className="px-4 py-2 text-left">Autor</th>
                <th className="px-4 py-2 text-left">Solicitante</th>
                <th className="px-4 py-2 text-left">Fecha</th>
                <th className="px-4 py-2 text-center">Estado</th>
                <th className="px-4 py-2 text-right">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((request) => (
                <tr key={request.id} className="border-t">
                  <td className="px-4 py-2">
                    {request.title}
                    {request.openLibraryKey && (
                      <p className="text-xs text-gray-500">Open Library: {request.openLibraryKey}</p>
                    )}
                  </td>
                  <td className="px-4 py-2">{request.author}</td>
                  <td className="px-4 py-2">{request.requestedByEmail}</td>
                  <td className="px-4 py-2">{new Date(request.requestedAt).toLocaleDateString()}</td>
                  <td className="px-4 py-2 text-center">
                    <RequestStatusBadge status={request.status} />
                    {request.status === 'Rejected' && request.adminNotes && (
                      <p className="mt-1 text-xs text-gray-500">Motivo: {request.adminNotes}</p>
                    )}
                  </td>
                  <td className="px-4 py-2 text-right">
                    {request.status === 'Pending' && (
                      <>
                        <button
                          type="button"
                          onClick={() => openApprove(request)}
                          className="mr-2 rounded bg-green-600 px-2 py-1 text-xs text-white"
                        >
                          Aprobar
                        </button>
                        <button
                          type="button"
                          onClick={() => openReject(request)}
                          className="rounded bg-red-600 px-2 py-1 text-xs text-white"
                        >
                          Rechazar
                        </button>
                      </>
                    )}
                    {request.status === 'Approved' && request.promotedBookId && (
                      <span className="text-xs text-gray-500">Libro creado</span>
                    )}
                  </td>
                </tr>
              ))}
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

      {approving && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <form onSubmit={handleApprove} className="w-full max-w-lg rounded-lg bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">Dar de alta libro solicitado</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label htmlFor="approve-title" className="mb-1 block text-sm font-medium">Título</label>
                <input
                  id="approve-title"
                  required
                  value={approveForm.title}
                  onChange={(e) => setApproveForm((f) => ({ ...f, title: e.target.value }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label htmlFor="approve-author" className="mb-1 block text-sm font-medium">Autor</label>
                <input
                  id="approve-author"
                  required
                  value={approveForm.author}
                  onChange={(e) => setApproveForm((f) => ({ ...f, author: e.target.value }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label htmlFor="approve-isbn" className="mb-1 block text-sm font-medium">ISBN</label>
                <input
                  id="approve-isbn"
                  value={approveForm.isbn}
                  onChange={(e) => setApproveForm((f) => ({ ...f, isbn: e.target.value }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label htmlFor="approve-genre" className="mb-1 block text-sm font-medium">Género</label>
                <input
                  id="approve-genre"
                  value={approveForm.genre}
                  onChange={(e) => setApproveForm((f) => ({ ...f, genre: e.target.value }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div className="md:col-span-2">
                <label htmlFor="approve-description" className="mb-1 block text-sm font-medium">Descripción</label>
                <textarea
                  id="approve-description"
                  rows={3}
                  value={approveForm.description}
                  onChange={(e) => setApproveForm((f) => ({ ...f, description: e.target.value }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
              <div>
                <label htmlFor="approve-copies" className="mb-1 block text-sm font-medium">Total de copias</label>
                <input
                  id="approve-copies"
                  type="number"
                  min={1}
                  value={approveForm.totalCopies}
                  onChange={(e) => setApproveForm((f) => ({ ...f, totalCopies: Number(e.target.value) }))}
                  className="w-full rounded border border-gray-300 px-3 py-2"
                />
              </div>
            </div>
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={closeApprove}
                className="rounded border border-gray-300 px-4 py-2 text-sm"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={savingApprove}
                className="rounded bg-green-600 px-4 py-2 text-sm text-white disabled:opacity-50"
              >
                {savingApprove ? 'Guardando...' : 'Dar de alta y aprobar'}
              </button>
            </div>
          </form>
        </div>
      )}

      {rejecting && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <form onSubmit={handleReject} className="w-full max-w-md rounded-lg bg-white p-6">
            <h2 className="mb-4 text-lg font-semibold">Rechazar solicitud</h2>
            <p className="mb-4 text-sm text-gray-600">
              Libro: <span className="font-medium">{rejecting.title}</span> de {rejecting.author}
            </p>
            <label htmlFor="reject-notes" className="mb-1 block text-sm font-medium">Motivo (obligatorio)</label>
            <textarea
              id="reject-notes"
              rows={3}
              required
              value={rejectNotes}
              onChange={(e) => setRejectNotes(e.target.value)}
              className="w-full rounded border border-gray-300 px-3 py-2"
            />
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={closeReject}
                className="rounded border border-gray-300 px-4 py-2 text-sm"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={savingReject}
                className="rounded bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50"
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
