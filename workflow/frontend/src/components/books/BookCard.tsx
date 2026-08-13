import { useState, type ReactNode } from 'react'
import type { Book } from '@/types'
import { cn } from '@/lib/utils'
import { getCoverUrl } from '@/lib/covers'
import { CoverOrnament } from './CoverOrnament'
import { StatusBadge } from '@/components/ui/StatusBadge'

interface BookCardProps {
  book: Book
  className?: string
  /** Área de acción opcional (p. ej. botón "Alquilar") */
  action?: ReactNode
}

export function BookCard({ book, className, action }: BookCardProps) {
  const [coverFailed, setCoverFailed] = useState(false)
  const coverUrl = getCoverUrl(book, 'M')
  const showFallback = coverUrl === null || coverFailed

  return (
    <article
      className={cn(
        'texture-grain group relative flex gap-4 rounded-lg border border-tan/80 bg-card p-4 shadow-[0_1px_3px_rgba(51,36,26,0.14),0_6px_16px_-8px_rgba(51,36,26,0.22)] transition-all duration-300 hover:-translate-y-0.5 hover:border-brass/60 hover:shadow-[0_4px_10px_rgba(51,36,26,0.16),0_14px_28px_-10px_rgba(51,36,26,0.3)] dark:border-wood',
        className,
      )}
    >
      <div className="relative h-40 w-28 shrink-0 overflow-hidden rounded-r-sm rounded-l-xs border border-wood/40 shadow-md">
        {showFallback ? (
          <CoverOrnament title={book.title} author={book.author} />
        ) : (
          <img
            src={coverUrl}
            alt={`Portada de ${book.title}`}
            referrerPolicy="no-referrer"
            loading="lazy"
            onError={() => setCoverFailed(true)}
            className="h-full w-full object-cover"
          />
        )}
      </div>

      <div className="flex min-w-0 flex-1 flex-col">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <h3 className="font-heading text-lg font-semibold leading-snug text-espresso dark:text-parchment">
            {book.title}
          </h3>
          <StatusBadge variant={book.isAvailable ? 'available' : 'unavailable'}>
            {book.isAvailable ? 'Disponible' : 'No disponible'}
          </StatusBadge>
        </div>

        <p className="mt-1 text-sm text-sepia dark:text-tan">{book.author}</p>

        {book.genre && (
          <p className="mt-1.5 text-xs italic text-wood dark:text-brass">{book.genre}</p>
        )}

        <div className="mt-auto flex items-end justify-between gap-3 pt-3">
          <p className="text-xs text-sepia dark:text-tan/90">
            {book.availableCopies} / {book.totalCopies} copias disponibles
          </p>
          {action && <div className="shrink-0">{action}</div>}
        </div>
      </div>
    </article>
  )
}
