'use client'

import { useCallback, useRef, useState } from 'react'
import { Upload, FileAudio, Mic, X } from 'lucide-react'
import { cn, formatFileSize } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'

const ACCEPTED_TYPES = [
  'audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg',
  'audio/ogg; codecs=opus', 'audio/aac', 'audio/webm',
  'audio/x-m4a', 'audio/x-wav',
]

const ACCEPTED_EXTENSIONS = '.mp3,.wav,.m4a,.ogg,.opus,.aac,.webm'

interface DropZoneProps {
  onUpload: (file: File) => void
  disabled?: boolean
}

export function DropZone({ onUpload, disabled }: DropZoneProps) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    const f = e.dataTransfer.files[0]
    if (f) {
      setFile(f)
      onUpload(f)
    }
  }, [onUpload])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(true)
  }, [])

  const handleDragLeave = useCallback(() => {
    setIsDragging(false)
  }, [])

  const handleClick = () => {
    if (!disabled) inputRef.current?.click()
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setFile(f)
      onUpload(f)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center w-full max-w-xl mx-auto">
      <AnimatePresence>
        {!file && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="w-full"
          >
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onClick={handleClick}
              className={cn(
                'relative flex flex-col items-center justify-center gap-4 p-16 rounded-2xl border-2 border-dashed transition-all duration-200 cursor-pointer',
                isDragging
                  ? 'border-primary bg-primary/5 scale-[1.02]'
                  : 'border-muted-foreground/25 hover:border-muted-foreground/50 hover:bg-muted/50',
                disabled && 'opacity-50 pointer-events-none',
              )}
            >
              <div className="p-4 rounded-full bg-secondary">
                <Mic className="h-10 w-10 text-muted-foreground" />
              </div>
              <div className="text-center space-y-1">
                <p className="text-lg font-medium">
                  Arrastrá un audio o hacé clic para subirlo
                </p>
                <p className="text-sm text-muted-foreground">
                  MP3, WAV, M4A, OGG, OPUS, AAC, WEBM
                </p>
              </div>
            </div>
            <input
              ref={inputRef}
              type="file"
              accept={ACCEPTED_EXTENSIONS}
              className="hidden"
              onChange={handleFileSelect}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
