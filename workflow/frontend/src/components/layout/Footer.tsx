export function Footer() {
  return (
    <footer className="wood-panel mt-auto border-t border-brass/40">
      <div className="container mx-auto flex flex-col items-center gap-3 px-4 py-8 text-center">
        <span aria-hidden="true" className="flex items-center gap-3 text-brass">
          <span className="block h-px w-10 bg-gradient-to-r from-transparent to-brass/70" />
          <span className="block size-1.5 rotate-45 bg-brass" />
          <span className="block h-px w-10 bg-gradient-to-l from-transparent to-brass/70" />
        </span>
        <p className="font-heading text-sm italic text-parchment/90">
          Biblioteca Virtual Inteligente
        </p>
        <p className="text-xs text-tan/80">
          &copy; {new Date().getFullYear()} Biblioteca Virtual Inteligente
        </p>
      </div>
    </footer>
  )
}
