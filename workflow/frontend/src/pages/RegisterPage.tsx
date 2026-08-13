import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '@/services/auth'

export function RegisterPage() {
  const navigate = useNavigate()
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    setLoading(true)
    try {
      await authService.register(fullName, email, password)
      navigate('/', { replace: true })
    } catch {
      setError('No se pudo crear la cuenta. Verifica los datos e inténtalo de nuevo.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container mx-auto max-w-md px-4 py-16">
      <div className="texture-grain rounded-lg border border-tan/80 bg-card p-8 shadow-sm dark:border-wood">
        <h1 className="mb-1 font-heading text-3xl font-semibold text-espresso dark:text-parchment">Crear cuenta</h1>
        <div aria-hidden="true" className="ornament-rule mt-3 mb-6">
          <span className="ornament-diamond" />
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="fullName" className="mb-1 block text-sm font-medium text-espresso dark:text-parchment">Nombre completo</label>
            <input
              id="fullName"
              type="text"
              required
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
          </div>
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
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded border border-input bg-background px-3 py-2 text-sm text-espresso focus:border-brass focus:outline-none focus:ring-2 focus:ring-brass/40 dark:text-parchment"
            />
            <p className="mt-1 text-xs text-sepia dark:text-tan">
              Mínimo 8 caracteres: al menos una mayúscula, un número y un carácter especial o minúscula.
            </p>
          </div>
          {error && <p className="text-sm text-oxide">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-wine px-4 py-2 text-sm font-medium text-paper transition-colors hover:bg-oxide disabled:opacity-50 dark:bg-primary dark:text-primary-foreground dark:hover:brightness-110"
          >
            {loading ? 'Creando cuenta...' : 'Registrarse'}
          </button>
        </form>
        <p className="mt-4 text-sm text-sepia dark:text-tan">
          ¿Ya tienes cuenta? <Link to="/login" className="font-medium text-brass underline underline-offset-4 hover:text-ochre">Inicia sesión</Link>
        </p>
      </div>
    </div>
  )
}