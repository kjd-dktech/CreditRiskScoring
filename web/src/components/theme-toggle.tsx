'use client'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

type ThemeKey = 'A' | 'B' | 'C'

function applyTheme(theme: ThemeKey) {
  document.body.classList.remove('theme-b', 'theme-c')
  if (theme === 'B') document.body.classList.add('theme-b')
  if (theme === 'C') document.body.classList.add('theme-c')
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<ThemeKey>('A')

  useEffect(() => {
    const saved = (localStorage.getItem('theme') as ThemeKey) || 'A'
    setTheme(saved)
    applyTheme(saved)
  }, [])

  useEffect(() => {
    applyTheme(theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  const cycle = () => setTheme((t) => (t === 'A' ? 'B' : t === 'B' ? 'C' : 'A'))

  return (
    <Button onClick={cycle} variant={theme === 'A' ? 'primary' : 'secondary'}>
      Style {theme}
    </Button>
  )
}
