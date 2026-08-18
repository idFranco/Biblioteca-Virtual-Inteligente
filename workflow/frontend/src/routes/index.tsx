import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from './ProtectedRoute'
import { PermissionGuard } from './PermissionGuard'
import { LoginPage } from '@/pages/LoginPage'
import { RegisterPage } from '@/pages/RegisterPage'
import { CatalogPage } from '@/pages/CatalogPage'
import { BooksAdminPage } from '@/pages/BooksAdminPage'
import { MisAlquileresPage } from '@/pages/MisAlquileresPage'
import { AlquileresAdminPage } from '@/pages/AlquileresAdminPage'
import { GestionLibroPage } from '@/pages/GestionLibroPage'
import { HomePage } from '@/pages/HomePage'
import { SalaLecturaPage } from '@/pages/SalaLecturaPage'

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
        element: <CatalogPage />,
      },
      {
        path: 'admin/books',
        element: (
          <PermissionGuard permissions={['books.create', 'books.update', 'books.delete']}>
            <BooksAdminPage />
          </PermissionGuard>
        ),
      },
      {
        path: 'mis-alquileres',
        element: (
          <PermissionGuard permissions={['rentals.view_own']}>
            <MisAlquileresPage />
          </PermissionGuard>
        ),
      },
      {
        path: 'admin/rentals',
        element: (
          <PermissionGuard permissions={['rentals.view_all']}>
            <AlquileresAdminPage />
          </PermissionGuard>
        ),
      },
      {
        path: 'admin/gestion-libro',
        element: (
          <PermissionGuard permissions={['books.manage']}>
            <GestionLibroPage />
          </PermissionGuard>
        ),
      },
      {
        path: 'sala-lectura/:bookId',
        element: (
          <PermissionGuard permissions={['rentals.view_own', 'books.read']}>
            <SalaLecturaPage />
          </PermissionGuard>
        ),
      },
      {
        index: true,
        element: <HomePage />,
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
])