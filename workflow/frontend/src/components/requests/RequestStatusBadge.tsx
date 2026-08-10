import type { BookRequestStatus } from '@/types'

const LABELS: Record<BookRequestStatus, string> = {
  Pending: 'Pendiente',
  Approved: 'Aprobada',
  Rejected: 'Rechazada',
}

const STYLES: Record<BookRequestStatus, string> = {
  Pending: 'bg-yellow-100 text-yellow-800',
  Approved: 'bg-green-100 text-green-800',
  Rejected: 'bg-red-100 text-red-800',
}

export function RequestStatusBadge({ status }: { status: BookRequestStatus }) {
  return (
    <span className={`inline-block rounded-full px-3 py-1 text-xs font-medium ${STYLES[status]}`}>
      {LABELS[status]}
    </span>
  )
}
