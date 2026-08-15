import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/auth'

export function Header() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  const canManageBooks = user != null &&
    user.permissions.includes('books.create') &&
    user.permissions.includes('books.update') &&
    user.permissions.includes('books.delete')

  const canManageBookRequests = user != null && user.permissions.includes('books.manage')

  const canViewOwnRentals = user != null && user.permissions.includes('rentals.view_own')
  const canManageRentals = user != null && user.permissions.includes('rentals.view_all')

  async function handleLogout() {
    await authService.logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="wood-panel sticky top-0 z-40 border-b border-brass/40 shadow-[0_2px_12px_rgba(51,36,26,0.28)]">
      <div className="container mx-auto flex min-h-16 flex-wrap items-center justify-between gap-x-6 gap-y-2 px-4 py-2">
        <Link
          to="/"
          className="group flex items-center gap-2.5"
          aria-label="Biblioteca Virtual — Inicio"
        >
          <span
            aria-hidden="true"
            className="flex h-9 w-9 items-center justify-center rounded-sm border border-brass/70 bg-espresso/40 shadow-inner transition-colors group-hover:border-brass"
          >
            <svg viewBox="0 0 24 24" className="size-5 text-brass" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M12 6.5C10.5 5 8 4.5 5.5 4.5c-1 0-2 .1-2.5.3v13c.5-.2 1.5-.3 2.5-.3 2.5 0 5 .5 6.5 2 1.5-1.5 4-2 6.5-2 1 0 2 .1 2.5.3v-13c-.5-.2-1.5-.3-2.5-.3-2.5 0-5 .5-6.5 2Z" />
              <path d="M12 6.5v13" />
            </svg>
          </span>
          <span className="font-heading text-xl font-semibold tracking-tight text-parchment">
            Biblioteca <span className="italic text-brass">Virtual</span>
          </span>
        </Link>

        <nav className="flex flex-wrap items-center gap-x-5 gap-y-2" aria-label="Navegación principal">
          <Link to="/" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
            Inicio
          </Link>
          <Link to="/catalog" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
            Catálogo
          </Link>
          {canManageBooks && (
            <Link to="/admin/books" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
              Gestión de libros
            </Link>
          )}
          {canViewOwnRentals && (
            <Link to="/mis-alquileres" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
              Mis alquileres
            </Link>
          )}
          {canManageRentals && (
            <Link to="/admin/rentals" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
              Gestión de alquileres
            </Link>
          )}
          {canManageBookRequests && (
            <Link to="/admin/gestion-libro" className="text-sm text-parchment/85 transition-colors hover:text-brass hover:underline hover:underline-offset-4">
              Gestión de libro
            </Link>
          )}
          {user && (
            <span className="text-sm text-tan">
              Hola, <span className="font-medium text-parchment">{user.fullName}</span>
            </span>
          )}
          {user && (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded-md border border-brass/70 px-3 py-1.5 text-sm text-parchment transition-colors hover:bg-brass/20 hover:text-brass"
            >
              Cerrar sesión
            </button>
          )}
        </nav>
      </div>
    </header>
  )
}
