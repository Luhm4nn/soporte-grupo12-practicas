'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Navbar } from '@/components/navbar'
import { AudioRecorder } from '@/components/audio-recorder'
import { DropZone } from '@/components/drop-zone'
import { UploadProgress } from '@/components/upload-progress'
import { useUpload } from '@/hooks/use-upload'
import { motion, AnimatePresence } from 'framer-motion'
import { Upload } from 'lucide-react'

export default function Home() {
  const router = useRouter()
  const { upload, uploading, progress, audioId, error, reset } = useUpload()
  const [currentFile, setCurrentFile] = useState<File | null>(null)
  const [showUpload, setShowUpload] = useState(false)

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
            <>
              <AudioRecorder onRecord={handleUpload} disabled={uploading} />

              <div className="mt-6 text-center">
                {showUpload ? (
                  <AnimatePresence mode="wait">
                    <motion.div
                      key="upload"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <DropZone onUpload={handleUpload} disabled={uploading} />
                      <button
                        onClick={() => setShowUpload(false)}
                        className="mt-4 text-sm text-muted-foreground hover:underline"
                      >
                        Volver a grabar
                      </button>
                    </motion.div>
                  </AnimatePresence>
                ) : (
                  <button
                    onClick={() => setShowUpload(true)}
                    className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <Upload className="h-4 w-4" />
                    o subí un archivo de audio
                  </button>
                )}
              </div>
            </>
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
