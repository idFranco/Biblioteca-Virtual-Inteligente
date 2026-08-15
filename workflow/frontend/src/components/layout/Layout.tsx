import { Outlet, useLocation } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'
import { ChatWidget } from '@/components/chat/ChatWidget'

export function Layout() {
  const location = useLocation()

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      {/* key por ruta: reinicia la transición suave en cada navegación */}
      <main key={location.pathname} className="page-fade flex-1">
        <Outlet />
      </main>
      <Footer />
      <ChatWidget />
    </div>
  )
}
