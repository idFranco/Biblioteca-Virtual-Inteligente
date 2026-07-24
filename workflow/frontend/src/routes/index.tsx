import { createBrowserRouter } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: <div className="container mx-auto px-4 py-8"><h1 className="text-3xl font-bold">Bienvenido a la Biblioteca Virtual</h1></div>,
      },
    ],
  },
])
