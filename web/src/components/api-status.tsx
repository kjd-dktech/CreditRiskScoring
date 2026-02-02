'use client'
import { useEffect, useState } from 'react'

function fetchWithTimeout(url: string, ms = 3000) {
  const controller = new AbortController()
  const id = setTimeout(() => controller.abort(), ms)
  return fetch(url, { signal: controller.signal }).finally(() => clearTimeout(id))
}

export function ApiStatus() {
  const [status, setStatus] = useState<'loading'|'online'|'offline'>('loading')

  useEffect(() => {
    let cancelled = false
    const ping = async () => {
      try {
        const r = await fetchWithTimeout('/api/health', 3000)
        if (!r.ok) throw new Error('bad status')
        const j = await r.json()
        if (!cancelled) setStatus(j?.status === 'healthy' ? 'online' : 'offline')
      } catch {
        if (!cancelled) setStatus('offline')
      }
    }
    ping()
    const iv = setInterval(ping, 15000)
    return () => {
      cancelled = true
      clearInterval(iv)
    }
  }, [])

  const color = status === 'online' ? 'bg-emerald-500' : status === 'offline' ? 'bg-rose-500' : 'bg-amber-400'
  const label = status === 'online' ? 'API online' : status === 'offline' ? 'API offline' : 'API…'

  return (
    <div className="inline-flex items-center gap-2 text-xs text-slate-300">
      <span className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} />
      <span>{label}</span>
    </div>
  )
}
