import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { authService } from '@/services/auth'

export function Header() {
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  async function handleLogout() {
    await authService.logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <h1 className="text-xl font-bold">Biblioteca Virtual</h1>
        <nav className="flex items-center gap-4">
          <Link to="/" className="text-sm text-muted-foreground hover:underline">Inicio</Link>
          <Link to="/catalog" className="text-sm text-muted-foreground hover:underline">Catálogo</Link>
          {user && (
            <span className="text-sm">
              Hola, <span className="font-medium">{user.fullName}</span>
            </span>
          )}
          {user && (
            <button
              type="button"
              onClick={handleLogout}
              className="rounded border border-gray-300 px-3 py-1 text-sm hover:bg-gray-100"
            >
              Cerrar sesión
            </button>
          )}
        </nav>
      </div>
    </header>
  )
}