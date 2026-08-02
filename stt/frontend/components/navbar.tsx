'use client'

import { ThemeToggle } from './theme-toggle'
import { Mic } from 'lucide-react'

export function Navbar() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/80 backdrop-blur-sm">
      <div className="flex h-14 items-center justify-between px-6 max-w-7xl mx-auto">
        <a href="/" className="flex items-center gap-2 font-semibold text-lg">
          <Mic className="h-5 w-5" />
          AudioCopilot
        </a>
        <ThemeToggle />
      </div>
    </header>
  )
}
