import { cn } from '@/lib/utils'

interface PageHeaderProps {
  title: string
  subtitle?: string
  className?: string
}

/**
 * Encabezado de página con tipografía serif (Fraunces), regla ornamental de
 * latón con rombo y aparición escalonada.
 */
export function PageHeader({ title, subtitle, className }: PageHeaderProps) {
  return (
    <header className={cn('mb-8 max-w-2xl', className)}>
      <h1 className="reveal font-heading text-3xl font-semibold tracking-tight text-espresso sm:text-4xl dark:text-parchment">
        {title}
      </h1>
      <div aria-hidden="true" className="ornament-rule reveal reveal-delay-1 mt-4">
        <span className="ornament-diamond" />
      </div>
      {subtitle && (
        <p className="reveal reveal-delay-2 mt-3 text-sm leading-relaxed text-sepia dark:text-tan">
          {subtitle}
        </p>
      )}
    </header>
  )
}
