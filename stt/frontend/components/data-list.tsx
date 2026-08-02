'use client'

import { Copy, ExternalLink } from 'lucide-react'
import { toast } from 'sonner'

interface DataListProps {
  items: string[]
  type?: 'phone' | 'email' | 'link' | 'date' | 'tag'
}

export function DataList({ items, type = 'date' }: DataListProps) {
  if (!items?.length) return <p className="text-sm text-muted-foreground">No se detectaron elementos.</p>

  const copy = async (value: string) => {
    await navigator.clipboard.writeText(value)
    toast.success('Copiado')
  }

  return (
    <div className="space-y-2">
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center justify-between p-2 rounded-lg bg-secondary/50 group">
          <span className="text-sm font-mono">{item}</span>
          <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => copy(item)}
              className="p-1.5 rounded-md hover:bg-secondary transition-colors"
              title="Copiar"
            >
              <Copy className="h-3.5 w-3.5" />
            </button>
            {type === 'link' && (
              <a
                href={item.startsWith('http') ? item : `https://${item}`}
                target="_blank"
                rel="noopener noreferrer"
                className="p-1.5 rounded-md hover:bg-secondary transition-colors"
                title="Abrir"
              >
                <ExternalLink className="h-3.5 w-3.5" />
              </a>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
