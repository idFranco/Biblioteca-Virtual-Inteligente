import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

export type StatusVariant =
  | 'available'
  | 'unavailable'
  | 'active'
  | 'returned'
  | 'overdue'
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'neutral'

const VARIANT_CLASSES: Record<StatusVariant, string> = {
  available:
    'bg-olive/15 text-olive ring-olive/25 dark:bg-olive/20 dark:text-[color-mix(in_oklch,var(--olive),var(--paper)_42%)] dark:ring-olive/40',
  unavailable:
    'bg-oxide/15 text-oxide ring-oxide/25 dark:bg-oxide/20 dark:text-[color-mix(in_oklch,var(--oxide),var(--paper)_36%)] dark:ring-oxide/40',
  active:
    'bg-ochre/15 text-ochre ring-ochre/25 dark:bg-ochre/20 dark:text-[color-mix(in_oklch,var(--ochre),var(--paper)_30%)] dark:ring-ochre/40',
  returned:
    'bg-olive/15 text-olive ring-olive/25 dark:bg-olive/20 dark:text-[color-mix(in_oklch,var(--olive),var(--paper)_42%)] dark:ring-olive/40',
  overdue:
    'bg-oxide/15 text-oxide ring-oxide/25 dark:bg-oxide/20 dark:text-[color-mix(in_oklch,var(--oxide),var(--paper)_36%)] dark:ring-oxide/40',
  pending:
    'bg-ochre/15 text-ochre ring-ochre/25 dark:bg-ochre/20 dark:text-[color-mix(in_oklch,var(--ochre),var(--paper)_30%)] dark:ring-ochre/40',
  approved:
    'bg-olive/15 text-olive ring-olive/25 dark:bg-olive/20 dark:text-[color-mix(in_oklch,var(--olive),var(--paper)_42%)] dark:ring-olive/40',
  rejected:
    'bg-oxide/15 text-oxide ring-oxide/25 dark:bg-oxide/20 dark:text-[color-mix(in_oklch,var(--oxide),var(--paper)_36%)] dark:ring-oxide/40',
  neutral:
    'bg-tan/25 text-sepia ring-tan/40 dark:bg-tan/15 dark:text-tan dark:ring-tan/30',
}

interface StatusBadgeProps {
  variant: StatusVariant
  children: ReactNode
  className?: string
}

export function StatusBadge({ variant, children, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset',
        VARIANT_CLASSES[variant],
        className,
      )}
    >
      <span aria-hidden="true" className="size-1.5 rounded-full bg-current opacity-80" />
      {children}
    </span>
  )
}
