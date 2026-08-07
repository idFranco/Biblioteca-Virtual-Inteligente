import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from './ProtectedRoute'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'

export const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout />
      </ProtectedRoute>
    ),
    children: [
      {
        path: 'catalog',
        element: (
          <div className="container mx-auto px-4 py-8">
            <h1 className="text-2xl font-bold">Catálogo de libros</h1>
          </div>
        ),
      },
      {
        index: true,
        element: (
          <div className="container mx-auto px-4 py-8">
            <h1 className="text-3xl font-bold">Bienvenido a la Biblioteca Virtual</h1>
          </div>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])