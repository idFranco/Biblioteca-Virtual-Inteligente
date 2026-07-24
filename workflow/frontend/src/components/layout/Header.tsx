export function Header() {
  return (
    <header className="border-b">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <h1 className="text-xl font-bold">Biblioteca Virtual</h1>
        <nav className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">Inicio</span>
        </nav>
      </div>
    </header>
  )
}
