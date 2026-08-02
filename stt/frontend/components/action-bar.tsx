'use client'

import { Copy, Download, Share2, FileText, FileCode, File } from 'lucide-react'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

interface ActionBarProps {
  text: string
}

export function ActionBar({ text }: ActionBarProps) {
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(text)
      toast.success('Copiado al portapapeles')
    } catch {
      toast.error('Error al copiar')
    }
  }

  const download = (format: string) => {
    let content = text
    let mime = 'text/plain'
    let ext = 'txt'

    if (format === 'markdown') {
      content = text
      mime = 'text/markdown'
      ext = 'md'
    } else if (format === 'pdf') {
      toast.info('PDF export coming soon')
      return
    }

    const blob = new Blob([content], { type: mime })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transcripcion.${ext}`
    a.click()
    URL.revokeObjectURL(url)
    toast.success(`Descargado como ${format.toUpperCase()}`)
  }

  const share = async () => {
    if (navigator.share) {
      await navigator.share({ text })
    } else {
      await copyToClipboard()
    }
  }

  const actions = [
    { icon: Copy, label: 'Copiar', onClick: copyToClipboard },
    { icon: FileText, label: 'TXT', onClick: () => download('txt') },
    { icon: FileCode, label: 'Markdown', onClick: () => download('markdown') },
    { icon: File, label: 'PDF', onClick: () => download('pdf') },
    { icon: Share2, label: 'Compartir', onClick: share },
  ]

  return (
    <div className="flex items-center gap-2 flex-wrap">
      {actions.map((action) => (
        <button
          key={action.label}
          onClick={action.onClick}
          className={cn(
            'inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium',
            'border bg-card hover:bg-secondary transition-colors',
          )}
        >
          <action.icon className="h-4 w-4" />
          {action.label}
        </button>
      ))}
    </div>
  )
}
