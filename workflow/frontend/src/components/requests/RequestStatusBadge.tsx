import type { BookRequestStatus } from '@/types'
import { StatusBadge } from '@/components/ui/StatusBadge'

const LABELS: Record<BookRequestStatus, string> = {
  Pending: 'Pendiente',
  Approved: 'Aprobada',
  Rejected: 'Rechazada',
}

const VARIANTS: Record<BookRequestStatus, 'pending' | 'approved' | 'rejected'> = {
  Pending: 'pending',
  Approved: 'approved',
  Rejected: 'rejected',
}

export function RequestStatusBadge({ status }: { status: BookRequestStatus }) {
  return <StatusBadge variant={VARIANTS[status]}>{LABELS[status]}</StatusBadge>
}