'use client'
import { createContext, useCallback, useContext, useMemo, useState } from 'react'

type Toast = { id: string; title?: string; message: string; type?: 'info'|'success'|'error' };

const ToastCtx = createContext<{ toasts: Toast[]; push: (t: Omit<Toast,'id'>) => void; dismiss: (id: string)=>void } | null>(null)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const push = useCallback((t: Omit<Toast,'id'>) => {
    const id = Math.random().toString(36).slice(2)
    const toast: Toast = { id, ...t }
    setToasts((arr) => [...arr, toast])
    setTimeout(() => setToasts((arr) => arr.filter((x) => x.id !== id)), 4000)
  }, [])
  const dismiss = useCallback((id: string) => setToasts((arr) => arr.filter((x) => x.id !== id)), [])
  const value = useMemo(() => ({ toasts, push, dismiss }), [toasts, push, dismiss])
  return (
    <ToastCtx.Provider value={value}>
      {children}
      <div className="fixed z-50 right-4 bottom-4 space-y-2">
        {toasts.map((t) => (
          <div key={t.id} className={`rounded-md border px-4 py-3 min-w-[260px] shadow-lg ${
            t.type === 'error' ? 'bg-rose-500/15 border-rose-500/40 text-rose-100' :
            t.type === 'success' ? 'bg-emerald-500/15 border-emerald-500/40 text-emerald-100' :
            'bg-slate-800/90 border-slate-700 text-slate-100'
          }`}>
            {t.title && <div className="text-sm font-semibold mb-0.5">{t.title}</div>}
            <div className="text-sm">{t.message}</div>
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastCtx)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}
