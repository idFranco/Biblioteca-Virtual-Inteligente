function requireEnv(name: string, value: string | undefined): string {
  if (!value) {
    throw new Error(`Falta la variable de entorno '${name}' requerida para compilar el frontend.`)
  }
  return value
}

export const API_BASE_URL: string = requireEnv('VITE_API_BASE_URL', import.meta.env.VITE_API_BASE_URL)

export const CHATBOT_API_BASE_URL: string = requireEnv(
  'VITE_CHATBOT_API_BASE_URL',
  import.meta.env.VITE_CHATBOT_API_BASE_URL,
)
