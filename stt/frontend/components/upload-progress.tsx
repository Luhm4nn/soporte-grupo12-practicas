'use client'

import { motion } from 'framer-motion'
import { Loader2, FileAudio } from 'lucide-react'
import { formatFileSize } from '@/lib/utils'

interface UploadProgressProps {
  fileName: string
  fileSize: number
  progress: number
}

export function UploadProgress({ fileName, fileSize, progress }: UploadProgressProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-xl mx-auto p-6 rounded-xl border bg-card"
    >
      <div className="flex items-center gap-3 mb-4">
        <div className="p-2 rounded-lg bg-primary/10">
          <FileAudio className="h-5 w-5 text-primary" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="font-medium text-sm truncate">{fileName}</p>
          <p className="text-xs text-muted-foreground">{formatFileSize(fileSize)}</p>
        </div>
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
      <div className="h-2 rounded-full bg-secondary overflow-hidden">
        <motion.div
          className="h-full rounded-full bg-primary"
          initial={{ width: 0 }}
          animate={{ width: `${progress}%` }}
          transition={{ duration: 0.5 }}
        />
      </div>
      <p className="text-xs text-muted-foreground mt-2 text-right">{progress}%</p>
    </motion.div>
  )
}
