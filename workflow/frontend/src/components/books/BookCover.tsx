import { useState, type SyntheticEvent } from 'react'
import { cn } from '@/lib/utils'
import { getCoverUrl, type CoverSize } from '@/lib/covers'
import { CoverOrnament } from './CoverOrnament'

/**
 * Umbral mínimo de dimensiones naturales para considerar una portada real.
 * covers.openlibrary.org devuelve una imagen placeholder en blanco (no un
 * error HTTP) cuando no existe portada, por lo que el `onError` no se dispara;
 * se detecta aquí por tamaño para caer al ornamento en lugar de quedar en blanco.
 */
const BLANK_IMAGE_THRESHOLD = 30

interface BookCoverProps {
  title: string
  author?: string | null
  isbn?: string | null
  openLibraryKey?: string | null
  size?: CoverSize
  className?: string
}

export function BookCover({ title, author, isbn, openLibraryKey, size = 'M', className }: BookCoverProps) {
  const [state, setState] = useState<'loading' | 'loaded' | 'failed'>('loading')
  const coverUrl = getCoverUrl(
    { isbn: isbn ?? null, openLibraryKey: openLibraryKey ?? null },
    size,
  )

  function handleError() {
    setState('failed')
  }

  function handleLoad(event: SyntheticEvent<HTMLImageElement>) {
    const image = event.currentTarget
    if (image.naturalWidth < BLANK_IMAGE_THRESHOLD || image.naturalHeight < BLANK_IMAGE_THRESHOLD) {
      setState('failed')
      return
    }
    setState('loaded')
  }

  return (
    <div
      className={cn(
        'relative h-full w-full overflow-hidden rounded-r-sm rounded-l-xs border border-wood/40 shadow-md',
        className,
      )}
    >
      {coverUrl === null || state === 'failed' ? (
        <CoverOrnament title={title} author={author ?? undefined} />
      ) : (
        <>
          {state === 'loading' && (
            <div
              aria-hidden="true"
              className="absolute inset-0 animate-pulse bg-parchment/60 dark:bg-wood-dark"
            />
          )}
          <img
            src={coverUrl}
            alt={`Portada de ${title}`}
            referrerPolicy="no-referrer"
            loading="lazy"
            onError={handleError}
            onLoad={handleLoad}
            className="h-full w-full object-cover"
          />
        </>
      )}
    </div>
  )
}