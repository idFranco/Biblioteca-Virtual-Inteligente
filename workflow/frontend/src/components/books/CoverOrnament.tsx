import { cn } from '@/lib/utils'

interface CoverOrnamentProps {
  title: string
  author?: string
  className?: string
}

/**
 * Portada decorativa de respaldo: gradiente cálido (vino → madera), lomo de
 * latón, inicial serif y un pequeño ex libris. Se muestra cuando el libro no
 * tiene ISBN/OLID o cuando la portada remota no carga.
 */
export function CoverOrnament({ title, author, className }: CoverOrnamentProps) {
  const initial = (title.trim().charAt(0) || '?').toUpperCase()

  return (
    <div
      role="img"
      aria-label={`Portada decorativa de ${title}`}
      className={cn(
        'texture-grain relative flex h-full w-full flex-col justify-between overflow-hidden rounded-r-sm rounded-l-xs bg-gradient-to-br from-wine via-oxide to-wood-dark p-3 shadow-inner',
        className,
      )}
    >
      {/* Lomo del libro */}
      <span
        aria-hidden="true"
        className="absolute inset-y-0 left-0 w-1.5 bg-gradient-to-b from-brass via-ochre to-wood"
      />
      <span
        aria-hidden="true"
        className="absolute inset-y-0 left-1.5 w-px bg-paper/25"
      />
      {/* Viñeta superior */}
      <span
        aria-hidden="true"
        className="ml-4 mt-1 inline-flex h-3 w-6 items-center justify-center self-start rounded-sm border border-brass/80"
      >
        <span className="block size-1 rotate-45 bg-brass" />
      </span>

      {/* Inicial serif */}
      <span
        aria-hidden="true"
        className="ml-4 self-center font-heading text-6xl font-semibold leading-none text-parchment/90 drop-shadow-[0_2px_2px_rgba(0,0,0,0.35)]"
      >
        {initial}
      </span>

      {/* Ex libris inferior */}
      <span aria-hidden="true" className="ml-4 mb-1 flex flex-col gap-1 self-start">
        <span className="block h-px w-8 bg-gradient-to-r from-brass to-transparent" />
        <span className="block h-1.5 w-1.5 rotate-45 border border-brass/90" />
        {author && (
          <span className="font-heading text-[0.6rem] font-medium italic tracking-wide text-parchment/70">
            {author}
          </span>
        )}
      </span>
    </div>
  )
}
