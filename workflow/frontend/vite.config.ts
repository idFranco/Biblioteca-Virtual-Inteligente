import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

const requiredEnvVars = ['VITE_API_BASE_URL', 'VITE_CHATBOT_API_BASE_URL']

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const missing = requiredEnvVars.filter((name) => !env[name])
  if (missing.length > 0) {
    throw new Error(
      `Faltan variables de entorno requeridas para compilar el frontend: ${missing.join(', ')}. ` +
        'Defínelas en el .env o en el entorno antes de ejecutar vite build/dev.',
    )
  }

  return {
    plugins: [react(), tailwindcss()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
  }
})
