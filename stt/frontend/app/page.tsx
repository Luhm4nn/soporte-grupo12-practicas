'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/navbar'
import { DropZone } from '@/components/drop-zone'
import { UploadProgress } from '@/components/upload-progress'
import { useUpload } from '@/hooks/use-upload'
import { motion } from 'framer-motion'

export default function Home() {
  const router = useRouter()
  const { upload, uploading, progress, audioId, error, reset } = useUpload()
  const [currentFile, setCurrentFile] = useState<File | null>(null)

  const handleUpload = async (file: File) => {
    setCurrentFile(file)
    const id = await upload(file)
    if (id) {
      router.push(`/audio/${id}`)
    }
  }

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className="flex-1 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full"
        >
          <div className="text-center mb-8 space-y-2">
            <h1 className="text-3xl font-bold tracking-tight">
              AudioCopilot
            </h1>
            <p className="text-muted-foreground">
              Transcripción inteligente con IA
            </p>
          </div>

          {uploading && currentFile ? (
            <UploadProgress
              fileName={currentFile.name}
              fileSize={currentFile.size}
              progress={progress}
            />
          ) : (
            <DropZone onUpload={handleUpload} disabled={uploading} />
          )}

          {error && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-sm text-destructive text-center mt-4"
            >
              {error}
            </motion.p>
          )}
        </motion.div>
      </main>
    </div>
  )
}
