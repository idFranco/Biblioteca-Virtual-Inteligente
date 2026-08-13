import { cn } from '@/lib/utils'

interface PaginationProps {
  page: number
  totalPages: number
  onChange: (page: number) => void
  className?: string
}

export function Pagination({ page, totalPages, onChange, className }: PaginationProps) {
  if (totalPages <= 1) return null

  return (
    <nav aria-label="Paginación" className={cn('mt-8 flex items-center justify-center gap-4', className)}>
      <button
        type="button"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
        className="rounded-md border border-brass/50 bg-paper px-4 py-1.5 text-sm font-medium text-espresso shadow-sm transition-colors hover:border-brass hover:bg-brass/15 disabled:pointer-events-none disabled:opacity-40 dark:bg-wood-dark dark:text-parchment dark:hover:border-brass dark:hover:bg-brass/15"
      >
        Anterior
      </button>
      <span className="text-sm text-sepia dark:text-tan">
        Página <span className="font-semibold text-espresso dark:text-parchment">{page}</span> de {totalPages}
      </span>
      <button
        type="button"
        disabled={page >= totalPages}
        onClick={() => onChange(page + 1)}
        className="rounded-md border border-brass/50 bg-paper px-4 py-1.5 text-sm font-medium text-espresso shadow-sm transition-colors hover:border-brass hover:bg-brass/15 disabled:pointer-events-none disabled:opacity-40 dark:bg-wood-dark dark:text-parchment dark:hover:border-brass dark:hover:bg-brass/15"
      >
        Siguiente
      </button>
    </nav>
  )
}
