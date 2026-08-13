import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface Spine {
  title: string
  color: string
  height: string
}

const SHELF: Spine[] = [
  { title: 'Cien años de soledad', color: 'from-wine via-oxide to-wood-dark', height: 'h-36' },
  { title: 'Don Quijote', color: 'from-olive via-wood to-wood-dark', height: 'h-40' },
  { title: 'Rayuela', color: 'from-brass via-ochre to-wood', height: 'h-32' },
  { title: 'Ficciones', color: 'from-wood-dark via-wood to-wood-dark', height: 'h-38' },
  { title: 'La Odisea', color: 'from-oxide via-wine to-wood-dark', height: 'h-34' },
  { title: 'Orgullo y prejuicio', color: 'from-ochre via-brass to-wood', height: 'h-36' },
]

function BookSpine({ spine }: { spine: Spine }) {
  return (
    <div
      className={`${spine.height} relative w-9 shrink-0 overflow-hidden rounded-t-sm rounded-b-none border border-espresso/40 bg-gradient-to-b ${spine.color} shadow-md`}
      aria-hidden="true"
    >
      <span className="absolute inset-x-0 top-0 h-1.5 bg-brass/70" />
      <span
        className="absolute inset-0 flex items-center justify-center py-3 font-heading text-[0.55rem] font-medium uppercase tracking-[0.18em] text-parchment/85 [writing-mode:vertical-rl]"
      >
        {spine.title}
      </span>
      <span className="absolute inset-x-0 bottom-0 h-1 bg-brass/70" />
    </div>
  )
}

export function HomePage() {
  const user = useAuthStore((state) => state.user)
  const canViewOwnRentals = user != null && user.permissions.includes('rentals.view_own')

  return (
    <div className="container mx-auto px-4 py-12 sm:py-16">
      <div className="grid items-center gap-12 lg:grid-cols-[1.15fr_1fr]">
        <div>
          <p className="reveal inline-flex items-center gap-2 rounded-full border border-brass/40 bg-paper px-3 py-1 text-xs font-medium uppercase tracking-[0.16em] text-brass dark:bg-wood-dark">
            <span aria-hidden="true" className="size-1 rotate-45 bg-brass" />
            Sala de lectura
          </p>

          <h1 className="reveal reveal-delay-1 mt-5 font-heading text-4xl font-semibold leading-[1.08] tracking-tight text-espresso sm:text-5xl dark:text-parchment">
            Bienvenido a la
            <span className="mt-1 block italic text-wine dark:text-brass">Biblioteca Virtual</span>
          </h1>

          <div aria-hidden="true" className="ornament-rule reveal reveal-delay-2 mt-6 max-w-sm">
            <span className="ornament-diamond" />
          </div>

          <p className="reveal reveal-delay-2 mt-5 max-w-xl text-base leading-relaxed text-sepia dark:text-tan">
            Un espacio cálido de estanterías digitales donde descubrir, reservar y
            disfrutar del catálogo: clásicos, novela, ciencia ficción y mucho más,
            con la ayuda de nuestro asistente bibliotecario.
          </p>

          <div className="reveal reveal-delay-3 mt-8 flex flex-wrap items-center gap-4">
            <Link
              to="/catalog"
              className="inline-flex items-center gap-2 rounded-md bg-wine px-5 py-2.5 text-sm font-medium text-paper shadow-[0_4px_12px_-4px_rgba(123,45,43,0.55)] transition-colors hover:bg-oxide dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
            >
              Explorar el catálogo
            </Link>
            {canViewOwnRentals && (
              <Link
                to="/mis-alquileres"
                className="inline-flex items-center gap-2 rounded-md border border-brass/60 bg-paper px-5 py-2.5 text-sm font-medium text-espresso transition-colors hover:bg-brass/15 dark:bg-wood-dark dark:text-parchment"
              >
                Mis alquileres
              </Link>
            )}
          </div>
        </div>

        <div className="reveal reveal-delay-3 relative lg:justify-self-end">
          <div className="texture-grain relative rounded-lg border border-tan/80 bg-gradient-to-b from-parchment to-paper p-6 shadow-[0_10px_30px_-12px_rgba(51,36,26,0.4)] sm:p-8 dark:border-wood dark:from-wood-dark dark:to-espresso">
            <div className="flex items-end gap-2 pl-2">
              {SHELF.map((spine) => (
                <BookSpine key={spine.title} spine={spine} />
              ))}
            </div>
            {/* Repisa de madera */}
            <div
              aria-hidden="true"
              className="mt-0 h-2.5 rounded-b-sm bg-gradient-to-b from-wood to-wood-dark shadow-[0_3px_4px_rgba(51,36,26,0.35)]"
            />
            <div className="mt-5 flex items-center justify-between">
              <p className="font-heading text-sm italic text-sepia dark:text-tan">
                «Un hogar para cada libro, un libro para cada lector»
              </p>
              <span aria-hidden="true" className="flex gap-1">
                <span className="size-1.5 rounded-full bg-brass" />
                <span className="size-1.5 rounded-full bg-ochre" />
                <span className="size-1.5 rounded-full bg-olive" />
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
