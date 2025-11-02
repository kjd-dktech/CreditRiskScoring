import './globals.css'
import type { Metadata } from 'next'
import { ThemeToggle } from '@/components/theme-toggle'
import { ToastProvider } from '@/components/ui/toast'
import { ApiStatus } from '@/components/api-status'

export const metadata: Metadata = {
  title: 'Credit Risk Scoring Demo',
  description: 'Predict credit risk',
  icons: { icon: 'favicon.png' }
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <header className="sticky top-0 z-10 backdrop-blur supports-[backdrop-filter]:bg-slate-900/60 bg-slate-900/80 border-b border-slate-800">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
            <div className="flex items-center gap-6">
              <a href="/" className="text-slate-200 font-semibold">Scoring de Crédit</a>
              <a href="/about" className="text-slate-300 hover:text-slate-100 text-sm">À propos</a>
            </div>
            <div className="flex items-center gap-4">
              <ApiStatus />
              <ThemeToggle />
            </div>
          </div>
        </header>
        <ToastProvider>
          <main className="max-w-5xl mx-auto px-4 py-10 flex-1">{children}</main>
        </ToastProvider>
        <footer className="w-full border-t border-slate-800 bg-slate-900/80 py-4 mt-8">
          <div className="max-w-5xl mx-auto px-4 text-center text-slate-400 text-sm">
            Réalisé par Kodjo Jean DEGBEVI — DKTech Innovations
          </div>
        </footer>
      </body>
    </html>
  )
}
