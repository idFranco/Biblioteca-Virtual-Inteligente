import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface PermissionGuardProps {
  permissions: string[]
  children: React.ReactNode
}

export function PermissionGuard({ permissions, children }: PermissionGuardProps) {
  const user = useAuthStore((state) => state.user)

  const hasAll = permissions.length === 0 ||
    (user != null && permissions.every((p) => user.permissions.includes(p)))

  if (!hasAll) {
    return <Navigate to="/" replace />
  }

  return children
}