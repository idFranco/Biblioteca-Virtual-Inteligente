import { useState, type FormEvent } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { authService } from '@/services/auth'

export function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname ?? '/'

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await authService.login(email, password)
      navigate(from, { replace: true })
    } catch {
      setError('Credenciales inválidas. Verifica tu correo y contraseña.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto max-w-md px-4 py-16">
      <div className="texture-grain rounded-lg border border-tan/80 bg-card p-8 shadow-sm dark:border-wood">
        <h1 className="mb-1 font-heading text-3xl font-semibold text-espresso dark:text-parchment">Iniciar sesión</h1>
        <div aria-hidden="true" className="ornament-rule mt-3 mb-6">
          <span className="ornament-diamond" />
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Correo electrónico</label>
            <input
              id="email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Contraseña</label>
            <input
              id="password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
          {error && <p className="text-sm text-oxide">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-wine px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
          >
            {loading ? 'Ingresando...' : 'Ingresar'}
          </button>
        </form>
        <p className="mt-4 text-sm text-sepia dark:text-tan">
          ¿No tienes cuenta? <Link to="/register" className="font-medium text-brass underline underline-offset-4 hover:text-ochre">Regístrate</Link>
        </p>
      </div>
    </div>
  )
}